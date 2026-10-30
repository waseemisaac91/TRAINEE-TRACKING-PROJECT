"""
Database Service  (Task 5)  –  replaces google_drive_service.py

Everything the Trainee Tracking project used to read from Google Drive is now read
from PostgreSQL.  No gspread / Google credentials / service_account.json are needed.

Design (OOP):
    DatabaseConfig            connection settings (env vars or db_settings.json)
    Database                  opens connections, runs queries, returns dict rows
    Repository (base)         one subclass per table
        TraineeRepository, ApplicationRepository, MentorRepository,
        UserRepository, ProjectTrackingRepository
    AuthService               login check against the users table
    TraineeTrackingService    facade used by the UI

Drop-in compatibility: the module-level functions at the bottom keep the names the old
google_drive_service used (fetch_interviews, fetch_mentor, fetch_users, fetch_applications,
load_users, authenticate), so in your project you only change the import line:

    from services import google_drive_service as gds   →   import database_service as gds
"""

import os
import json
import hmac
import hashlib
import secrets
from contextlib import contextmanager
from dataclasses import dataclass

import psycopg2
from psycopg2.extras import RealDictCursor


# --------------------------------------------------------------------------
# Password helpers (stored format: pbkdf2_sha256$iterations$salt$hash)
# --------------------------------------------------------------------------
def hash_password(password, iterations=200_000):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), iterations).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password, stored):
    """Works for hashed values AND for old plain-text values."""
    parts = (stored or "").split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return hmac.compare_digest(password.encode(), (stored or "").encode())
    _, iterations, salt, digest = parts
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations)).hex()
    return hmac.compare_digest(test, digest)


# --------------------------------------------------------------------------
# Configuration + connection
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    dbname: str = "crm"
    user: str = "postgres"
    password: str = ""

    @classmethod
    def load(cls, path="db_settings.json"):
        """Priority: environment variables > db_settings.json > defaults."""
        data = {}
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            data = {"host": raw.get("host"), "port": raw.get("port"),
                    "dbname": raw.get("dbname") or raw.get("database"),
                    "user": raw.get("user"), "password": raw.get("password")}
        env = {"host": os.getenv("DB_HOST"), "port": os.getenv("DB_PORT"),
               "dbname": os.getenv("DB_NAME"), "user": os.getenv("DB_USER"),
               "password": os.getenv("DB_PASSWORD")}
        merged = {k: (env[k] or data.get(k)) for k in env}
        merged = {k: v for k, v in merged.items() if v not in (None, "")}
        if "port" in merged:
            merged["port"] = int(merged["port"])
        return cls(**merged)


class Database:
    """Opens a short-lived connection per call (simple, safe for a desktop app)."""

    def __init__(self, config=None):
        self.config = config or DatabaseConfig.load()

    @contextmanager
    def cursor(self, dict_rows=True):
        conn = psycopg2.connect(connect_timeout=5, **vars(self.config))
        try:
            with conn:                                   # commit / rollback
                with conn.cursor(cursor_factory=RealDictCursor if dict_rows else None) as cur:
                    yield cur
        finally:
            conn.close()

    def fetch_all(self, sql, params=()):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    def fetch_one(self, sql, params=()):
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=()):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount


# --------------------------------------------------------------------------
# Repositories – one class per table
# --------------------------------------------------------------------------
class Repository:
    table = ""

    def __init__(self, db):
        self.db = db

    def all(self):
        return self.db.fetch_all(f"SELECT * FROM {self.table} ORDER BY 1")

    def count(self):
        return self.db.fetch_one(f"SELECT COUNT(*) AS n FROM {self.table}")["n"]


class TraineeRepository(Repository):
    table = "trainees"

    def by_id(self, trainee_id):
        return self.db.fetch_one("SELECT * FROM trainees WHERE traineeid = %s", (trainee_id,))

    def by_email(self, email):
        return self.db.fetch_one("SELECT * FROM trainees WHERE lower(emailaddress) = lower(%s)", (email,))

    def search(self, text):
        return self.db.fetch_all(
            "SELECT * FROM trainees WHERE fullname ILIKE %s OR emailaddress ILIKE %s ORDER BY fullname",
            (f"%{text}%", f"%{text}%"))

    def add(self, full_name, email, phone=None, postal_code=None, state=None):
        return self.db.execute(
            "INSERT INTO trainees (fullname, emailaddress, phonenumber, postalcode, stateofresidence) "
            "VALUES (%s,%s,%s,%s,%s)", (full_name, email, phone, postal_code, state))


def _yn(col):
    """SQL snippet: boolean column → 'Yes' / 'No' / NULL (the format the old sheets used)."""
    return f"CASE WHEN {col} IS TRUE THEN 'Yes' WHEN {col} IS FALSE THEN 'No' END"


class ApplicationRepository(Repository):
    table = "applications"

    def with_trainee(self):
        """Application rows joined with their trainee, using the OLD sheet headers as keys."""
        return self.db.fetch_all(f"""
            SELECT a.timestamp                       AS "Timestamp",
                   t.fullname                        AS "Full Name",
                   t.emailaddress                    AS "Email",
                   t.phonenumber                     AS "Phone",
                   t.postalcode                      AS "Postal Code",
                   t.stateofresidence                AS "Province",
                   a.currentstatus                   AS "Current Status",
                   a.financialstatus                 AS "Financial Situation",
                   {_yn('a.attendinglanguagecourse')} AS "Currently in a Language Course",
                   a.englishlevel                    AS "English Level",
                   a.dutchlevel                      AS "Dutch Level",
                   {_yn('a.underpressure')}          AS "Municipal Pressure Regarding Work",
                   {_yn('a.completedbootcamp')}      AS "Completed Another IT Bootcamp",
                   {_yn('a.attendedonlineitcourse')} AS "Followed an Online IT Course",
                   a.itexperience                    AS "Prior IT Work Experience",
                   {_yn('a.includedinproject')}      AS "Currently Involved in Another Project",
                   a.motivationforjoining            AS "Motivation",
                   a.applicationterm                 AS "Application Period",
                   a.traineeid                       AS "TraineeID"
            FROM applications a JOIN trainees t ON t.traineeid = a.traineeid
            ORDER BY a.timestamp, a.applicationid""")


class MentorRepository(Repository):
    table = "mentors"

    def with_trainee(self):
        return self.db.fetch_all(f"""
            SELECT m.meetingdate                     AS "Date",
                   t.fullname                        AS "Candidate Name",
                   m.mentorfullname                  AS "Mentor Name",
                   m.thoughts                        AS "Recommendation",
                   {_yn('m.eligibleforvitproject')}  AS "Eligible For VIT Project",
                   m.comments                        AS "Notes",
                   m.traineeid                       AS "TraineeID"
            FROM mentors m JOIN trainees t ON t.traineeid = m.traineeid
            ORDER BY m.meetingdate, m.mentorid""")


class ProjectTrackingRepository(Repository):
    table = "projecttracking"

    def with_trainee(self):
        return self.db.fetch_all("""
            SELECT t.fullname               AS "Full Name",
                   p.projectsubmissiondate  AS "Project Sent Date",
                   p.projectreviewdate      AS "Project Received Date",
                   p.traineeid              AS "TraineeID"
            FROM projecttracking p JOIN trainees t ON t.traineeid = p.traineeid
            ORDER BY p.projectsubmissiondate, p.projecttrackingid""")


class UserRepository(Repository):
    table = "users"

    def by_username(self, username):
        return self.db.fetch_one("SELECT * FROM users WHERE lower(username) = lower(%s)", (username,))

    def add(self, username, password, role="user", hashed=True):
        return self.db.execute(
            "INSERT INTO users (username, password, role) VALUES (%s,%s,%s)",
            (username, hash_password(password) if hashed else password, role))


# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
class AuthService:
    def __init__(self, users):
        self.users = users

    @staticmethod
    def _role(value):
        return "admin" if (value or "").strip().lower() == "admin" else "user"

    def authenticate(self, username, password):
        """Returns (success, role | None, message) – same contract as the old Drive version."""
        try:
            user = self.users.by_username(username or "")
        except psycopg2.Error as exc:
            return False, None, f"Could not read the users table: {exc}"
        if user is None:
            return False, None, "User not found."
        if verify_password(password or "", user["password"]):
            return True, self._role(user["role"]), "Login successful"
        return False, None, "Wrong password."


# --------------------------------------------------------------------------
# Facade used by the application
# --------------------------------------------------------------------------
class TraineeTrackingService:
    def __init__(self, config=None):
        self.db = Database(config)
        self.trainees = TraineeRepository(self.db)
        self.applications = ApplicationRepository(self.db)
        self.mentors = MentorRepository(self.db)
        self.users = UserRepository(self.db)
        self.projects = ProjectTrackingRepository(self.db)
        self.auth = AuthService(self.users)

    # same names / shapes as google_drive_service
    def fetch_applications(self):
        return self.applications.with_trainee()

    def fetch_mentor(self):
        return self.mentors.with_trainee()

    def fetch_interviews(self):
        return self.projects.with_trainee()

    def fetch_users(self):
        return [{"Username": u["username"], "Password": u["password"], "Role": u["role"]}
                for u in self.users.all()]

    def load_users(self):
        """(users, error) with lower-case keys – like the old Drive version."""
        try:
            return [{"username": u["username"], "password": u["password"], "role": u["role"]}
                    for u in self.users.all()], None
        except psycopg2.Error as exc:
            return [], f"Could not read the users table: {exc}"

    def authenticate(self, username, password):
        return self.auth.authenticate(username, password)


# --------------------------------------------------------------------------
# Module-level API (drop-in replacement for google_drive_service)
# --------------------------------------------------------------------------
_service = None


def get_service():
    global _service
    if _service is None:
        _service = TraineeTrackingService()
    return _service


def configure(config):
    """Optional: call once at start-up with a DatabaseConfig."""
    global _service
    _service = TraineeTrackingService(config)


def fetch_applications():
    return get_service().fetch_applications()


def fetch_mentor():
    return get_service().fetch_mentor()


def fetch_interviews():
    return get_service().fetch_interviews()


def fetch_users():
    return get_service().fetch_users()


def load_users():
    return get_service().load_users()


def authenticate(username, password):
    return get_service().authenticate(username, password)

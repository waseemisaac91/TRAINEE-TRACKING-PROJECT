# Database_Module  –  TASK 4: import data from the cloud files (Google Drive) into PostgreSQL
# Imports all 5 tables, in dependency order:
#    Applications sheet -> trainees, applications | Mentor -> mentors | Users -> users | Interviews -> projecttracking

import sys
import datetime as dt
import re
from dataclasses import dataclass, field

import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QComboBox, QFrame, QDialog, QPlainTextEdit,
    QMessageBox, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

from database_service import hash_password
from Ui import SettingsDialog, load_config, save_config
from paged_table import PagedTable

try:
    from services import google_drive_service as gds
except ImportError:
    import google_drive_service as gds


# ----------------------------------------------------------------------------
# 1) Schema (Task1 - Tables.sql)
# ----------------------------------------------------------------------------
TABLES = ["trainees", "applications", "mentors", "users", "projecttracking"]

DDL = """
CREATE TABLE IF NOT EXISTS Trainees (
    TraineeID SERIAL PRIMARY KEY, FullName VARCHAR(100) NOT NULL,
    EmailAddress VARCHAR(255) UNIQUE NOT NULL, PhoneNumber VARCHAR(20),
    PostalCode VARCHAR(10), StateOfResidence VARCHAR(50));
CREATE TABLE IF NOT EXISTS Applications (
    ApplicationID SERIAL PRIMARY KEY,
    TraineeID INTEGER REFERENCES Trainees(TraineeID) ON DELETE CASCADE,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, CurrentStatus VARCHAR(150),
    WillJoinITPHTraining BOOLEAN, FinancialStatus VARCHAR(50),
    AttendingLanguageCourse BOOLEAN, EnglishLevel VARCHAR(20), DutchLevel VARCHAR(20),
    UnderPressure BOOLEAN, CompletedBootcamp BOOLEAN, AttendedOnlineITCourse BOOLEAN,
    ITExperience TEXT, IncludedInProject BOOLEAN, WillingnessToWork BOOLEAN,
    MotivationForJoining TEXT, ApplicationTerm VARCHAR(20));
CREATE TABLE IF NOT EXISTS Mentors (
    MentorID SERIAL PRIMARY KEY, MeetingDate DATE, MentorFullName VARCHAR(100) NOT NULL,
    TraineeID INTEGER REFERENCES Trainees(TraineeID) ON DELETE CASCADE,
    HasRelevantKnowledge BOOLEAN, EligibleForVITProject BOOLEAN, Thoughts TEXT,
    AvailabilityStatus VARCHAR(50), Comments TEXT);
CREATE TABLE IF NOT EXISTS Users (
    UserID SERIAL PRIMARY KEY, Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL, Role VARCHAR(20) NOT NULL);
CREATE TABLE IF NOT EXISTS ProjectTracking (
    ProjectTrackingID SERIAL PRIMARY KEY,
    TraineeID INTEGER REFERENCES Trainees(TraineeID) ON DELETE CASCADE,
    ProjectSubmissionDate DATE, ProjectReviewDate DATE);
"""
WIDEN_STATUS = "ALTER TABLE applications ALTER COLUMN currentstatus TYPE VARCHAR(150)"


# ----------------------------------------------------------------------------
# 2) Helpers
# ----------------------------------------------------------------------------
def norm(s):
    """Header / name comparison: ignore case and extra spaces."""
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return s or None


def parse_datetime(v):
    """Returns (datetime | None, error | None). Month-first is tried before day-first."""
    s = clean(v)
    if not s:
        return None, None
    for f in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%Y %H:%M", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
              "%d/%m/%Y", "%d/%m/%Y %H:%M", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(s, f), None
        except ValueError:
            pass
    return None, f"unreadable date '{s}'"


def yes_no(v):
    s = norm(clean(v) or "")
    return True if s == "yes" else False if s == "no" else None


def connect(cfg):
    return psycopg2.connect(connect_timeout=5, **cfg)


@dataclass
class Plan:
    headers: list
    rows: list
    ops: list = field(default_factory=list)       # (sql, params)
    summary: list = field(default_factory=list)   # lines for the log


# ----------------------------------------------------------------------------
# 3) IMPORTERS (OOP)
# ----------------------------------------------------------------------------
class Importer:
    key = title = sheet = table = ""
    columns = []              # (sheet column, db column, required)
    uses_hash = False

    @property
    def label(self):
        return f"{self.title}  ←  {self.sheet} sheet"

    def prepare(self, records):
        if not records:
            raise ValueError("The sheet is empty (no data rows).")
        recs = [{norm(k): v for k, v in r.items()} for r in records]
        missing = [c for c, _, req in self.columns if req and norm(c) not in recs[0]]
        if missing:
            raise ValueError(f"Column(s) not found in sheet '{self.sheet}': {missing}\n"
                             f"Headers found: {list(records[0].keys())}")
        return recs

    @staticmethod
    def trainees(conn):
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT traineeid, fullname, emailaddress FROM trainees")
                found = cur.fetchall()
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Cannot read table trainees: {(e.pgerror or str(e)).strip()}")
        by_name, by_email = {}, {}
        for tid, name, email in found:
            by_name.setdefault(norm(name), []).append(tid)
            by_email[email.lower()] = (tid, name)
        return by_name, by_email, len(found)

    @staticmethod
    def write_ops(mode, table, values, keys):
        ops = []
        cols = list(values)
        if mode == "update":
            sets = [c for c in cols if c not in keys]
            if sets:
                ops.append((f"UPDATE {table} SET {', '.join(c + '=%s' for c in sets)} WHERE "
                            + " AND ".join(f"{k} IS NOT DISTINCT FROM %s" for k in keys),
                            [values[c] for c in sets] + [values[k] for k in keys]))
        # Add INSERT operation with a check to avoid duplicates
        ops.append((f"INSERT INTO {table} ({', '.join(cols)}) SELECT {', '.join(['%s'] * len(cols))} "
                    f"WHERE NOT EXISTS (SELECT 1 FROM {table} WHERE "
                    + " AND ".join(f"{k} IS NOT DISTINCT FROM %s" for k in keys) + ")",
                    list(values.values()) + [values[k] for k in keys]))
        return ops

    @staticmethod
    def summary(total, rows):
        ready = sum(1 for r in rows if str(r[-1]).startswith("✔"))
        return f"{total} sheet rows · {ready} ready · {total - ready} skipped"

    def build(self, records, mode, hash_pw, conn):
        raise NotImplementedError


class TraineesImporter(Importer):
    key, title, sheet, table = "Trainees", "1 · Trainees", "Applications", "trainees"
    columns = [("Full Name", "fullname", True), ("Email", "emailaddress", True),
               ("Phone", "phonenumber", False), ("Postal Code", "postalcode", False),
               ("Province", "stateofresidence", False)]

    def build(self, records, mode, hash_pw, conn):
        recs = self.prepare(records)
        last = {}
        for i, r in enumerate(recs):
            e = clean(r.get("email"))
            if e:
                last[e.lower()] = i
        rows, ops, conflicts = [], [], []
        for i, r in enumerate(recs):
            name, email = clean(r.get("full name")), clean(r.get("email"))
            phone, postal, prov = clean(r.get("phone")), clean(r.get("postal code")), clean(r.get("province"))
            status = "✔ ready"
            if not name or not email:
                status = "⚠ skipped — name or email is empty"
            elif "@" not in email:
                status = "⚠ skipped — invalid email"
            elif last[email.lower()] != i:
                other = clean(recs[last[email.lower()]].get("full name"))
                if norm(other) != norm(name):
                    status = f"⚠ skipped — email already used by '{other}' (email must be unique: fix it in the sheet)"
                    conflicts.append(name)
                else:
                    status = "⚠ skipped — same person appears again later (latest row used)"
            elif len(name) > 100 or (postal and len(postal) > 10) or (phone and len(phone) > 20):
                status = "⚠ skipped — value too long for the column"
            rows.append([name, email, phone, postal, prov, status])
            if status.startswith("✔"):
                sql = ("INSERT INTO trainees (fullname, emailaddress, phonenumber, postalcode, stateofresidence) "
                       "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (emailaddress) ")
                sql += ("DO UPDATE SET fullname=EXCLUDED.fullname, phonenumber=EXCLUDED.phonenumber, "
                        "postalcode=EXCLUDED.postalcode, stateofresidence=EXCLUDED.stateofresidence"
                        if mode == "update" else "DO NOTHING")
                ops.append((sql, (name, email, phone, postal, prov)))
        summ = [self.summary(len(recs), rows)]
        if conflicts:
            summ.append(f"⚠ Different people share one email, not imported: {', '.join(conflicts)}")
        return Plan(["Full Name → fullname", "Email → emailaddress", "Phone → phonenumber",
                     "Postal Code → postalcode", "Province → stateofresidence", "Status"], rows, ops, summ)


class ApplicationsImporter(Importer):
    key, title, sheet, table = "Applications", "2 · Applications", "Applications", "applications"
    columns = [("Email", "traineeid", True), ("Timestamp", "timestamp", True),
               ("Current Status", "currentstatus", False), ("Financial Situation", "financialstatus", False),
               ("Currently in a Language Course", "attendinglanguagecourse", False),
               ("English Level", "englishlevel", False), ("Dutch Level", "dutchlevel", False),
               ("Municipal Pressure Regarding Work", "underpressure", False),
               ("Completed Another IT Bootcamp", "completedbootcamp", False),
               ("Followed an Online IT Course", "attendedonlineitcourse", False),
               ("Prior IT Work Experience", "itexperience", False),
               ("Currently Involved in Another Project", "includedinproject", False),
               ("Motivation", "motivationforjoining", False),
               ("Reasons for Applying to VIT", "motivationforjoining", False),
               ("Application Period", "applicationterm", False)]

    @staticmethod
    def pressure(v):
        s = norm(clean(v) or "")
        if not s:
            return None
        if s == "no":
            return False
        return True if s.startswith(("yes", "partially", "i am expected")) else None

    @staticmethod
    def bootcamp(v):
        s = norm(clean(v) or "")
        if not s:
            return None
        return s == "yes" or s.startswith("completed")

    def build(self, records, mode, hash_pw, conn):
        recs = self.prepare(records)
        _, by_email, _n = self.trainees(conn)
        rows, ops = [], []
        for r in recs:
            name, email = clean(r.get("full name")), clean(r.get("email"))
            ts, err = parse_datetime(r.get("timestamp"))
            hit = by_email.get((email or "").lower())
            status = "✔ ready"
            if not email:
                status = "⚠ skipped — email is empty"
            elif not hit:
                status = "⚠ skipped — email not found in trainees (import Trainees first)"
            elif name and norm(hit[1]) != norm(name):
                status = f"⚠ skipped — email belongs to trainee '{hit[1]}'"
            elif err or not ts:
                status = f"⚠ skipped — {err or 'timestamp is empty'}"
            vals = dict(
                traineeid=hit[0] if hit else None, timestamp=ts,
                currentstatus=clean(r.get("current status")),
                financialstatus=clean(r.get("financial situation")),
                attendinglanguagecourse=yes_no(r.get("currently in a language course")),
                englishlevel=clean(r.get("english level")), dutchlevel=clean(r.get("dutch level")),
                underpressure=self.pressure(r.get("municipal pressure regarding work")),
                completedbootcamp=self.bootcamp(r.get("completed another it bootcamp")),
                attendedonlineitcourse=yes_no(r.get("followed an online it course")),
                itexperience=clean(r.get("prior it work experience")),
                includedinproject=yes_no(r.get("currently involved in another project")),
                motivationforjoining="\n\nReasons: ".join(
                    x for x in (clean(r.get("motivation")), clean(r.get("reasons for applying to vit"))) if x) or None,
                applicationterm=clean(r.get("application period")))
            if status.startswith("✔") and any(len(str(vals[k])) > n for k, n in
                                              (("financialstatus", 50), ("englishlevel", 20),
                                               ("dutchlevel", 20), ("applicationterm", 20)) if vals[k]):
                status = "⚠ skipped — value too long for the column"
            rows.append([name, hit[0] if hit else None, ts.strftime("%Y-%m-%d %H:%M") if ts else None,
                         vals["currentstatus"], vals["underpressure"], vals["completedbootcamp"],
                         vals["applicationterm"], status])
            if status.startswith("✔"):
                ops += self.write_ops(mode, "applications", vals, ["traineeid", "timestamp"])
        if ops:
            ops.insert(0, (WIDEN_STATUS, ()))
        summ = [self.summary(len(recs), rows)]
        return Plan(["Full Name", "TraineeID (by Email)", "Timestamp", "Current Status",
                     "UnderPressure (rule)", "CompletedBootcamp (rule)", "Application Period", "Status"],
                    rows, ops, summ)


class MentorsImporter(Importer):
    key, title, sheet, table = "Mentors", "3 · Mentors", "Mentor", "mentors"
    columns = [("Candidate Name", "traineeid", True), ("Date", "meetingdate", True),
               ("Mentor Name", "mentorfullname", True), ("Recommendation", "thoughts", False),
               ("Alternative Recommendation", "thoughts", False), ("Score", "thoughts", False),
               ("Secondary Score", "thoughts", False), ("Notes", "comments", False)]

    @staticmethod
    def eligible(rec):
        s = norm(rec or "")
        return None if not s else ("vit project" in s and "next vit" not in s)

    def build(self, records, mode, hash_pw, conn):
        recs = self.prepare(records)
        by_name, _, n_tr = self.trainees(conn)
        rows, ops = [], []
        for r in recs:
            name, mentor = clean(r.get("candidate name")), clean(r.get("mentor name"))
            d, err = parse_datetime(r.get("date"))
            ids = by_name.get(norm(name), []) if name else []
            rec, alt = clean(r.get("recommendation")), clean(r.get("alternative recommendation"))
            sc, sc2 = clean(r.get("score")), clean(r.get("secondary score"))
            thoughts = "; ".join(x for x in (
                f"{rec} (score {sc})" if rec else None,
                f"alternative: {alt} (score {sc2})" if alt else None) if x) or None
            status = "✔ ready"
            if not name or not mentor:
                status = "⚠ skipped — candidate or mentor name is empty"
            elif not ids:
                status = "⚠ skipped — candidate not found in trainees (import Trainees first)"
            elif len(ids) > 1:
                status = f"⚠ skipped — {len(ids)} trainees share this name"
            elif err or not d:
                status = f"⚠ skipped — {err or 'date is empty'}"
            elif len(mentor) > 100:
                status = "⚠ skipped — mentor name too long"
            vals = dict(meetingdate=d.date() if d else None, mentorfullname=mentor,
                        traineeid=ids[0] if len(ids) == 1 else None,
                        eligibleforvitproject=self.eligible(rec), thoughts=thoughts,
                        comments=clean(r.get("notes")))
            rows.append([name, vals["traineeid"], vals["meetingdate"], mentor,
                         vals["eligibleforvitproject"], thoughts, status])
            if status.startswith("✔"):
                ops += self.write_ops(mode, "mentors", vals,
                                      ["traineeid", "meetingdate", "mentorfullname"])
        summ = [self.summary(len(recs), rows)]
        return Plan(["Candidate Name → traineeid", "TraineeID", "Date → meetingdate", "Mentor Name",
                     "Eligible (rule)", "Thoughts (recommendation + scores)", "Status"], rows, ops, summ)


class UsersImporter(Importer):
    key, title, sheet, table = "Users", "4 · Users", "Users", "users"
    uses_hash = True
    columns = [("Username", "username", True), ("Password", "password", True), ("Role", "role", True)]

    def build(self, records, mode, hash_pw, conn):
        recs = self.prepare(records)
        last = {}
        for i, r in enumerate(recs):
            u = clean(r.get("username"))
            if u:
                last[u] = i
        rows, ops = [], []
        for i, r in enumerate(recs):
            user, pw, role = clean(r.get("username")), clean(r.get("password")), clean(r.get("role"))
            role = role.lower() if role else None
            status = "✔ ready"
            if not (user and pw and role):
                status = "⚠ skipped — username, password or role is empty"
            elif last[user] != i:
                status = "⚠ skipped — duplicate username (latest row used)"
            elif len(user) > 50 or len(role) > 20:
                status = "⚠ skipped — value too long for the column"
            elif role not in ("admin", "user"):
                status = "✔ ready (note: role is not admin/user)"
            rows.append([user, "••••••" if pw else None, role, status])
            if status.startswith("✔"):
                sql = "INSERT INTO users (username, password, role) VALUES (%s,%s,%s) ON CONFLICT (username) "
                sql += ("DO UPDATE SET password=EXCLUDED.password, role=EXCLUDED.role"
                        if mode == "update" else "DO NOTHING")
                ops.append((sql, (user, hash_password(pw) if hash_pw else pw, role)))
        note = "passwords will be stored HASHED (PBKDF2)" if hash_pw else "passwords will be stored as PLAIN TEXT"
        return Plan(["Username → username", "Password → password", "Role → role", "Status"],
                    rows, ops, [self.summary(len(recs), rows), note])


class ProjectTrackingImporter(Importer):
    key, title, sheet, table = "ProjectTracking", "5 · ProjectTracking", "Interviews", "projecttracking"
    columns = [("Full Name", "traineeid", True), ("Project Sent Date", "projectsubmissiondate", False),
               ("Project Received Date", "projectreviewdate", False)]

    def build(self, records, mode, hash_pw, conn):
        recs = self.prepare(records)
        by_name, _, n_tr = self.trainees(conn)
        rows, ops = [], []
        for r in recs:
            name = clean(r.get("full name"))
            sent, e1 = parse_datetime(r.get("project sent date"))
            recv, e2 = parse_datetime(r.get("project received date"))
            ids = by_name.get(norm(name), []) if name else []
            tid = ids[0] if len(ids) == 1 else None
            if not name:
                status = "⚠ skipped — name is empty"
            elif not ids:
                status = "⚠ skipped — not found in trainees (import Trainees first)"
            elif len(ids) > 1:
                status = f"⚠ skipped — {len(ids)} trainees share this name"
            elif e1 or e2:
                status = f"⚠ skipped — {e1 or e2}"
            else:
                status = "✔ ready"
            sd, rd = (sent.date() if sent else None), (recv.date() if recv else None)
            rows.append([name, tid, sd, rd, status])
            if status.startswith("✔"):
                ops += self.write_ops(mode, "projecttracking",
                                      dict(traineeid=tid, projectsubmissiondate=sd, projectreviewdate=rd),
                                      ["traineeid", "projectsubmissiondate"])
        summ = [self.summary(len(recs), rows)]
        if not n_tr:
            summ.append("⚠ The trainees table is empty — import Trainees first.")
        return Plan(["Full Name → traineeid", "TraineeID (lookup)", "Project Sent Date → projectsubmissiondate",
                     "Project Received Date → projectreviewdate", "Status"], rows, ops, summ)


IMPORTERS = [TraineesImporter(), ApplicationsImporter(), MentorsImporter(),
             UsersImporter(), ProjectTrackingImporter()]
BY_KEY = {i.key: i for i in IMPORTERS}
SHEETS = ["Applications", "Interviews", "Mentor", "Users"]


def execute_ops(cfg, ops):
    conn = connect(cfg)
    try:
        with conn:
            with conn.cursor() as cur:
                written = 0
                for sql, params in ops:
                    cur.execute(sql, params)
                    written += max(cur.rowcount, 0)
        return written
    finally:
        conn.close()


# ----------------------------------------------------------------------------
# 4) Background worker
# ----------------------------------------------------------------------------
class Worker(QThread):
    done = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            self.done.emit(self.fn())
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")


# ----------------------------------------------------------------------------
# 5) Main Window
# ----------------------------------------------------------------------------
class ImporterApp(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.plan = None
        self._workers = []
        self.stat_labels = {}
        self.setWindowTitle("Trainee Tracking Project")
        self.resize(1280, 880)

        central = QWidget()
        central.setObjectName("Central")
        
        # Add Scroll Area to handle small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(central)
        self.setCentralWidget(scroll)
        
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 12)
        root.setSpacing(16)
        root.addLayout(self.build_header())
        root.addLayout(self.build_stats())

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_check_tab(), "🔎  Field Check")
        self.tabs.addTab(self.create_import_tab(), "📥  Import")
        self.tabs.addTab(self.create_tables_tab(), "🗄️  Database Tables")
        self.tabs.addTab(self.create_custom_query_tab(), "⚡  Custom Query") # Custom Query Tab
        root.addWidget(self.tabs, 1)
        self.statusBar().showMessage("Ready")
        QTimer.singleShot(0, self.refresh_stats)

    # ---------------------------------------------------------------- helpers
    def run_async(self, fn, on_done, busy="Working…"):
        self.statusBar().showMessage(busy)
        w = Worker(fn)
        self._workers.append(w)
        w.done.connect(lambda res: (self.statusBar().showMessage("Ready"), on_done(res)))
        w.failed.connect(self.on_error)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        w.start()

    def on_error(self, msg):
        self.statusBar().showMessage("Error")
        self.log(f"❌ {msg}")
        QMessageBox.critical(self, "Error", msg)
        self.btn_load.setEnabled(True)
        self.btn_all.setEnabled(True)
        self.btn_check.setEnabled(True)

    def log(self, text):
        self.logbox.appendPlainText(f"[{dt.datetime.now():%H:%M:%S}] {text}")

    def query(self, sql, params=()):
        conn = connect(self.cfg)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(sql, params)
                cols = [d[0] for d in cur.description] if cur.description else []
                return cols, (cur.fetchall() if cur.description else [])
        finally:
            conn.close()

    # ---------------------------------------------------------------- header + stats
    def build_header(self):
        box = QHBoxLayout()
        left = QVBoxLayout()
        t = QLabel("From Cloud Chaos to Database Clarity")
        t.setObjectName("Header")
        s = QLabel(f"Google Drive Sheets  →  PostgreSQL  ·  {self.cfg['user']}@{self.cfg['host']}:"
                   f"{self.cfg['port']}/{self.cfg['database']}")
        s.setObjectName("SubHeader")
        left.addWidget(t)
        left.addWidget(s)
        box.addLayout(left)
        box.addStretch()
        b1 = QPushButton("🛠  Create missing tables")
        b1.setObjectName("SecondaryButton")
        b1.clicked.connect(self.create_tables)
        b2 = QPushButton("🔄  Refresh")
        b2.setObjectName("SecondaryButton")
        b2.clicked.connect(self.refresh_stats)
        box.addWidget(b1)
        box.addWidget(b2)
        return box

    def build_stats(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        for tname in TABLES:
            card = QFrame()
            card.setObjectName("StatCard")
            lay = QVBoxLayout(card)
            lay.setContentsMargins(16, 12, 16, 12)
            val = QLabel("—")
            val.setObjectName("StatValue")
            ttl = QLabel(tname)
            ttl.setObjectName("StatTitle")
            lay.addWidget(val)
            lay.addWidget(ttl)
            self.stat_labels[tname] = val
            row.addWidget(card)
        return row

    def refresh_stats(self):
        for tname in TABLES:
            try:
                _, rows = self.query(f"SELECT COUNT(*) FROM {tname}")
                self.stat_labels[tname].setText(str(rows[0][0]))
            except psycopg2.Error:
                self.stat_labels[tname].setText("✖")
        if hasattr(self, "tbl_combo"):
            self.load_table()

    def create_tables(self):
        try:
            self.query(DDL)
            self.log("🛠 Tables checked / created.")
            self.refresh_stats()
            QMessageBox.information(self, "Tables", "All 5 tables exist now.")
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------------------------------------------------------------- tab 1: field check
    def create_check_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        top = QHBoxLayout()
        info = QLabel("Reads the header row of each Google Sheet through google_drive_service and compares "
                      "it with the PostgreSQL column names.")
        info.setObjectName("SubHeader")
        self.btn_check = QPushButton("🔎  Check sheets on Google Drive")
        self.btn_check.clicked.connect(self.run_check)
        top.addWidget(info, 1)
        top.addWidget(self.btn_check)
        lay.addLayout(top)
        self.check_label = QLabel("")
        self.check_label.setObjectName("InfoLabel")
        lay.addWidget(self.check_label)
        self.check_table = PagedTable(["Sheet file", "Sheet column", "→ DB table.column",
                                       "In Google Sheet", "In PostgreSQL", "Note"],
                                      center_cols=(3, 4), fit_columns=True, default_size="100")
        lay.addWidget(self.check_table, 1)
        return w

    def run_check(self):
        self.btn_check.setEnabled(False)

        def work():
            client = gds.get_client()
            headers = {}
            for key in SHEETS:
                sh = client.open_by_key(gds.SPREADSHEET_IDS[key]).sheet1
                headers[key] = [h for h in sh.row_values(1)]
            _, cols = self.query("SELECT table_name, column_name FROM information_schema.columns "
                                 "WHERE table_schema='public'")
            db = {}
            for t, c in cols:
                db.setdefault(t.lower(), set()).add(c.lower())
            return headers, db

        self.run_async(work, self.on_check, "Reading headers from Google Drive…")

    def on_check(self, res):
        self.btn_check.setEnabled(True)
        headers, db = res
        rows, problems = [], 0
        for sheet in SHEETS:
            hs = headers[sheet]
            exact, normed = set(hs), {norm(h): h for h in hs}
            used = set()
            for entry in IMPORTERS:
                if entry.sheet != sheet:
                    continue
                for col, dbcol, _req in entry.columns:
                    note = ""
                    if col in exact:
                        s_ok = "✔ found"
                        used.add(col)
                    elif norm(col) in normed:
                        s_ok = "✔ found"
                        used.add(normed[norm(col)])
                        note = f"spelling/space differs: '{normed[norm(col)]}'"
                    else:
                        s_ok = "✖ MISSING"
                        problems += 1
                    if entry.table not in db:
                        d_ok, problems = "✖ no table", problems + 1
                    elif dbcol in db[entry.table]:
                        d_ok = "✔ found"
                    else:
                        d_ok, problems = "✖ MISSING", problems + 1
                    if dbcol == "traineeid":
                        note = (note + " looked up in trainees").strip()
                    rows.append([sheet, col, f"{entry.table}.{dbcol}", s_ok, d_ok, note])
            for h in hs:
                if h not in used:
                    rows.append([sheet, h, "—", "✔ found", "—", "not imported"])
        self.check_table.set_rows(rows)
        if problems:
            self.check_label.setText(f"⚠ {problems} name problem(s) found — see rows marked ✖.")
        else:
            self.check_label.setText("✅ All mapped field names exist in the Google Sheets and in PostgreSQL.")

    # ---------------------------------------------------------------- tab 2: import
    def create_import_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        form = QFrame()
        form.setObjectName("FormFrame")
        fl = QHBoxLayout(form)
        fl.setContentsMargins(16, 14, 16, 14)
        fl.setSpacing(14)
        self.job_combo = QComboBox()
        for imp in IMPORTERS:
            self.job_combo.addItem(imp.label, imp.key)
        self.job_combo.currentIndexChanged.connect(self.on_job_changed)
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Skip rows that already exist", "skip")
        self.mode_combo.addItem("Update rows that already exist", "update")
        self.hash_check = QCheckBox("Hash passwords (recommended)")
        self.hash_check.setChecked(True)
        self.btn_load = QPushButton("1 · Load && Validate")
        self.btn_load.clicked.connect(self.load_plan)
        self.btn_all = QPushButton("⚡ Import ALL 5 (in order)")
        self.btn_all.setObjectName("WarnButton")
        self.btn_all.clicked.connect(self.import_all)
        self.btn_import = QPushButton("2 · Import to PostgreSQL")
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self.do_import)
        fl.addWidget(self.job_combo, 3)
        fl.addWidget(self.mode_combo, 2)
        fl.addWidget(self.hash_check)
        fl.addWidget(self.btn_load)
        fl.addWidget(self.btn_import)
        fl.addWidget(self.btn_all)
        lay.addWidget(form)

        self.map_label = QLabel("")
        self.map_label.setObjectName("InfoLabel")
        self.map_label.setWordWrap(True)
        lay.addWidget(self.map_label)

        self.preview = PagedTable([" "], center_cols=(), fit_columns=True, default_size="50")
        lay.addWidget(self.preview, 1)

        self.logbox = QPlainTextEdit()
        self.logbox.setObjectName("QueryEditor")
        self.logbox.setReadOnly(True)
        self.logbox.setFixedHeight(130)
        lay.addWidget(self.logbox)
        self.on_job_changed()
        return w

    def job_key(self):
        return self.job_combo.currentData()

    def on_job_changed(self):
        key = self.job_key()
        imp = BY_KEY[key]
        pairs = "   ·   ".join(f"{c}  →  {d}" for c, d, _ in imp.columns)
        self.map_label.setText(f"Sheet “{imp.sheet}”  →  table {imp.table}:   {pairs}")
        self.hash_check.setVisible(imp.uses_hash)
        self.btn_import.setEnabled(False)
        self.plan = None

    def load_plan(self):
        key, mode = self.job_key(), self.mode_combo.currentData()
        hash_pw = self.hash_check.isChecked()
        self.btn_load.setEnabled(False)
        self.btn_import.setEnabled(False)

        def work():
            imp = BY_KEY[key]
            records = gds.read_sheet(imp.sheet)
            conn = connect(self.cfg)
            try:
                return imp.build(records, mode, hash_pw, conn)
            finally:
                conn.close()

        self.run_async(work, self.on_plan, "Reading from Google Drive…")

    def on_plan(self, plan):
        self.btn_load.setEnabled(True)
        self.plan = plan
        self.preview.set_columns(plan.headers)
        self.preview.set_rows(plan.rows)
        for line in plan.summary:
            self.log(line)
        self.btn_import.setEnabled(bool(plan.ops))

    def do_import(self):
        if not self.plan or not self.plan.ops:
            return
        n = len(self.plan.ops)
        if QMessageBox.question(self, "Import", f"Write the validated rows to PostgreSQL now?\n"
                                f"({n} operations, one transaction)") != QMessageBox.StandardButton.Yes:
            return
        self.btn_import.setEnabled(False)
        ops, cfg = self.plan.ops, self.cfg
        self.run_async(lambda: execute_ops(cfg, ops), self.on_imported, "Writing to PostgreSQL…")

    def on_imported(self, written):
        # Add comment after insert rows
        self.log(f"✅ Done — {written} row(s) written "
                 f"(rows that already existed are skipped or updated depending on the mode).")
        self.plan = None
        self.refresh_stats()

    def import_all(self):
        if QMessageBox.question(self, "Import ALL", "Read all 4 sheets from Google Drive and import the 5 tables "
                                "in order (Trainees → Applications → Mentors → Users → ProjectTracking)?"
                                ) != QMessageBox.StandardButton.Yes:
            return
        mode, hash_pw, cfg = self.mode_combo.currentData(), self.hash_check.isChecked(), self.cfg
        self.btn_all.setEnabled(False)

        def work():
            out = []
            for imp in IMPORTERS:
                records = gds.read_sheet(imp.sheet)
                conn = connect(cfg)
                try:
                    plan = imp.build(records, mode, hash_pw, conn)
                finally:
                    conn.close()
                out.append((imp.title, plan.summary, execute_ops(cfg, plan.ops) if plan.ops else 0))
            return out

        self.run_async(work, self.on_all_done, "Importing all tables…")

    def on_all_done(self, out):
        self.btn_all.setEnabled(True)
        for title, summ, n in out:
            # Add comment after insert rows for each table
            self.log(f"{title}: {' | '.join(summ)} → {n} row(s) written")
        self.log("✅ Import ALL finished.")
        self.refresh_stats()

    # ---------------------------------------------------------------- tab 3: tables
    def create_tables_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        top = QHBoxLayout()
        self.tbl_combo = QComboBox()
        self.tbl_combo.addItems(TABLES)
        self.tbl_combo.setCurrentText("users")
        self.tbl_combo.currentIndexChanged.connect(self.load_table)
        btn = QPushButton("🔄 Reload")
        btn.setObjectName("SecondaryButton")
        btn.clicked.connect(self.load_table)
        top.addWidget(self.tbl_combo)
        top.addWidget(btn)
        top.addStretch()
        lay.addLayout(top)
        self.data_table = PagedTable([" "], center_cols=(0,), fit_columns=True)
        lay.addWidget(self.data_table, 1)
        return w

    def load_table(self):
        t = self.tbl_combo.currentText()
        try:
            cols, rows = self.query(f"SELECT * FROM {t} ORDER BY 1 LIMIT 100000")
        except psycopg2.Error as e:
            self.data_table.clear()
            self.statusBar().showMessage(f"Table {t}: {str(e).strip()}")
            return
        if "password" in cols:
            i = cols.index("password")
            rows = [[("••••••" if j == i and v else v) for j, v in enumerate(r)] for r in rows]
        self.data_table.set_columns(cols)
        self.data_table.set_rows(rows)

    # ---------------------------------------------------------------- tab 4: custom query
    def create_custom_query_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        info = QLabel("Write and execute custom SQL queries (e.g., INSERT, UPDATE, DELETE).")
        info.setObjectName("SubHeader")
        lay.addWidget(info)

        self.query_edit = QPlainTextEdit()
        self.query_edit.setObjectName("QueryEditor")
        self.query_edit.setPlaceholderText("-- Write your SQL query here...\n-- Example: INSERT INTO trainees (fullname, emailaddress) VALUES ('Ali', 'ali@test.com');")
        self.query_edit.setMinimumHeight(90)
        self.query_edit.setMaximumHeight(150)
        lay.addWidget(self.query_edit, 0)

        btn_layout = QHBoxLayout()
        self.btn_run_query = QPushButton("▶️ Execute Query")
        self.btn_run_query.clicked.connect(self.execute_custom_query)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_run_query)
        lay.addLayout(btn_layout)

        self.query_result_table = PagedTable([" "], center_cols=(), fit_columns=True)
        lay.addWidget(self.query_result_table, 1)
        self.query_result_table.setMinimumHeight(320)
        return w

    def execute_custom_query(self):
        sql = self.query_edit.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Warning", "Please write a query first.")
            return

        try:
            conn = connect(self.cfg)
            with conn, conn.cursor() as cur:
                cur.execute(sql)
                
                # If it's a SELECT query, show results
                if cur.description:
                    cols = [d[0] for d in cur.description]
                    rows = cur.fetchall()
                    self.query_result_table.set_columns(cols)
                    self.query_result_table.set_rows(rows)
                    
                    msg = f"✅ Query returned {len(rows)} rows."
                    self.log(msg)
                    QMessageBox.information(self, "Success", msg) # إظهار النتيجة في صندوق
                    
                else:
                    # If it's an INSERT/UPDATE/DELETE
                    written = cur.rowcount
                    self.query_result_table.clear()
                    
                    msg = f"✅ Command executed — {written} row(s) affected."
                    self.log(msg)
                    QMessageBox.information(self, "Success", msg) # إظهار النتيجة في صندوق
                    self.refresh_stats()
                    
        except psycopg2.Error as e:
            self.log(f"❌ Error: {str(e).strip()}")
            QMessageBox.critical(self, "Query Error", str(e))
        finally:
            if conn:
                conn.close()

# ----------------------------------------------------------------------------
# MODERN UI STYLESHEET
# ----------------------------------------------------------------------------
MODERN_STYLESHEET = """
QMainWindow, QDialog { background-color: #0f1117; }
QWidget { color: #e6e8ef; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }

QLabel#Header { font-size: 24px; font-weight: 700; color: #ffffff; }
QLabel#SubHeader { color: #8b93a7; font-size: 12px; }
QLabel#DialogTitle { font-size: 18px; font-weight: 700; color: #ffffff; }
QLabel#InfoLabel { background-color: #232838; border: 1px solid #2f3547; border-radius: 8px; padding: 9px 12px; color: #e6e8ef; }

QFrame#StatCard { background-color: #171a23; border: 1px solid #262b3a; border-radius: 12px; }
QLabel#StatValue { font-size: 26px; font-weight: 700; color: #ffffff; }
QLabel#StatTitle { color: #8b93a7; font-size: 12px; }

QTabWidget::pane { border: 1px solid #262b3a; border-radius: 12px; background-color: #171a23; top: -1px; }
QTabBar::tab { background: transparent; color: #8b93a7; padding: 11px 22px; margin-right: 4px;
               border-top-left-radius: 10px; border-top-right-radius: 10px; font-size: 14px; }
QTabBar::tab:hover { color: #ffffff; }
QTabBar::tab:selected { background: #171a23; color: #a5b4fc; font-weight: 700; border: 1px solid #262b3a; border-bottom: none; }

QFrame#FormFrame { background-color: #1e2230; border: 1px solid #2a2f3f; border-radius: 12px; }

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {
    background-color: #232838; color: #ffffff; border: 1px solid #2f3547;
    border-radius: 8px; padding: 9px 12px; min-height: 18px; selection-background-color: #6366f1;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #6366f1; }
QComboBox QAbstractItemView { background-color: #1e2230; color: #ffffff; border: 1px solid #2f3547;
                              selection-background-color: #6366f1; outline: none; }

QPushButton { background-color: #6366f1; color: white; border: none; border-radius: 8px;
              padding: 10px 20px; font-size: 13px; font-weight: 600; }
QPushButton:hover { background-color: #7c7ff5; }
QPushButton:pressed { background-color: #4f52d9; }
QPushButton:disabled { background-color: #2a2f3f; color: #5d667c; }
QPushButton#SecondaryButton { background-color: #2a2f3f; color: #e6e8ef; }
QPushButton#SecondaryButton:hover { background-color: #353b4f; }
QPushButton#WarnButton { background-color: #f59e0b; color: #1a1300; }
QPushButton#WarnButton:hover { background-color: #fbb024; }

QTableWidget { background-color: #171a23; alternate-background-color: #1b1f2b; color: #e6e8ef;
               border: 1px solid #262b3a; border-radius: 10px; outline: none; }
QTableWidget::item { padding: 4px 8px; border: none; }
QTableWidget::item:selected { background-color: #6366f1; color: #ffffff; }
QHeaderView::section { background-color: #1e2230; color: #a5b4fc; font-weight: 700; border: none;
                       border-bottom: 1px solid #2a2f3f; padding: 10px 8px; }

QScrollBar:vertical { background: #12151d; width: 14px; margin: 0; border-radius: 7px; }
QScrollBar::handle:vertical { background: #4a5170; border-radius: 6px; min-height: 40px; margin: 2px; }
QScrollBar::handle:vertical:hover { background: #6366f1; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; width: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: #12151d; height: 14px; margin: 0; border-radius: 7px; }
QScrollBar::handle:horizontal { background: #4a5170; border-radius: 6px; min-width: 40px; margin: 2px; }
QScrollBar::handle:horizontal:hover { background: #6366f1; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { height: 0; width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
QTableCornerButton::section { background-color: #1e2230; border: none; }
QTableWidget QHeaderView { background-color: #1e2230; }

QScrollArea { background-color: #0f1117; border: none; }
QWidget#Central { background-color: #0f1117; }
QPlainTextEdit#QueryEditor { background-color: #12151d; color: #e6e8ef; border: 1px solid #2f3547;
                             border-radius: 8px; padding: 10px; selection-background-color: #6366f1; }
QPlainTextEdit#QueryEditor:focus { border: 1px solid #6366f1; }
QStatusBar { color: #8b93a7; }

QMenu { background-color: #1e2230; color: #e6e8ef; border: 1px solid #2f3547;
        border-radius: 8px; padding: 6px; }
QMenu::item { background-color: transparent; padding: 7px 28px 7px 14px; border-radius: 6px; }
QMenu::item:selected { background-color: #6366f1; color: #ffffff; }
QMenu::item:disabled { color: #5d667c; }
QMenu::separator { height: 1px; background: #2f3547; margin: 5px 8px; }
QMenu::icon { padding-left: 6px; }
QMessageBox { background-color: #171a23; }
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_STYLESHEET)  # Apply the modern style
    
    login = SettingsDialog(load_config())
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)
    try:
        save_config(login.saved_values())
    except OSError:
        pass
    window = ImporterApp(login.values())
    window.show()
    sys.exit(app.exec())
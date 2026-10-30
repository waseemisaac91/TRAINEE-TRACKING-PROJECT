-- 1. Create Trainees Table
CREATE TABLE Trainees (
    TraineeID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    EmailAddress VARCHAR(255) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20),
    PostalCode VARCHAR(10),
    StateOfResidence VARCHAR(50)
);

-- 2. Create Applications Table (Linked to Trainees)
CREATE TABLE Applications (
    ApplicationID SERIAL PRIMARY KEY,
    TraineeID INTEGER REFERENCES Trainees(TraineeID) ON DELETE CASCADE,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CurrentStatus VARCHAR(50),
    WillJoinITPHTraining BOOLEAN,
    FinancialStatus VARCHAR(50),
    AttendingLanguageCourse BOOLEAN,
    EnglishLevel VARCHAR(20),
    DutchLevel VARCHAR(20),
    UnderPressure BOOLEAN,
    CompletedBootcamp BOOLEAN,
    AttendedOnlineITCourse BOOLEAN,
    ITExperience TEXT,
    IncludedInProject BOOLEAN,
    WillingnessToWork BOOLEAN,
    MotivationForJoining TEXT,
    ApplicationTerm VARCHAR(20)
);

-- 3. Create Mentors Table (Linked to Trainees)
CREATE TABLE Mentors (
    MentorID SERIAL PRIMARY KEY,
    MeetingDate DATE,
    MentorFullName VARCHAR(100) NOT NULL,
    TraineeID INTEGER REFERENCES Trainees(TraineeID) ON DELETE CASCADE,
    HasRelevantKnowledge BOOLEAN,
    EligibleForVITProject BOOLEAN,
    Thoughts TEXT,
    AvailabilityStatus VARCHAR(50),
    Comments TEXT
);

-- 4. Create Users Table (Standalone)
CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Role VARCHAR(20) NOT NULL
);

-- 5. Create ProjectTracking Table (Linked to Trainees)
CREATE TABLE ProjectTracking (
    ProjectTrackingID SERIAL PRIMARY KEY,
    TraineeID INTEGER REFERENCES Trainees(TraineeID) ON DELETE CASCADE,
    ProjectSubmissionDate DATE,
    ProjectReviewDate DATE
);
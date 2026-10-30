-- ==========================================
-- VIT SYSTEM COMPLETE DATA SCRIPT (MULTIPLE RECORDS)
-- ==========================================

-- ==========================================
-- 1. Insert 45 Trainees (IDs 1-45)
-- ==========================================
INSERT INTO Trainees (FullName, EmailAddress, PhoneNumber, PostalCode, StateOfResidence) VALUES
('Ahmet Yılmaz', 'ahmet.yilmaz@example.com', '+31 6 10000001', '1011AB', 'Noord-Holland'),
('Ayşe Demir', 'ayse.demir@example.com', '+31 6 10000002', '3011CD', 'Zuid-Holland'),
('Mohammed Abdullah', 'mohammed.abdullah@example.com', '+31 6 10000003', '5611EF', 'Noord-Brabant'),
('Fatima Al-Zahra', 'fatima.zahra@example.com', '+31 6 10000004', '9711GH', 'Groningen'),
('Mehmet Kaya', 'mehmet.kaya@example.com', '+31 6 10000005', '3511IJ', 'Utrecht'),
('Sara Ahmed', 'sara.ahmed@example.com', '+31 6 10000006', '2011KL', 'Noord-Holland'),
('Emre Çelik', 'emre.celik@example.com', '+31 6 10000007', '5011MN', 'Noord-Brabant'),
('Omar Khaled', 'omar.khaled@example.com', '+31 6 10000008', '6211OP', 'Limburg'),
('Zeynep Şahin', 'zeynep.sahin@example.com', '+31 6 10000009', '2511QR', 'Zuid-Holland'),
('Ali Hassan', 'ali.hassan@example.com', '+31 6 10000010', '7311ST', 'Gelderland'),
('Mustafa Yıldız', 'mustafa.yildiz@example.com', '+31 6 10000011', '8911UV', 'Friesland'),
('Layla Mahmoud', 'layla.mahmoud@example.com', '+31 6 10000012', '4331WX', 'Zeeland'),
('Hussein Al-Sayed', 'hussein.sayed@example.com', '+31 6 10000013', '9401YZ', 'Drenthe'),
('Büşra Öztürk', 'busra.ozturk@example.com', '+31 6 10000014', '6501AB', 'Gelderland'),
('Yousef Ibrahim', 'yousef.ibrahim@example.com', '+31 6 10000015', '7811CD', 'Drenthe'),
('Nour Al-Huda', 'nour.alhuda@example.com', '+31 6 10000016', '2211EF', 'Zuid-Holland'),
('Can Aydın', 'can.aydin@example.com', '+31 6 10000017', '1811GH', 'Noord-Holland'),
('Rania Kamal', 'rania.kamal@example.com', '+31 6 10000018', '5211IJ', 'Noord-Brabant'),
('Hasan Arslan', 'hasan.arslan@example.com', '+31 6 10000019', '7551KL', 'Overijssel'),
('Mariam Saleh', 'mariam.saleh@example.com', '+31 6 10000020', '8911MN', 'Friesland'),
('Yusuf Aydın', 'yusuf.aydin@example.com', '+31 6 10000021', '1012AB', 'Noord-Holland'),
('Hiba Tariq', 'hiba.tariq@example.com', '+31 6 10000022', '3012CD', 'Zuid-Holland'),
('Kerem Koç', 'kerem.koc@example.com', '+31 6 10000023', '5612EF', 'Noord-Brabant'),
('Dina Samir', 'dina.samir@example.com', '+31 6 10000024', '9712GH', 'Groningen'),
('Baran Tekin', 'baran.tekin@example.com', '+31 6 10000025', '3512IJ', 'Utrecht'),
('Salma Nabil', 'salma.nabil@example.com', '+31 6 10000026', '2012KL', 'Noord-Holland'),
('Ozan Yılmaz', 'ozan.yilmaz@example.com', '+31 6 10000027', '5012MN', 'Noord-Brabant'),
('Yara Haddad', 'yara.haddad@example.com', '+31 6 10000028', '6212OP', 'Limburg'),
('Efe Demir', 'efe.demir@example.com', '+31 6 10000029', '2512QR', 'Zuid-Holland'),
('Amina Yusuf', 'amina.yusuf@example.com', '+31 6 10000030', '7312ST', 'Gelderland'),
('Bilal Zaid', 'bilal.zaid@example.com', '+31 6 10000031', '1013AB', 'Noord-Holland'),
('Lina Haddad', 'lina.haddad@example.com', '+31 6 10000032', '3013CD', 'Zuid-Holland'),
('Kaan Yılmaz', 'kaan.yilmaz@example.com', '+31 6 10000033', '5613EF', 'Noord-Brabant'),
('Reem Khalil', 'reem.khalil@example.com', '+31 6 10000034', '9713GH', 'Groningen'),
('Tolga Çetin', 'tolga.cetin@example.com', '+31 6 10000035', '3513IJ', 'Utrecht'),
('Aya Mansour', 'aya.mansour@example.com', '+31 6 10000036', '2013KL', 'Noord-Holland'),
('Berkay Aslan', 'berkay.aslan@example.com', '+31 6 10000037', '5013MN', 'Noord-Brabant'),
('Hana Youssef', 'hana.youssef@example.com', '+31 6 10000038', '6213OP', 'Limburg'),
('Ece Kara', 'ece.kara@example.com', '+31 6 10000039', '2513QR', 'Zuid-Holland'),
('Nasser Ahmed', 'nasser.ahmed@example.com', '+31 6 10000040', '7313ST', 'Gelderland'),
('Selin Yıldız', 'selin.yildiz@example.com', '+31 6 10000041', '1014AB', 'Noord-Holland'),
('Majid Al-Farsi', 'majid.alfarsi@example.com', '+31 6 10000042', '3014CD', 'Zuid-Holland'),
('Deniz Koç', 'deniz.koc@example.com', '+31 6 10000043', '5614EF', 'Noord-Brabant'),
('Rana Salim', 'rana.salim@example.com', '+31 6 10000044', '9714GH', 'Groningen'),
('Kadir Demir', 'kadir.demir@example.com', '+31 6 10000045', '3514IJ', 'Utrecht');

-- ==========================================
-- 2. Insert Applications (Multiple records for many trainees)
-- ==========================================
INSERT INTO Applications 
(TraineeID, CurrentStatus, WillJoinITPHTraining, FinancialStatus, AttendingLanguageCourse, EnglishLevel, DutchLevel, UnderPressure, CompletedBootcamp, AttendedOnlineITCourse, ITExperience, IncludedInProject, WillingnessToWork, MotivationForJoining, ApplicationTerm) 
VALUES
-- Ahmet (ID: 1) - 3 Applications
(1, 'Rejected', FALSE, 'Needs Support', TRUE, 'B1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'First attempt.', 'Spring 2025'),
(1, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'A2', TRUE, FALSE, TRUE, 'Some Python experience', TRUE, TRUE, 'I want to transition into IT.', 'Fall 2026'),
(1, 'In Review', TRUE, 'Stable', TRUE, 'B2', 'A2', TRUE, FALSE, TRUE, 'Some Python experience', TRUE, TRUE, 'Applying again for Spring.', 'Spring 2027'),
-- Ayşe (ID: 2) - 2 Applications
(2, 'Pending', FALSE, 'Needs Support', TRUE, 'B1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Looking for a career change.', 'Fall 2026'),
(2, 'In Review', TRUE, 'Stable', TRUE, 'B2', 'A2', TRUE, FALSE, FALSE, 'Basic HTML', FALSE, TRUE, 'Better this time.', 'Spring 2027'),
-- Mohammed (ID: 3) - 2 Applications
(3, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B1', TRUE, TRUE, TRUE, '2 years as a junior dev', TRUE, TRUE, 'To improve my skills.', 'Fall 2026'),
(3, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B1', TRUE, TRUE, TRUE, '2 years as a junior dev', TRUE, TRUE, 'Second application.', 'Spring 2027'),
-- Fatima (ID: 4)
(4, 'Rejected', FALSE, 'Needs Support', TRUE, 'A2', 'A2', FALSE, FALSE, FALSE, 'None', FALSE, FALSE, 'Interested in tech but need language support.', 'Spring 2026'),
-- Mehmet (ID: 5)
(5, 'Approved', TRUE, 'Stable', FALSE, 'B2', 'B2', TRUE, FALSE, TRUE, 'Basic SQL', TRUE, TRUE, 'To become a full-stack developer.', 'Fall 2026'),
-- Sara (ID: 6)
(6, 'Pending', TRUE, 'Stable', TRUE, 'B1', 'A2', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'Passionate about learning IT.', 'Spring 2026'),
-- Emre (ID: 7)
(7, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B1', TRUE, TRUE, TRUE, 'Cloud Computing basics', TRUE, TRUE, 'To work in the Dutch IT sector.', 'Fall 2026'),
-- Omar (ID: 8) - 2 Applications
(8, 'Rejected', FALSE, 'Needs Support', TRUE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'First attempt.', 'Fall 2025'),
(8, 'In Review', FALSE, 'Needs Support', TRUE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Looking for a new opportunity.', 'Spring 2026'),
-- Zeynep (ID: 9)
(9, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'B1', TRUE, TRUE, FALSE, 'Frontend basics', TRUE, TRUE, 'To build a career in web dev.', 'Fall 2026'),
-- Ali (ID: 10)
(10, 'Pending', FALSE, 'Needs Support', FALSE, 'B1', 'A2', FALSE, FALSE, TRUE, 'None', FALSE, TRUE, 'Need a fresh start.', 'Spring 2026'),
-- Mustafa (ID: 11)
(11, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'C1', TRUE, TRUE, TRUE, '3 years experience', TRUE, TRUE, 'To advance my current skills.', 'Fall 2026'),
-- Layla (ID: 12)
(12, 'In Review', TRUE, 'Stable', TRUE, 'B2', 'A1', FALSE, FALSE, FALSE, 'Basic HTML/CSS', FALSE, TRUE, 'Looking to join the tech field.', 'Fall 2026'),
-- Hussein (ID: 13)
(13, 'Rejected', FALSE, 'Needs Support', FALSE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, FALSE, 'Not ready for full-time.', 'Spring 2026'),
-- Büşra (ID: 14) - 3 Applications
(14, 'Rejected', FALSE, 'Needs Support', FALSE, 'B1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'First try.', 'Spring 2025'),
(14, 'Rejected', FALSE, 'Needs Support', FALSE, 'B1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Second try.', 'Fall 2025'),
(14, 'Approved', TRUE, 'Stable', TRUE, 'B1', 'A2', TRUE, FALSE, TRUE, 'Some Java', TRUE, TRUE, 'To find a job in IT.', 'Fall 2026'),
-- Yousef (ID: 15)
(15, 'Pending', TRUE, 'Stable', FALSE, 'B2', 'B1', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'To learn programming.', 'Spring 2026'),
-- Nour (ID: 16)
(16, 'Approved', TRUE, 'Stable', TRUE, 'C1', 'B2', TRUE, TRUE, TRUE, 'Data analysis basics', TRUE, TRUE, 'To become a data engineer.', 'Fall 2026'),
-- Can (ID: 17)
(17, 'In Review', FALSE, 'Needs Support', FALSE, 'B1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Looking for opportunities.', 'Spring 2026'),
-- Rania (ID: 18)
(18, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'A2', TRUE, FALSE, TRUE, 'Some C#', TRUE, TRUE, 'To switch careers to tech.', 'Fall 2026'),
-- Hasan (ID: 19)
(19, 'Rejected', FALSE, 'Needs Support', TRUE, 'A2', 'A2', FALSE, FALSE, FALSE, 'None', FALSE, FALSE, 'Need more language training first.', 'Spring 2026'),
-- Mariam (ID: 20)
(20, 'Pending', TRUE, 'Stable', FALSE, 'B1', 'B1', TRUE, TRUE, FALSE, 'None', FALSE, TRUE, 'To work in the IT industry.', 'Fall 2026'),
-- Yusuf (ID: 21)
(21, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'B1', TRUE, FALSE, TRUE, 'Basic Python', TRUE, TRUE, 'Career switch.', 'Fall 2026'),
-- Hiba (ID: 22)
(22, 'Pending', FALSE, 'Needs Support', TRUE, 'A2', 'A2', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Looking to learn.', 'Spring 2026'),
-- Kerem (ID: 23)
(23, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B2', TRUE, TRUE, TRUE, 'Full stack', TRUE, TRUE, 'Job ready.', 'Fall 2026'),
-- Dina (ID: 24)
(24, 'In Review', TRUE, 'Stable', TRUE, 'B1', 'A2', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'Interested.', 'Fall 2026'),
-- Baran (ID: 25)
(25, 'Approved', TRUE, 'Stable', FALSE, 'B2', 'A2', TRUE, FALSE, TRUE, 'Basic SQL', TRUE, TRUE, 'Work in NL.', 'Fall 2026'),
-- Salma (ID: 26)
(26, 'Rejected', FALSE, 'Needs Support', FALSE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, FALSE, 'Not suitable.', 'Spring 2026'),
-- Ozan (ID: 27)
(27, 'Pending', TRUE, 'Stable', TRUE, 'B1', 'A2', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'Learn IT.', 'Fall 2026'),
-- Yara (ID: 28)
(28, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B1', TRUE, TRUE, TRUE, '2 years exp', TRUE, TRUE, 'Career growth.', 'Fall 2026'),
-- Efe (ID: 29)
(29, 'In Review', FALSE, 'Needs Support', TRUE, 'B1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Need help.', 'Spring 2026'),
-- Amina (ID: 30)
(30, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'B2', TRUE, FALSE, TRUE, 'Basic JS', TRUE, TRUE, 'Full-time job.', 'Fall 2026'),
-- Trainees 31-45 (1 application each to keep it clean)
(31, 'Pending', TRUE, 'Needs Support', TRUE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Looking for a new career.', 'Spring 2027'),
(32, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'B1', TRUE, TRUE, TRUE, 'Basic C++', TRUE, TRUE, 'Passionate about tech.', 'Fall 2026'),
(33, 'In Review', FALSE, 'Stable', FALSE, 'B1', 'A2', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'Interested in IT.', 'Spring 2027'),
(34, 'Rejected', FALSE, 'Needs Support', TRUE, 'A1', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, FALSE, 'Need more time.', 'Spring 2026'),
(35, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B2', TRUE, TRUE, TRUE, '3 years as QA', TRUE, TRUE, 'Transition to dev.', 'Fall 2026'),
(36, 'Pending', TRUE, 'Stable', FALSE, 'B2', 'A2', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'Learn programming.', 'Fall 2026'),
(37, 'Approved', TRUE, 'Stable', TRUE, 'B2', 'B1', TRUE, TRUE, TRUE, 'Cloud basics', TRUE, TRUE, 'IT career.', 'Fall 2026'),
(38, 'Rejected', FALSE, 'Needs Support', FALSE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'First try.', 'Spring 2026'),
(39, 'Pending', TRUE, 'Stable', TRUE, 'B1', 'A2', TRUE, FALSE, FALSE, 'None', FALSE, TRUE, 'New opportunity.', 'Fall 2026'),
(40, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B2', TRUE, TRUE, TRUE, '5 years exp', TRUE, TRUE, 'Senior role.', 'Fall 2026'),
(41, 'Pending', FALSE, 'Needs Support', TRUE, 'A2', 'A2', FALSE, FALSE, FALSE, 'None', FALSE, TRUE, 'Career change.', 'Spring 2026'),
(42, 'Approved', TRUE, 'Stable', FALSE, 'B2', 'B1', TRUE, FALSE, TRUE, 'Basic Networking', TRUE, TRUE, 'IT Support.', 'Fall 2026'),
(43, 'In Review', TRUE, 'Stable', TRUE, 'B1', 'A2', TRUE, TRUE, FALSE, 'None', FALSE, TRUE, 'Web dev.', 'Spring 2027'),
(44, 'Rejected', FALSE, 'Needs Support', TRUE, 'A2', 'A1', FALSE, FALSE, FALSE, 'None', FALSE, FALSE, 'Need language skills.', 'Fall 2025'),
(45, 'Approved', TRUE, 'Stable', FALSE, 'C1', 'B1', TRUE, TRUE, TRUE, 'Junior Dev', TRUE, TRUE, 'Ready to work.', 'Fall 2026');

-- ==========================================
-- 3. Insert Mentors (Multiple meetings for some trainees)
-- ==========================================
INSERT INTO Mentors 
(MeetingDate, MentorFullName, TraineeID, HasRelevantKnowledge, EligibleForVITProject, Thoughts, AvailabilityStatus, Comments) 
VALUES
-- Ahmet (ID: 1) - 3 meetings
('2026-01-10', 'Jan de Vries', 1, FALSE, FALSE, 'Needs more time.', 'Busy', 'Follow up.'),
('2026-06-15', 'Sara Ahmed', 1, TRUE, TRUE, 'Improved a lot.', 'Available', 'Eligible.'),
('2026-09-01', 'Omar Khaled', 1, TRUE, TRUE, 'Excellent progress.', 'Available', 'Ready.'),
-- Ayşe (ID: 2) - 2 meetings
('2026-02-20', 'Ahmet Yılmaz', 2, FALSE, FALSE, 'Language issue.', 'Available', 'Hold.'),
('2026-08-10', 'Fatima Al-Zahra', 2, TRUE, FALSE, 'Better but still needs work.', 'Busy', 'Pending.'),
-- Mohammed (ID: 3) - 2 meetings
('2026-03-15', 'Jan de Vries', 3, TRUE, TRUE, 'Strong technical skills.', 'Available', 'ITPH ready.'),
('2026-09-01', 'Sara Ahmed', 3, TRUE, TRUE, 'Continues to impress.', 'Available', 'Recommend for advanced.'),
-- Fatima (ID: 4)
('2026-10-04', 'Fatima Al-Zahra', 4, FALSE, FALSE, 'Language barrier is an issue.', 'Unavailable', 'Not recommended at this time.'),
-- Mehmet (ID: 5) - 2 meetings
('2026-02-10', 'Mehmet Kaya', 5, TRUE, TRUE, 'Good problem-solving skills.', 'Available', 'Can start immediately.'),
('2026-09-15', 'Ahmet Yılmaz', 5, TRUE, TRUE, 'Ready for next challenge.', 'Available', 'Accept.'),
-- Sara (ID: 6)
('2026-10-06', 'Sara Ahmed', 6, TRUE, TRUE, 'Eager to learn and highly motivated.', 'Available', 'Recommended for the next term.'),
-- Emre (ID: 7)
('2026-10-07', 'Emre Çelik', 7, TRUE, TRUE, 'Excellent profile, very proactive.', 'Available', 'Fast-track to the project.'),
-- Omar (ID: 8) - 2 meetings
('2025-11-05', 'Omar Khaled', 8, FALSE, FALSE, 'Still exploring options.', 'Busy', 'Needs career counselling first.'),
('2026-04-12', 'Jan de Vries', 8, FALSE, FALSE, 'Still not ready.', 'Unavailable', 'Deny.'),
-- Zeynep (ID: 9)
('2026-10-09', 'Zeynep Şahin', 9, TRUE, TRUE, 'Solid understanding of basics.', 'Available', 'Ready to start.'),
-- Ali (ID: 10)
('2026-10-10', 'Ali Hassan', 10, FALSE, TRUE, 'Needs to improve English.', 'Busy', 'Join next term.'),
-- Mustafa (ID: 11)
('2026-10-11', 'Mustafa Yıldız', 11, TRUE, TRUE, 'Highly experienced, great addition.', 'Available', 'Assign immediately.'),
-- Layla (ID: 12)
('2026-10-12', 'Layla Mahmoud', 12, TRUE, TRUE, 'Good potential.', 'Available', 'Recommended.'),
-- Hussein (ID: 13)
('2026-10-13', 'Hussein Al-Sayed', 13, FALSE, FALSE, 'Not ready yet.', 'Unavailable', 'Try again next year.'),
-- Büşra (ID: 14) - 3 meetings
('2025-09-01', 'Büşra Öztürk', 14, FALSE, FALSE, 'Needs time.', 'Busy', 'Defer.'),
('2026-02-01', 'Büşra Öztürk', 14, FALSE, FALSE, 'Still needs time.', 'Busy', 'Wait.'),
('2026-05-20', 'Can Aydın', 14, TRUE, TRUE, 'Great improvement.', 'Available', 'Accept.'),
-- Yousef (ID: 15)
('2026-10-15', 'Yousef Ibrahim', 15, FALSE, TRUE, 'Good motivation, needs technical training.', 'Busy', 'Pending review.'),
-- Nour (ID: 16)
('2026-10-16', 'Nour Al-Huda', 16, TRUE, TRUE, 'Excellent skills.', 'Available', 'Direct to ITPH.'),
-- Can (ID: 17)
('2026-10-17', 'Can Aydın', 17, FALSE, FALSE, 'Not suitable at the moment.', 'Unavailable', 'Rejected.'),
-- Rania (ID: 18)
('2026-10-18', 'Rania Kamal', 18, TRUE, TRUE, 'Very good technical background.', 'Available', 'Accept.'),
-- Hasan (ID: 19)
('2026-10-19', 'Hasan Arslan', 19, FALSE, FALSE, 'Needs more time.', 'Busy', 'Deferred.'),
-- Mariam (ID: 20)
('2026-10-20', 'Mariam Saleh', 20, TRUE, TRUE, 'Ready for the project.', 'Available', 'Accept.'),
-- Yusuf (ID: 21) - 2 meetings
('2026-03-10', 'Yusuf Aydın', 21, TRUE, FALSE, 'Good but needs English.', 'Available', 'Hold.'),
('2026-09-15', 'Kerem Koç', 21, TRUE, TRUE, 'English improved.', 'Available', 'Go.'),
-- Hiba (ID: 22)
('2026-10-22', 'Hiba Tariq', 22, FALSE, FALSE, 'Language barrier.', 'Busy', 'Defer.'),
-- Kerem (ID: 23)
('2026-10-23', 'Kerem Koç', 23, TRUE, TRUE, 'Job ready.', 'Available', 'Hire.'),
-- Dina (ID: 24)
('2026-10-24', 'Dina Samir', 24, TRUE, TRUE, 'Interested.', 'Available', 'Accept.'),
-- Baran (ID: 25)
('2026-10-25', 'Baran Tekin', 25, TRUE, TRUE, 'Good SQL.', 'Available', 'Ready.'),
-- Salma (ID: 26)
('2026-10-26', 'Salma Nabil', 26, FALSE, FALSE, 'Not suitable.', 'Unavailable', 'Reject.'),
-- Ozan (ID: 27)
('2026-10-27', 'Ozan Yılmaz', 27, TRUE, FALSE, 'Needs practice.', 'Busy', 'Wait.'),
-- Yara (ID: 28)
('2026-10-28', 'Yara Haddad', 28, TRUE, TRUE, 'Experienced.', 'Available', 'Ready.'),
-- Efe (ID: 29)
('2026-10-29', 'Efe Demir', 29, FALSE, FALSE, 'Needs time.', 'Unavailable', 'Deny.'),
-- Amina (ID: 30)
('2026-10-30', 'Amina Yusuf', 30, TRUE, TRUE, 'Ready.', 'Available', 'Accept.'),
-- Trainees 31-45 (1 meeting each)
('2026-11-01', 'Jan de Vries', 31, FALSE, FALSE, 'Needs time to adapt.', 'Busy', 'Follow up in 3 months.'),
('2026-11-02', 'Sara Ahmed', 32, TRUE, TRUE, 'Strong logical thinking.', 'Available', 'Assign to frontend team.'),
('2026-11-03', 'Omar Khaled', 33, TRUE, FALSE, 'Good communicator.', 'Available', 'Ready for interview.'),
('2026-11-04', 'Fatima Al-Zahra', 34, FALSE, FALSE, 'Language barrier.', 'Unavailable', 'Not ready.'),
('2026-11-05', 'Mehmet Kaya', 35, TRUE, TRUE, 'Experienced, needs modern stack.', 'Available', 'Fast-track to ITPH.'),
('2026-11-06', 'Zeynep Şahin', 36, TRUE, TRUE, 'Eager to learn.', 'Available', 'Recommend.'),
('2026-11-07', 'Ali Hassan', 37, TRUE, TRUE, 'Solid background.', 'Available', 'Accept.'),
('2026-11-08', 'Hussein Al-Sayed', 38, FALSE, FALSE, 'Still exploring.', 'Busy', 'Defer.'),
('2026-11-09', 'Layla Mahmoud', 39, TRUE, FALSE, 'Needs technical training.', 'Available', 'Conditional accept.'),
('2026-11-10', 'Mustafa Yıldız', 40, TRUE, TRUE, 'Excellent profile.', 'Available', 'Hire immediately.'),
('2026-11-11', 'Ahmet Yılmaz', 41, FALSE, TRUE, 'Motivated but needs basics.', 'Available', 'Review.'),
('2026-11-12', 'Sara Ahmed', 42, TRUE, TRUE, 'Good background.', 'Available', 'Accept.'),
('2026-11-13', 'Jan de Vries', 43, TRUE, TRUE, 'Strong candidate.', 'Busy', 'Pending.'),
('2026-11-14', 'Fatima Al-Zahra', 44, FALSE, FALSE, 'Not ready yet.', 'Unavailable', 'Reject.'),
('2026-11-15', 'Omar Khaled', 45, TRUE, TRUE, 'Ready to go.', 'Available', 'Accept.');

-- ==========================================
-- 4. Insert Users (Standalone)
-- ==========================================
INSERT INTO Users (Username, Password, Role) VALUES
('admin_waseem', 'hashed_password_123', 'Admin'),
('mentor_jan', 'hashed_password_456', 'Mentor'),
('coordinator_dana', 'hashed_password_789', 'Admin'),
('user_ahmet', 'hashed_password_101', 'User'),
('user_fatima', 'hashed_password_202', 'User'),
('admin_dana', 'hashed_456', 'Admin'),
('mentor_sara', 'hashed_101', 'Mentor'),
('user_mehmet', 'hashed_104', 'User'),
('user_omar', 'hashed_105', 'User'),
('user_zeynep', 'hashed_106', 'User'),
('mentor_omar', 'hashed_201', 'Mentor'),
('user_bilal', 'hashed_202', 'User'),
('user_lina', 'hashed_203', 'User'),
('user_kaan', 'hashed_204', 'User'),
('admin_reem', 'hashed_205', 'Admin');

-- ==========================================
-- 5. Insert ProjectTracking (Multiple projects for some trainees)
-- ==========================================
INSERT INTO ProjectTracking (TraineeID, ProjectSubmissionDate, ProjectReviewDate) VALUES
-- Ahmet (ID: 1) - 3 projects
(1, '2026-01-01', '2026-01-05'),
(1, '2026-06-01', '2026-06-05'),
(1, '2026-11-01', '2026-11-05'),
-- Ayşe (ID: 2) - 2 projects
(2, '2026-03-01', '2026-03-05'),
(2, '2026-09-01', '2026-09-05'),
-- Mohammed (ID: 3) - 4 projects
(3, '2025-10-01', '2025-10-05'),
(3, '2026-02-01', '2026-02-05'),
(3, '2026-06-01', '2026-06-05'),
(3, '2026-10-01', '2026-10-05'),
-- Fatima (ID: 4) - 1 project
(4, '2026-09-01', '2026-09-06'),
-- Mehmet (ID: 5) - 2 projects
(5, '2026-02-01', '2026-02-05'),
(5, '2026-09-01', '2026-09-05'),
-- Sara (ID: 6)
(6, '2026-10-02', '2026-10-06'),
-- Emre (ID: 7)
(7, '2026-09-25', '2026-09-28'),
-- Omar (ID: 8)
(8, '2026-09-28', '2026-10-02'),
-- Zeynep (ID: 9)
(9, '2026-10-01', '2026-10-05'),
-- Ali (ID: 10)
(10, '2026-10-05', '2026-10-10'),
-- Mustafa (ID: 11)
(11, '2026-02-15', '2026-02-20'),
(11, '2026-08-15', '2026-08-20'),
-- Layla (ID: 12)
(12, '2026-09-10', '2026-09-15'),
-- Hussein (ID: 13)
(13, '2026-09-12', '2026-09-17'),
-- Büşra (ID: 14) - 2 projects
(14, '2026-03-01', '2026-03-05'),
(14, '2026-09-20', '2026-09-25'),
-- Yousef (ID: 15)
(15, '2026-10-10', '2026-10-15'),
-- Nour (ID: 16)
(16, '2026-08-05', '2026-08-10'),
-- Can (ID: 17)
(17, '2026-09-18', '2026-09-23'),
-- Rania (ID: 18)
(18, '2026-09-25', '2026-09-30'),
-- Hasan (ID: 19)
(19, '2026-09-28', '2026-10-03'),
-- Mariam (ID: 20)
(20, '2026-10-02', '2026-10-07'),
-- Yusuf (ID: 21)
(21, '2026-07-01', '2026-07-06'),
-- Hiba (ID: 22)
(22, '2026-09-05', '2026-09-10'),
-- Kerem (ID: 23)
(23, '2026-08-25', '2026-08-30'),
-- Dina (ID: 24)
(24, '2026-09-15', '2026-09-20'),
-- Baran (ID: 25)
(25, '2026-10-01', '2026-10-06'),
-- Salma (ID: 26)
(26, '2026-09-22', '2026-09-27'),
-- Ozan (ID: 27)
(27, '2026-09-25', '2026-09-30'),
-- Yara (ID: 28)
(28, '2026-08-10', '2026-08-15'),
-- Efe (ID: 29)
(29, '2026-09-30', '2026-10-05'),
-- Amina (ID: 30)
(30, '2026-10-05', '2026-10-10'),
-- Trainees 31-45 (1 project each)
(31, '2026-09-01', '2026-09-05'),
(32, '2026-09-05', '2026-09-10'),
(33, '2026-09-10', '2026-09-15'),
(34, '2026-09-12', '2026-09-17'),
(35, '2026-08-20', '2026-08-25'),
(36, '2026-09-18', '2026-09-23'),
(37, '2026-09-15', '2026-09-20'),
(38, '2026-09-20', '2026-09-25'),
(39, '2026-09-25', '2026-09-30'),
(40, '2026-09-28', '2026-10-02'),
(41, '2026-09-30', '2026-10-04'),
(42, '2026-09-01', '2026-09-05'),
(43, '2026-09-10', '2026-09-15'),
(44, '2026-09-14', '2026-09-19'),
(45, '2026-09-20', '2026-09-25');
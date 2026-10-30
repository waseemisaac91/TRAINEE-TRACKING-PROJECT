--1
SELECT 
    t.FullName,
    COUNT(a.ApplicationID) AS Total_Applications
FROM Trainees t
JOIN Applications a ON t.TraineeID = a.TraineeID
GROUP BY  t.FullName
ORDER BY Total_Applications DESC;

---2
SELECT 
    m.MentorFullName,
    COUNT(m.MentorID) AS Total_Meetings
FROM Mentors m
JOIN Trainees t ON m.TraineeID = t.TraineeID
GROUP BY m.MentorFullName
ORDER BY Total_Meetings DESC;

--3
SELECT 
    t.FullName,
    COUNT(p.ProjectTrackingID) AS Total_Projects_Submitted
FROM Trainees t
JOIN ProjectTracking p ON t.TraineeID = p.TraineeID
GROUP BY t.TraineeID, t.FullName
ORDER BY Total_Projects_Submitted DESC;

--4


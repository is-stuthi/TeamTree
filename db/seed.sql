-- =========================================================
-- Seed data. Every demo login uses the password "password123"
-- (migrate.py substitutes its bcrypt hash for ${SEED_PASSWORD_HASH}).
-- Explicit ids keep tests deterministic. Dates are relative to today.
--
-- Built-in demo situations:
--   P1  Plant Disease Classifier  Open, ML text for vector search
--   P3  Smart Inventory Tracker   Open, skill gap (Docker), Jay (11) fully qualified, not applied
--   P4  Portfolio Generator       Ongoing, 3-level subtask tree, Kavya left (membership history)
--   P5  Hackathon Team Finder     Open but FULL (3/3) with a pending application
--   P8  Accessibility Auditor     Open, zero applications
--   User 15 is deactivated. Users 1 and 14 are admins.
-- =========================================================
USE teamtree;

-- ---------------- Users ----------------
INSERT INTO Users (id, f_name, m_name, l_name, email, password_hash, role, bio, location,
                   experience_level, availability, is_active, created_at) VALUES
(1,  'Admin',  NULL, 'User',    'admin@teamtree.dev',  '${SEED_PASSWORD_HASH}', 'admin',  'Platform administrator.', 'Bengaluru', 'Expert', 'Full-time', TRUE, NOW() - INTERVAL 120 DAY),
(2,  'Alice',  NULL, 'Rao',     'alice@teamtree.dev',  '${SEED_PASSWORD_HASH}', 'member', 'ML engineer who loves computer vision and agritech.', 'Bengaluru', 'Advanced', 'Full-time', TRUE, NOW() - INTERVAL 110 DAY),
(3,  'Bob',    NULL, 'Mehta',   'bob@teamtree.dev',    '${SEED_PASSWORD_HASH}', 'member', 'Full-stack web developer, Node and React.', 'Mysuru', 'Intermediate', 'Part-time', TRUE, NOW() - INTERVAL 100 DAY),
(4,  'Chitra', NULL, 'Iyer',    'chitra@teamtree.dev', '${SEED_PASSWORD_HASH}', 'member', 'Backend developer interested in IoT and logistics.', 'Chennai', 'Advanced', 'Part-time', TRUE, NOW() - INTERVAL 98 DAY),
(5,  'Dev',    NULL, 'Nair',    'dev@teamtree.dev',    '${SEED_PASSWORD_HASH}', 'member', 'Open source maintainer, TypeScript and Next.js.', 'Kochi', 'Expert', 'Weekends', TRUE, NOW() - INTERVAL 95 DAY),
(6,  'Esha',   NULL, 'Kulkarni','esha@teamtree.dev',   '${SEED_PASSWORD_HASH}', 'member', 'First-year student learning Python and design.', 'Pune', 'Beginner', 'Full-time', TRUE, NOW() - INTERVAL 90 DAY),
(7,  'Farhan', NULL, 'Ali',     'farhan@teamtree.dev', '${SEED_PASSWORD_HASH}', 'member', 'Frontend developer, React and graph databases.', 'Hyderabad', 'Intermediate', 'Full-time', TRUE, NOW() - INTERVAL 88 DAY),
(8,  'Gauri',  NULL, 'Shetty',  'gauri@teamtree.dev',  '${SEED_PASSWORD_HASH}', 'member', 'Mobile and web developer building wellbeing apps.', 'Mangaluru', 'Advanced', 'Part-time', TRUE, NOW() - INTERVAL 85 DAY),
(9,  'Harsh',  NULL, 'Patil',   'harsh@teamtree.dev',  '${SEED_PASSWORD_HASH}', 'member', 'DevOps enthusiast, CI pipelines and Linux.', 'Nashik', 'Intermediate', 'Weekends', TRUE, NOW() - INTERVAL 80 DAY),
(10, 'Isha',   NULL, 'Reddy',   'isha@teamtree.dev',   '${SEED_PASSWORD_HASH}', 'member', 'UI/UX designer exploring frontend.', 'Vizag', 'Beginner', 'Part-time', TRUE, NOW() - INTERVAL 75 DAY),
(11, 'Jay',    NULL, 'Kumar',   'jay@teamtree.dev',    '${SEED_PASSWORD_HASH}', 'member', 'Cloud engineer: Docker, Kubernetes, AWS, Python.', 'Bengaluru', 'Expert', 'Full-time', TRUE, NOW() - INTERVAL 70 DAY),
(12, 'Kavya',  NULL, 'Menon',   'kavya@teamtree.dev',  '${SEED_PASSWORD_HASH}', 'member', 'Data analyst, currently busy with exams.', 'Thrissur', 'Intermediate', 'Unavailable', TRUE, NOW() - INTERVAL 65 DAY),
(13, 'Liam',   NULL, 'Dsouza',  'liam@teamtree.dev',   '${SEED_PASSWORD_HASH}', 'member', 'Security researcher and data science hobbyist.', 'Goa', 'Advanced', 'Full-time', TRUE, NOW() - INTERVAL 60 DAY),
(14, 'Meera',  NULL, 'Joshi',   'meera@teamtree.dev',  '${SEED_PASSWORD_HASH}', 'admin',  'Accessibility advocate and product manager.', 'Mumbai', 'Advanced', 'Part-time', TRUE, NOW() - INTERVAL 58 DAY),
(15, 'Nikhil', NULL, 'Bhat',    'nikhil@teamtree.dev', '${SEED_PASSWORD_HASH}', 'member', 'Deactivated demo account.', 'Udupi', 'Beginner', 'Weekends', FALSE, NOW() - INTERVAL 50 DAY);

-- ---------------- Skills (25 in 5 categories) ----------------
INSERT INTO Skill (s_id, s_name, category) VALUES
(1,'Python','Programming'),(2,'Java','Programming'),(3,'C++','Programming'),(4,'Go','Programming'),(5,'TypeScript','Programming'),
(6,'React','Web'),(7,'Next.js','Web'),(8,'Node.js','Web'),(9,'HTML/CSS','Web'),(10,'GraphQL','Web'),
(11,'SQL','Data'),(12,'Machine Learning','Data'),(13,'Data Analysis','Data'),(14,'Deep Learning','Data'),(15,'Neo4j','Data'),
(16,'Docker','DevOps & Security'),(17,'Kubernetes','DevOps & Security'),(18,'AWS','DevOps & Security'),(19,'Linux','DevOps & Security'),(20,'Cybersecurity','DevOps & Security'),
(21,'UI/UX','Design & Product'),(22,'Figma','Design & Product'),(23,'Technical Writing','Design & Product'),(24,'Product Management','Design & Product'),(25,'User Research','Design & Product');

-- ---------------- User skills ----------------
INSERT INTO user_has_skill (u_id, s_id, u_s_level) VALUES
(1,1,'Expert'),(1,11,'Expert'),(1,19,'Advanced'),
(2,1,'Expert'),(2,12,'Advanced'),(2,14,'Advanced'),(2,13,'Intermediate'),(2,6,'Beginner'),
(3,6,'Intermediate'),(3,8,'Intermediate'),(3,11,'Beginner'),(3,5,'Intermediate'),(3,9,'Advanced'),
(4,1,'Advanced'),(4,11,'Advanced'),(4,2,'Intermediate'),(4,13,'Intermediate'),
(5,5,'Expert'),(5,7,'Expert'),(5,6,'Advanced'),(5,23,'Advanced'),(5,8,'Advanced'),
(6,1,'Beginner'),(6,21,'Beginner'),(6,22,'Beginner'),
(7,6,'Intermediate'),(7,15,'Intermediate'),(7,16,'Beginner'),(7,5,'Intermediate'),
(8,5,'Advanced'),(8,6,'Advanced'),(8,7,'Intermediate'),(8,21,'Intermediate'),
(9,16,'Intermediate'),(9,19,'Advanced'),(9,7,'Beginner'),(9,23,'Beginner'),
(10,21,'Intermediate'),(10,22,'Advanced'),(10,9,'Intermediate'),(10,15,'Beginner'),
(11,1,'Expert'),(11,16,'Expert'),(11,17,'Expert'),(11,18,'Advanced'),(11,6,'Advanced'),
(12,13,'Advanced'),(12,11,'Intermediate'),(12,1,'Intermediate'),
(13,20,'Advanced'),(13,19,'Advanced'),(13,13,'Advanced'),(13,1,'Advanced'),(13,11,'Intermediate'),
(14,21,'Advanced'),(14,24,'Expert'),(14,25,'Advanced'),(14,9,'Intermediate'),
(15,1,'Beginner');

-- ---------------- Projects (inserted Open; final statuses set at the end) ----------------
INSERT INTO Project (p_id, owner_id, p_name, description, deadline, status, max_team_size, creation_date) VALUES
(1, 2, 'Plant Disease Classifier',
    'A machine learning image classifier that detects crop leaf diseases from smartphone photos, helping farmers act early. Deep learning model with a simple React upload interface.',
    CURDATE() + INTERVAL 60 DAY, 'Open', 5, NOW() - INTERVAL 40 DAY),
(2, 3, 'Campus Event Hub',
    'A web app where college clubs publish events and students RSVP. Node.js backend, React frontend and a clean, friendly UI.',
    CURDATE() + INTERVAL 45 DAY, 'Open', 4, NOW() - INTERVAL 35 DAY),
(3, 4, 'Smart Inventory Tracker',
    'Barcode-based inventory tracking for small shops with containerised deployment. Python backend, React dashboard, deployed with Docker.',
    CURDATE() + INTERVAL 50 DAY, 'Open', 4, NOW() - INTERVAL 33 DAY),
(4, 5, 'Developer Portfolio Generator',
    'Generate a polished developer portfolio website from a GitHub profile and markdown files. Next.js static export with themes.',
    CURDATE() + INTERVAL 30 DAY, 'Open', NULL, NOW() - INTERVAL 60 DAY),
(5, 7, 'Hackathon Team Finder',
    'Match hackathon participants into balanced teams using a graph of skills and past collaborations stored in Neo4j.',
    CURDATE() + INTERVAL 20 DAY, 'Open', 3, NOW() - INTERVAL 30 DAY),
(6, 8, 'Mental Health Journal App',
    'A private journaling app with mood tracking charts and gentle reminders to support student wellbeing.',
    CURDATE() - INTERVAL 10 DAY, 'Open', 4, NOW() - INTERVAL 90 DAY),
(7, 11, 'Kubernetes Cost Dashboard',
    'Visualise per-namespace cloud spend for Kubernetes clusters on AWS.',
    CURDATE() + INTERVAL 15 DAY, 'Open', 3, NOW() - INTERVAL 70 DAY),
(8, 14, 'Accessibility Auditor',
    'A browser tool that audits web pages for accessibility issues and suggests fixes for colour contrast, alt text and keyboard navigation.',
    CURDATE() + INTERVAL 40 DAY, 'Open', 3, NOW() - INTERVAL 12 DAY),
(9, 2, 'Bus Route Optimizer',
    'Analyse city bus GPS and ticketing data to suggest better routes and timings. Data analysis, clustering and a SQL warehouse.',
    CURDATE() + INTERVAL 25 DAY, 'Open', 4, NOW() - INTERVAL 55 DAY),
(10, 13, 'Cyber Range for Students',
    'A sandboxed lab of vulnerable containers where students practise ethical hacking and defensive security.',
    CURDATE() + INTERVAL 70 DAY, 'Open', 5, NOW() - INTERVAL 20 DAY);

INSERT INTO Domain (project_id, d_name) VALUES
(1,'Machine Learning'),(1,'Agriculture'),(2,'Web'),(2,'Education'),(3,'Logistics'),(3,'IoT'),
(4,'Web'),(4,'Developer Tools'),(5,'Social'),(5,'Web'),(6,'Health'),(6,'Mobile'),
(7,'Cloud'),(7,'DevOps'),(8,'Web'),(8,'Accessibility'),(9,'Transport'),(9,'Data Science'),
(10,'Security'),(10,'Education');

INSERT INTO Requires (p_id, s_id, req_role, p_s_level, req_count) VALUES
(1,1,'ML Engineer','Advanced',1),(1,14,'ML Engineer','Intermediate',1),(1,6,'Frontend Developer','Intermediate',1),
(2,6,'Frontend Developer','Intermediate',1),(2,8,'Backend Developer','Intermediate',1),(2,11,'Backend Developer','Beginner',1),(2,21,'Designer','Beginner',1),
(3,16,'DevOps Engineer','Advanced',1),(3,1,'Backend Developer','Intermediate',1),(3,6,'Frontend Developer','Intermediate',1),
(4,7,'Frontend Developer','Advanced',1),(4,5,'Frontend Developer','Intermediate',2),(4,23,'Docs Writer','Beginner',1),
(5,15,'Graph Developer','Intermediate',1),(5,1,'Backend Developer','Beginner',1),
(6,6,'Frontend Developer','Advanced',1),(6,21,'Designer','Intermediate',1),
(7,17,'Cloud Engineer','Advanced',1),(7,18,'Cloud Engineer','Intermediate',1),
(8,21,'Designer','Advanced',1),(8,9,'Frontend Developer','Intermediate',1),
(9,13,'Data Analyst','Advanced',1),(9,1,'Data Engineer','Advanced',1),(9,11,'Data Engineer','Intermediate',1),
(10,20,'Security Engineer','Advanced',1),(10,19,'Security Engineer','Intermediate',1),(10,16,'DevOps Engineer','Intermediate',1);

-- ---------------- Teams + owner memberships ----------------
INSERT INTO Team (t_id, p_id, team_name, create_date)
SELECT p_id, p_id, LEFT(CONCAT(p_name, ' Team'), 150), creation_date FROM Project;

INSERT INTO Joins (t_id, u_id, role, join_date)
SELECT p_id, owner_id, 'Owner', DATE(creation_date) FROM Project;

-- ---------------- Applications (before member joins, so capacity checks pass) ----------------
INSERT INTO Application (a_id, applicant_id, p_id, msg, status, a_date, decision_date) VALUES
(1,  6, 1, 'I am learning Python and would love to help label the dataset.', 'Pending',  NOW() - INTERVAL 3 DAY,  NULL),
(2,  7, 1, 'I can build the React upload interface.',                       'Rejected', NOW() - INTERVAL 20 DAY, NOW() - INTERVAL 18 DAY),
(3, 11, 1, 'Happy to containerise the model serving.',                     'Withdrawn',NOW() - INTERVAL 15 DAY, NULL),
(4,  9, 2, 'I can set up CI and deployment for the hub.',                   'Pending',  NOW() - INTERVAL 5 DAY,  NULL),
(5, 10, 2, 'I would like to design the event cards and RSVP flow.',         'Pending',  NOW() - INTERVAL 2 DAY,  NULL),
(6,  7, 3, 'Frontend dev, comfortable with React dashboards.',              'Accepted', NOW() - INTERVAL 28 DAY, NOW() - INTERVAL 27 DAY),
(7, 12, 3, 'Interested in the inventory analytics.',                        'Rejected', NOW() - INTERVAL 25 DAY, NOW() - INTERVAL 24 DAY),
(8,  8, 4, 'I have built several Next.js sites with theming.',              'Accepted', NOW() - INTERVAL 55 DAY, NOW() - INTERVAL 54 DAY),
(9,  9, 4, 'I can own the deployment pipeline.',                            'Accepted', NOW() - INTERVAL 54 DAY, NOW() - INTERVAL 53 DAY),
(10, 6, 5, 'I want to learn graph databases on a real project.',            'Accepted', NOW() - INTERVAL 26 DAY, NOW() - INTERVAL 25 DAY),
(11, 3, 5, 'Backend help for the matching service.',                        'Accepted', NOW() - INTERVAL 24 DAY, NOW() - INTERVAL 23 DAY),
(12,10, 5, 'I can design the team cards.',                                  'Pending',  NOW() - INTERVAL 27 DAY, NULL),
(13, 2, 6, 'I can help with the mood chart.',                               'Accepted', NOW() - INTERVAL 85 DAY, NOW() - INTERVAL 84 DAY),
(14,12, 6, 'Data analyst, can build the insights page.',                    'Accepted', NOW() - INTERVAL 84 DAY, NOW() - INTERVAL 83 DAY),
(15, 4, 9, 'Strong SQL and Python, keen on transport data.',                'Accepted', NOW() - INTERVAL 50 DAY, NOW() - INTERVAL 49 DAY),
(16,13, 9, 'I can handle route clustering.',                                'Accepted', NOW() - INTERVAL 49 DAY, NOW() - INTERVAL 48 DAY),
(17, 5,10, 'Can help build the lab orchestration.',                         'Pending',  NOW() - INTERVAL 1 DAY,  NULL),
(18, 3,10, 'Interested in security.',                                       'Rejected', NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 8 DAY),
(19, 6, 2, 'Applying to help with design.',                                 'Withdrawn',NOW() - INTERVAL 12 DAY, NULL),
(20, 4, 7, 'Can help with the AWS billing API.',                            'Accepted', NOW() - INTERVAL 65 DAY, NOW() - INTERVAL 64 DAY),
(21,12, 4, 'Can write docs.',                                               'Accepted', NOW() - INTERVAL 52 DAY, NOW() - INTERVAL 51 DAY);

-- ---------------- Member joins (from accepted applications) ----------------
INSERT INTO Joins (t_id, u_id, role, join_date)
SELECT a.p_id, a.applicant_id,
       CASE a.a_id WHEN 6 THEN 'Frontend Developer' WHEN 8 THEN 'Frontend Developer'
                   WHEN 9 THEN 'DevOps Engineer'   WHEN 10 THEN 'Graph Developer'
                   WHEN 11 THEN 'Backend Developer' WHEN 15 THEN 'Data Engineer'
                   WHEN 16 THEN 'Data Analyst'     WHEN 21 THEN 'Docs Writer' ELSE 'Member' END,
       DATE(a.decision_date)
FROM Application a WHERE a.status = 'Accepted';

-- Kavya left P4 (history is kept)
UPDATE Joins SET leave_date = CURDATE() - INTERVAL 20 DAY WHERE t_id = 4 AND u_id = 12;

-- ---------------- Tasks ----------------
INSERT INTO Task (task_id, p_id, u_id, parent_task_id, t_name, description, status, priority, due_date) VALUES
(1, 4, 5,    NULL, 'Build MVP',            'First usable version of the generator.', 'In Progress', 'High',     CURDATE() + INTERVAL 25 DAY),
(2, 4, 8,    1,    'Template engine',      'Render pages from markdown + theme.',    'In Progress', 'High',     CURDATE() + INTERVAL 15 DAY),
(3, 4, 8,    2,    'Markdown parser',      'Parse front matter and content.',        'Done',        'Medium',   CURDATE() - INTERVAL 5 DAY),
(4, 4, 9,    2,    'Theme system',         'Pluggable colour/typography themes.',    'To Do',       'Medium',   CURDATE() + INTERVAL 12 DAY),
(5, 4, 9,    1,    'Deploy pipeline',      'Static export + CI deploy.',             'Blocked',     'Critical', CURDATE() + INTERVAL 20 DAY),
(6, 4, 5,    NULL, 'Write docs',           'README and usage guide.',                'To Do',       'Low',      CURDATE() + INTERVAL 28 DAY),
(7, 9, 2,    NULL, 'Collect GTFS data',    'Download and clean city feeds.',         'Done',        'High',     CURDATE() - INTERVAL 30 DAY),
(8, 9, 13,   NULL, 'Route clustering',     'Cluster stops by demand.',               'In Progress', 'High',     CURDATE() + INTERVAL 10 DAY),
(9, 9, 4,    NULL, 'Warehouse schema',     'SQL schema for trips and tickets.',      'To Do',       'Medium',   CURDATE() - INTERVAL 2 DAY),
(10,6, 8,    NULL, 'Journal editor',       'Rich text editor for entries.',          'Done',        'High',     CURDATE() - INTERVAL 40 DAY),
(11,6, 2,    NULL, 'Mood chart',           'Weekly mood visualisation.',             'Done',        'Medium',   CURDATE() - INTERVAL 30 DAY),
(12,6, 12,   NULL, 'Reminders',            'Gentle daily reminders.',                'Done',        'Low',      CURDATE() - INTERVAL 20 DAY),
(13,3, 4,    NULL, 'Set up repository',    'Repo, linting, CI skeleton.',            'Done',        'Medium',   CURDATE() - INTERVAL 20 DAY),
(14,3, 7,    NULL, 'Barcode scanner UI',   'Camera-based scanning screen.',          'In Progress', 'High',     CURDATE() + INTERVAL 14 DAY),
(15,3, NULL, NULL, 'Containerise services','Dockerfiles + compose for deployment.',  'To Do',       'High',     CURDATE() + INTERVAL 30 DAY),
(16,5, 7,    NULL, 'Graph model',          'Design the skill/collaboration graph.',  'Done',        'High',     CURDATE() - INTERVAL 10 DAY),
(17,5, 6,    NULL, 'Signup form',          'Collect participant skills.',            'In Progress', 'Medium',   CURDATE() + INTERVAL 7 DAY);

-- ---------------- Final project statuses ----------------
UPDATE Project SET status = 'Ongoing'   WHERE p_id IN (4, 9);
UPDATE Project SET status = 'Completed' WHERE p_id = 6;
UPDATE Project SET status = 'Closed'    WHERE p_id = 7;

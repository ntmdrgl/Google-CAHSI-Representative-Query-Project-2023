use artifactdb;

-- Create Tables 

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(32) NOT NULL,
    last_name VARCHAR(32) NOT NULL,
    birthday DATE
);


CREATE TABLE education (
    education_id INT PRIMARY KEY,
    education_name VARCHAR(32) NOT NULL,
    degree ENUM('Associate', 'Bachelor', 'Graduate', 'Professional', 'Doctoral'),
    field_of_study ENUM('Computer Science', 'Computer Engineering'),
    cs_focus SET('Software Engineering', 'Artificial Intelligence', 'Web Developer', 'Cybersecurity'),
    start_date DATE,
    end_date DATE,
    ongoing BOOL,
    user_id INT
);

CREATE TABLE project (
    project_id INT PRIMARY KEY,
    project_name VARCHAR(64) NOT NULL,
    project_tags SET('State', 'Federal', 'NSF', 'NIH', 'Industry'),
    start_date DATE,
    end_date DATE,
    ongoing BOOL,
    user_id INT,
    schedule_id INT
);

CREATE TABLE organization (
    organization_id INT PRIMARY KEY,
    organization_name VARCHAR(64) NOT NULL,
    organization_tags SET('School', 'Workplace', 'Club', 'Union'),
    start_date DATE,
    end_date DATE,
    ongoing BOOL,
    user_id INT,
    schedule_id INT
);

CREATE TABLE schedule (
    schedule_id INT PRIMARY KEY,
    schedule_name VARCHAR(64) NOT NULL
);

CREATE TABLE event (
    event_id INT PRIMARY KEY,
    event_name VARCHAR(64) NOT NULL,
    event_days SET('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'),
    start_date TIME,
    end_date TIME,
    schedule_id INT
);

-- Alter Table, etablish relationships

-- 1:M relationships
ALTER TABLE education
ADD FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL;

ALTER TABLE project
ADD FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
ADD FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE SET NULL;

ALTER TABLE organization
ADD FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
ADD FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE SET NULL;

ALTER TABLE event 
ADD FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE SET NULL;

-- M:N relationships
CREATE TABLE connection (
    user_id INT,
    connections_id INT,
    PRIMARY KEY (user_id, connections_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (connections_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- many projects are a part of many organizations
CREATE TABLE project_organization (
    project_id INT,
    organization_id INT,
    PRIMARY KEY (project_id, organization_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organization(organization_id) ON DELETE CASCADE
);
-- many projects have many connections
CREATE TABLE project_connection (
    project_id INT,
    connections_id INT,
    PRIMARY KEY (project_id, connections_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE,
    FOREIGN KEY (connections_id) REFERENCES connection(connections_id) ON DELETE CASCADE
);
-- many organizations have many connections
CREATE TABLE organization_connection (
    organization_id INT,
    connections_id INT,
    PRIMARY KEY (organization_id, connections_id),
    FOREIGN KEY (organization_id) REFERENCES organization(organization_id) ON DELETE CASCADE,
    FOREIGN KEY (connections_id) REFERENCES connection(connections_id) ON DELETE CASCADE
);

-- many schedules have many connections

CREATE TABLE schedule_connection (
    schedule_id INT,
    connections_id INT,
    PRIMARY KEY (schedule_id, connections_id),
    FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (connections_id) REFERENCES connection(connections_id) ON DELETE CASCADE
);

-- Fill the tables with data


/* 
Ficticious scenario: 
2) Alex attends Fresno State, John attends Clovis Community
3) Alex works on CAHSI and Artifact, while John works on Research and Artifact
4) Alex works for Google and Fresno State, John works for Clovis Community and Fresno State 
5) Alex and has a CAHSI project schedule, John has a Research project schedule
   6) Alex has a weekly meeting and weekly work, John has lit review and independent study 
- Alex and John are connected
- CAHSI proj is with Google org, Artifact is with Fresno State, Research is with Clovis Community
- Alex works with John on Artifact and has weekly dicussions with John
  - Likewise John works with Alex on Artifact, BUT does not have weekly discussion labeled
- John puts that he has weekly Fresno State schedule with Alex about Artifact

We want to give as much information to each to fill in gaps of information in areas that Alex and
John are connected in. 

*/

INSERT INTO users VALUES
(101, 'Alexander', 'Madrigal', '2005-04-19'),
(102, 'John', 'Smith', '2000-12-31');

INSERT INTO education VALUES
(201, 'Fresno State', 'Bachelor', 'Computer Science', 'Software Engineering,Artificial Intelligence', '2023-08-01', NULL, 1, 101),
(202, 'Clovis Community', 'Associate', 'Computer Engineering', 'Artificial Intelligence,Web Developer', '2022-09-01', NULL, 1, 102);

INSERT INTO schedule VALUES
(501, 'CAHSI Weekly'),
(502, 'Research Weekly');

INSERT INTO project VALUES 
(301, 'CAHSI', 'State', '2023-09-30', NULL, 1, 101, 501),
(302, 'Artifact', NULL, '2024-02-18', NULL, 1, 101, NULL),
(303, 'Research', NULL, '2022-06-12', NULL, 1, 102, 502),
(304, 'Artifact', NULL, '2024-02-18', NULL, 1, 102, NULL);

INSERT INTO organization VALUES
(401, 'Google', 'Workplace', NULL, NULL, 1, 101, NULL),
(402, 'Fresno State', 'School', NULL, NULL, 1, 101, NULL),
(403, 'Clovis Community', 'School', NULL, NULL, 1, 102, NULL),
(404, 'Fresno State', 'School', NULL, NULL, 1, 102, NULL);

INSERT INTO event VALUES
(601, 'CAHSI Meeting', 'Thu', '12:50:00', '13:15:00', 501),
(602, 'CAHSI Work', 'Fri,Sat,Mon', NULL, NULL, 501),
(603, 'Lit Review', 'Tue,Wed', NULL, NULL, 502),
(604, 'Independent Study', 'Sun', NULL, NULL, 502);

INSERT INTO connection VALUES 
(101, 102),
(102, 101);

INSERT INTO project_organization VALUES
(301, 401),
(302, 402),
(303, 401),
(304, 402);

INSERT INTO project_connection VALUES
(302, 102),
(304, 101);

INSERT INTO organization_connection VALUES
(404, 101);







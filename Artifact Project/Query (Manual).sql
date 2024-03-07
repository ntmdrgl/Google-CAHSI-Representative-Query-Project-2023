
-- Use FIND_IN_SET to find labels in sets
SELECT * 
FROM education
WHERE FIND_IN_SET('Artificial Intelligence', cs_focus) > 0;


-- Use JOIN to combine tables, use ON to connection table with keys for 1:M 
-- ex. Find the organizations whose users' birthdays are after 2000

SELECT organization.organization_name, organization.organization_tags, users.first_name, users.last_name, users.birthday
FROM organization
JOIN users
ON organization.user_id = users.user_id
WHERE users.birthday > '2000-1-1' AND organization.organization_tags = 'Workplace';


-- Use JOIN with nested queries for N:M 
-- ex. Find name of all organizations that Alexander has projects with

SELECT organization.organization_name
FROM organization
JOIN project_organization ON project_organization.organization_id = organization.organization_id
JOIN project ON project_organization.project_id = project.project_id
WHERE project_organization.project_id = 
    (SELECT project_organization.project_id
    WHERE project.user_id = 101);


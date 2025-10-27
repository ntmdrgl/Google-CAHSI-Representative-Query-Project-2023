-- Find all the projects that Alex's connection's have in his projects
-- Goal: Return all projects from the user's connections
-- Query 1: find all connections from user's projects
-- Query 2: find all projects from selected connections 
SELECT * 
FROM project
JOIN (
	SELECT connection.connection_id
	FROM connection
	JOIN (SELECT project_connection.connection_id
		FROM project_connection
		JOIN project ON project_connection.project_id = project.id
		WHERE project.user_id = 25
	) AS sub_1
	WHERE sub_1.connection_id = connection.id
) AS sub_2
WHERE sub_2.connection_id = project.user_id;

-- Goal: Get name and birthday
-- Sub query returns all connections of user
-- Main query find the user of all connections 
SELECT *
FROM user
JOIN (SELECT  connection.connection_id
FROM connection
JOIN user on user.id = connection.user_id
where connection.user_id = 25 AND user.private = false
) AS sub
where user.id = sub.connection_id;

-- GOAL: find all connection's not already connected with user  
SELECT * -- user.first_name, user.last_name 
FROM user 
LEFT JOIN (SELECT connection.connection_id
	FROM connection
	WHERE connection.user_id = 25request
) AS sub 
ON user.id = sub.connection_id -- user's connection is with a user
WHERE sub.connection_id IS NULL AND user.id != 25; -- find user's without connections excluding the user
 

	

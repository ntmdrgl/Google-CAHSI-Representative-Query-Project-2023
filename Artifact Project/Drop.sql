use artifactdb;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS education;
DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS organization;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS connection;
DROP TABLE IF EXISTS project_organization;
DROP TABLE IF EXISTS project_connection;
DROP TABLE IF EXISTS organization_connection;
DROP TABLE IF EXISTS schedule_connection;

SET FOREIGN_KEY_CHECKS = 1;
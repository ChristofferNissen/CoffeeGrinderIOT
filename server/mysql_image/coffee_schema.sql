CREATE DATABASE coffee_database;

USE coffee_database;

CREATE TABLE Grinds (
  Id INTEGER PRIMARY KEY auto_increment,
  GrindName VARCHAR(100) not null,
  Duration INTEGER not null
);

CREATE TABLE Records (
  Id INTEGER PRIMARY KEY auto_increment,
  Date VARCHAR(100) NOT NULL,
  Grind INTEGER not null,
  Count INTEGER not null
);

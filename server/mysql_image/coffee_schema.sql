CREATE DATABASE coffee_database;

USE coffee_database;

CREATE TABLE Grinds (
  Id INTEGER PRIMARY KEY auto_increment,
  GrindName VARCHAR(100) not null,
  Duration INTEGER not null
);

CREATE TABLE record (
  id INTEGER PRIMARY KEY auto_increment,
  Dato DATE not null,
  Grind int not null,
  FOREIGN KEY (Grind) REFERENCES Grinds(Id),
  Count INTEGER not null
);

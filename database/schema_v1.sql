-- Version 1: Initial Database Schema

-- Users 
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL DEFAULT 'Not set',
    last_name VARCHAR(100) NOT NULL DEFAULT 'Not set',
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    contact VARCHAR(20) NOT NULL DEFAULT 'Not set',
    address VARCHAR(200) NOT NULL DEFAULT 'Not set',
    age INTEGER,
    gender VARCHAR(10) DEFAULT 'Not set',
    role VARCHAR(20) NOT NULL DEFAULT 'Not set',
    password VARCHAR(200) NOT NULL,
    CONSTRAINT check_age_for_users CHECK ((role = 'admin') OR (role != 'admin' AND age >= 18))
);

-- Shelters 
CREATE TABLE shelter (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    address VARCHAR(200) NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    website VARCHAR(150) UNIQUE,
    date_established VARCHAR(50) NOT NULL,
    shelter_type VARCHAR(50) NOT NULL,
    approved BOOLEAN DEFAULT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'shelter',
    password VARCHAR(200) NOT NULL
);

--  Animals 
CREATE TABLE animal (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    age VARCHAR(20),
    breed VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    image1 VARCHAR(200) NOT NULL,
    shelter_id INTEGER NOT NULL REFERENCES shelter(id)
);

--  Adoption Requests 
CREATE TABLE adoption_request (
    id SERIAL PRIMARY KEY,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    animal_id INTEGER NOT NULL REFERENCES animal(id)
);

--  Notifications 
CREATE TABLE notification (
    id SERIAL PRIMARY KEY,
    message VARCHAR(200),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES "user"(id),
    shelter_id INTEGER REFERENCES shelter(id)
);
DROP DATABASE IF EXISTS scrum_gruppe3;
CREATE DATABASE IF NOT EXISTS scrum_gruppe3;
ALTER DATABASE scrum_gruppe3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scrum_gruppe3;


DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    
    fornavn VARCHAR(100) NOT NULL,
    etternavn VARCHAR(100) NOT NULL,
    epost VARCHAR(255) UNIQUE NOT NULL,
    passord_hash VARCHAR(255) NOT NULL,
    telefonnummer VARCHAR(25),
    adresse TEXT,
    registreringsdato DATE NOT NULL,
    rolle ENUM('admin', 'student') DEFAULT 'student'
);

DROP TABLE IF EXISTS books;
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    
    tittel VARCHAR(255) NOT NULL,
    forfatter VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    utgivelsesår YEAR NOT NULL,
    kategori VARCHAR(100),
    status ENUM('Tilgjengelig', 'Utlånt', 'Forsinket') DEFAULT 'Tilgjengelig'
);

DROP TABLE IF EXISTS loans;
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
	FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    
    user_id INT,
    book_id INT,
    utlånsdato DATE NOT NULL,
    forventet_returdato DATE NOT NULL,
    faktisk_returdato DATE,
    status ENUM('Aktiv', 'Fullført', 'Forsinket') DEFAULT 'Aktiv'
);

DROP TABLE IF EXISTS reminders;
CREATE TABLE reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
	FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
	
    loan_id INT,
    purringsdato DATE NOT NULL,
    status ENUM('Sendt', 'Ikke Sendt') DEFAULT 'Ikke Sendt',
    melding TEXT
);

################################################################################
####################### FORSLAG TIL UTBEDRING ##################################
################################################################################

-- Bok Anmeldelser
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
	FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    
    book_id INT,
    user_id INT,
    vurdering INT CHECK (vurdering >= 1 AND vurdering <= 5),
    anmeldelse TEXT,
    anmeldelsesdato DATE NOT NULL
);


### CHAT GPT FORBEDRINGER

-- Bok Tags (for bedre søkefunksjonalitet og filtrering)
CREATE TABLE tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    
    navn VARCHAR(50) UNIQUE NOT NULL
);

-- Koblingstabell mellom bøker og tags
CREATE TABLE book_tags (
    PRIMARY KEY (book_id, tag_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id),

    book_id INT,
    tag_id INT
);



INSERT INTO books (tittel, forfatter, isbn, utgivelsesår, kategori, status) VALUES
('JavaScript for Vikings: Erobre webutvikling med ære', 'Michelle Stephens', '9780830888092', 2015, 'Webutvikling', 'Tilgjengelig'),
('Buggenes hemmelige liv: Fortellinger fra koden', 'Melanie Martin', '9780727704450', 2012, 'Webutvikling', 'Tilgjengelig'),
('Kaffe og Kode: Oppskrifter for nattlige kodingsøkter', 'Jill Thompson', '9781542802512', 2022, 'Webutvikling', 'Tilgjengelig'),
('Looping gjennom livet: En programmerers memoarer', 'Michele Howard', '9780787813222', 2010, 'Software Engineering', 'Tilgjengelig'),
('Hvordan unngå å krasje datamaskinen: En guide for nybegynnere', 'Jeffrey Johnson', '9781782074380', 1991, 'Programmering', 'Tilgjengelig'),
('Erfaringer fra en Java Utvikler Forlatt på en Øde Øy med Bare en JavaScript Bok', 'Luis Cole', '9780385238410', 2006, 'Lærebok', 'Tilgjengelig'),
('Hvorfor HTML Er Ikke Et Programmeringsspråk: En Samling Essay', 'Patrick Cole', '9780943261423', 2018, 'Lærebok', 'Tilgjengelig'),
('Fra Java til JavaScript: En Reise med Koffeinsjokk', 'Andrew Hall', '9781902437194', 2014, 'Lærebok', 'Tilgjengelig'),

('Ringenes Herre: Ringens brorskap', 'J.R.R. Tolkien', '9780261102754', 1954, 'Fantasy', 'Tilgjengelig'),
('Ringenes Herre: To tårn', 'J.R.R. Tolkien', '9780261102761', 1954, 'Fantasy', 'Tilgjengelig'),
('Ringenes Herre: Atter en konge', 'J.R.R. Tolkien', '9780261102978', 1955, 'Fantasy', 'Tilgjengelig'),

('Configurable needs-based budgetary management', 'Gerald West', '9780534287429', 1971, 'Fantasy', 'Utlånt'),
('Organized coherent firmware', 'Hannah Parker', '9780887358951', 2005, 'Roman', 'Utlånt'),
('Enhanced motivating leverage', 'Audrey Lyons', '9781922578655', 1958, 'Vitenskap', 'Tilgjengelig'),
('Digitized explicit structure', 'Ryan Frazier', '9780166058176', 1978, 'Vitenskap', 'Utlånt'),
('Optional background open architecture', 'Amber Mccoy', '9780383463340', 1937, 'Historie', 'Utlånt'),
('Customizable multi-state Graphic Interface', 'Mark George', '9781027375395', 2020, 'Roman', 'Forsinket'),
('Multi-layered asymmetric frame', 'Scott Howell', '9780149858007', 1920, 'Historie', 'Tilgjengelig'),
('Down-sized systemic ability', 'Alexander Romero', '9781370830787', 1924, 'Fantasy', 'Forsinket'),
('Reverse-engineered systematic database', 'Travis Patton', '9780326437933', 1958, 'Roman', 'Tilgjengelig'),
('Organized value-added monitoring', 'Kristina Washington', '9780940848672', 1999, 'Historie', 'Utlånt'),

('Mysteriet med den forsvunne pizza', 'Alex Hansen', '9780261102354', 2020, 'Krim', 'Tilgjengelig'),
('Eventyret om den snakkende brokkolien', 'Sofia Berg', '9780261102777', 2021, 'Fantasy', 'Utlånt'),
('Den utrolige reisen til sofaens indre', 'Erik Lund', '9780261102378', 2022, 'Vitenskap', 'Forsinket'),
('Pinguinene som elsket kebab', 'Michael Logan', '9781928220602', 1962, 'Fantasy', 'Utlånt'),
('På tur med trollet', 'Reginald Phelps', '9780120056927', 1959, 'Natur', 'Tilgjengelig'),
('Når katter drømmer', 'Charlene Wise', '9781100713144', 1953, 'Fantasy', 'Forsinket'),
('Magien i et fjellvann', 'John Lee', '9781561556724', 1980, 'Natur', 'Forsinket'),
('Hvordan snakke med en elg', 'Amber Kane', '9780022075644', 2021, 'Mysterium', 'Utlånt'),
('Den siste brunosten', 'Christine Shea', '9781569845622', 1975, 'Fantasy', 'Forsinket'),
('Fjellgeitens store eventyr', 'Elizabeth Harris', '9781629506579', 1923, 'Mysterium', 'Tilgjengelig'),
('Gåter under vann: Laksens hemmeligheter', 'Thomas Jones', '9780218598421', 1964, 'Fantasy', 'Utlånt'),
('Gnomene som ikke kunne danse', 'Cody Zamora', '9780413781239', 1974, 'Humor', 'Forsinket'),
('Den flyvende pølsen', 'Billy Ramsey', '9780360188518', 1938, 'Fantasy', 'Tilgjengelig'),
('Eventyret om den tapte sokken', 'Julie Wilson', '9780523872674', 1909, 'Fantasy', 'Utlånt'),
('Huldra som visste for mye', 'Todd Young', '9781432247706', 1927, 'Humor', 'Tilgjengelig'),
('Mysteriet med det evige regnet', 'Zachary Sanchez', '9780659401335', 1987, 'Humor', 'Forsinket'),
('Trollmannen fra Sogndal', 'Dr. Jesus Guerrero', '9781889868653', 1955, 'Mysterium', 'Tilgjengelig'),
('Vikinger på shopping', 'Laura Bell', '9780809175888', 2011, 'Fantasy', 'Tilgjengelig');
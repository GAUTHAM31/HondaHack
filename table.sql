CREATE TABLE LocationTable (
    LocationID int(11) NOT NULL AUTO_INCREMENT,
    Latitude  float,
    Longitude  float,
    Score int,
    LocationTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (LocationID)
);
CREATE TABLE CarTable (
    LocationID int NOT NULL,
    CarID int NOT NULL,
    ParkBrake  VARCHAR(3),
    ParkSensor  VARCHAR(3),
    ParkMode  VARCHAR(3),
    EngineStart BOOLEAN DEFAULT false,
    PRIMARY KEY (CarID),
    FOREIGN KEY (LocationID) REFERENCES LocationTable(LocationID)
);
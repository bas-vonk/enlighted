CREATE DATABASE 1_bronze;
\connect 1_bronze;
DROP SCHEMA public;
CREATE SCHEMA tibber;
CREATE SCHEMA enphase;
CREATE SCHEMA homeconnect;
CREATE SCHEMA nibe;
CREATE SCHEMA homewizard;

CREATE DATABASE 2_silver;
\connect 2_silver;
DROP SCHEMA public;
CREATE SCHEMA silver;

CREATE DATABASE 3_gold;
\connect 3_gold;
DROP SCHEMA public;
CREATE SCHEMA gold;

CREATE DATABASE auth;
\connect auth;
DROP SCHEMA public;
CREATE SCHEMA homeconnect;
CREATE SCHEMA nibe;
drop table if exists testtable;
create table testtable (
  "id" int,
  "name" varchar(100)
);
-- /pgdata/ is determined by the volume mount in the docker-compose file
COPY testtable FROM '/pgdata/testtable.csv' DELIMITER ',' CSV HEADER;

create user dbuser1 password 'pw1';
grant all privileges on table testtable to dbuser1;

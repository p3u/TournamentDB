CREATE DATABASE tournament;

\c tournament;


CREATE TABLE players (
                      id serial PRIMARY KEY,
                      player_name varchar(300)
);


CREATE TABLE matches (
                      id serial PRIMARY KEY,
                      winner serial REFERENCES players(id),
                      loser serial REFERENCES players(id)
);

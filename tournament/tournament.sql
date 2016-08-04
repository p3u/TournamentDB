CREATE DATABASE tournament;

\c tournament;


CREATE TABLE players ( content text,
                     id serial PRIMARY KEY,
                     player_name varchar(300)
);


CREATE TABLE matches ( content TEXT,
                    id serial PRIMARY KEY,
                    winner serial REFERENCES players(id),
                    loser serial REFERENCES players(id)
);

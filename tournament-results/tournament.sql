-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

\c vagrant

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

\c tournament

-- Drop all the tables if they exist (ORDER MATTERS!)
DROP VIEW player_standings;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;

-- 
CREATE TABLE events (
	event_id SERIAL PRIMARY KEY,
	event_name TEXT NOT NULL
);

-- 
CREATE TABLE players (
	player_id SERIAL PRIMARY KEY,
	event_id INTEGER NOT NULL,
	player_name TEXT NOT NULL,
	FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

-- TODO: Insure that both players are in the same event on INSERT
CREATE TABLE matches (
	match_id SERIAL PRIMARY KEY,
	event_id INTEGER NOT NULL,
	player_id_A INTEGER NOT NULL,
	player_id_B INTEGER NOT NULL,
	tie BOOLEAN DEFAULT FALSE,
	FOREIGN KEY (player_id_A) REFERENCES players(player_id),
	FOREIGN KEY (player_id_B) REFERENCES players(player_id),
	FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);


CREATE VIEW player_standings AS
SELECT t.event_id, t.player_id, t.player_name, t.wins, t.losses, t.matches 
FROM (
	SELECT e.event_id as event_id
		, p.player_id AS player_id
		, p.player_name AS player_name
		, COUNT(mw.player_id_A) AS wins
		, COUNT(ml.player_id_B) AS losses
		, COUNT(mw.player_id_A) + COUNT(ml.player_id_B) AS matches
	FROM players p
	INNER JOIN events e ON e.event_id = p.event_id
	LEFT JOIN matches mw ON mw.player_id_A = p.player_id
	LEFT JOIN matches ml ON ml.player_id_B = p.player_id
	GROUP BY e.event_id, p.player_id, p.player_name
) AS t
GROUP BY t.event_id, t.wins, t.losses, t.matches, t.player_id, t.player_name
ORDER BY SUM(t.wins) DESC, SUM(t.losses) ASC;

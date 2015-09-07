-- Table definitions for the tournament project.

\c vagrant

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

\c tournament

-- Drop all the tables if they exist
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

-- Player ID a 
CREATE TABLE matches (
	match_id SERIAL PRIMARY KEY,
	event_id INTEGER NOT NULL,
	player_id_win INTEGER NOT NULL,
	player_id_lose INTEGER NOT NULL,
	tie BOOLEAN DEFAULT FALSE,
	FOREIGN KEY (player_id_win) REFERENCES players(player_id),
	FOREIGN KEY (player_id_lose) REFERENCES players(player_id),
	FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);


CREATE VIEW player_standings AS
SELECT t.event_id, t.player_id, t.player_name, t.wins, t.losses, t.matches 
FROM (
	SELECT p.event_id as event_id
       , p.player_id AS player_id
       , p.player_name AS player_name
       , COUNT(m.player_id_win) AS wins
       , (SELECT COUNT(*) 
          FROM matches mc
          WHERE 
              mc.match_id = NULL
              AND player_id = mc.player_id_win
              OR player_id = mc.player_id_lose
         ) AS losses -- Not too sure why this works but it does...
       , (SELECT COUNT(*) 
          FROM matches mc
          WHERE 
              mc.event_id = event_id
              AND player_id = mc.player_id_win
              OR player_id = mc.player_id_lose
         ) AS matches 
	FROM events e
	INNER JOIN matches m ON e.event_id = m.event_id
	RIGHT JOIN players p ON p.player_id = m.player_id_win
	GROUP BY p.event_id, p.player_id
) AS t
GROUP BY t.event_id, t.wins, t.losses, t.matches, t.player_id, t.player_name
ORDER BY t.event_id, t.wins DESC, t.losses ASC;

#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def executeQuery(query, connection):
    """Executes a query on the given connection.  Returns nothing.
    Args: 
      query: The query string to be executed.
      connection: The database connection object.
    """
    c = connection.cursor()
    c.execute(query)
    connection.commit()
    connection.close()


def executeResultQuery(query, connection):
    """Executes a query on the provided connection. 
    Returns results of the query.
    Args: 
      query: The query string to be executed.
      connection: The database connection object.
    """
    c = connection.cursor()
    c.execute(query)
    result = c.fetchall()
    connection.commit()
    connection.close()
    return result


def deleteMatches():
    """Remove all the match records from the database."""
    q = "DELETE FROM matches;"
    executeQuery(q, connect())


def deleteEvent(event_id):
    """
    Remove a particular event from the database. Along with associated players
    and matches.
    """
    q = "DELETE FROM events WHERE event_id = %s;"
    db = connect()
    cur = db.cursor()
    cur.execute(q, [event_id,])
    db.commit()
    db.close()


def deleteEvents():
    """Remove all events from the database with associated players and matches.
    """
    q = "DELETE FROM events;"
    executeQuery(q, connect())


def deletePlayersFromEvent(event_id):
    """Remove all players form an event in the database."""
    q = "DELETE FROM players WHERE event_id = %s;"
    db = connect()
    cur = db.cursor()
    cur.execute(q, [event_id,])
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    q = "DELETE FROM players;"
    executeQuery(q, connect())


def countEvents():
    """Returns the number of events available for registration."""
    q = "SELECT COUNT(*) FROM events;"
    result = executeResultQuery(q, connect())
    count = [int(row[0]) for row in result]
    return count[0]    


def countPlayers():
    """Returns the number of players currently registered."""
    q = "SELECT COUNT(*) FROM players;"
    result = executeResultQuery(q, connect())
    count = [int(row[0]) for row in result]
    return count[0]


def createEvent(event_name):
    """Create a new event in the database with the given name."""
    q = "INSERT INTO events (event_name) VALUES (%s) RETURNING event_id;"
    db = connect()
    cur = db.cursor()
    cur.execute(q, [event_name,])
    eid = [int(row[0]) for row in cur.fetchall()]
    db.commit()
    db.close()
    return eid[0]


def registerPlayer(event_id, name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      event_id: The id of the event the player is registering for.
      name: the player's full name (need not be unique).
    """
    q1 = """
    INSERT INTO players (event_id, player_name) 
    VALUES (%s, %s) RETURNING player_id;
    """
    db = connect()
    cur = db.cursor()
    cur.execute(q1, [event_id, name,])
    db.commit()
    db.close()


def playerStandings(event_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    q = """
    SELECT player_id, player_name, wins, matches FROM player_standings
    WHERE event_id = %s;
    """
    db = connect()
    cur = db.cursor()
    cur.execute(q, [event_id,])
    result = cur.fetchall()
    ranking = [( 
        int(row[0]),
        str(row[1]),
        int(row[2]),
        int(row[3]),
    ) for row in result]
    db.close()
    return ranking


def reportMatch(event_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    q = """
        INSERT INTO matches (event_id, player_id_A, player_id_B, tie)
        VALUES (%s, %s, %s, %s);
        """
    db = connect()
    cur = db.cursor()
    cur.execute(q, [event_id, winner, loser, False,])
    db.commit()
    db.close()

 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    count_q = "SELECT COUNT(*) FROM players;"
    q = "SELECT player_id, player_name FROM player_standings;"
    db = connect()
    cur = db.cursor()
    cur.execute(count_q)
    num_of_players = [int(row) for row in cur.fetchone()]
    if num_of_players[0] % 2 == 0 and num_of_players[0] != 0:
        cur.execute(q)
        matchups = []
        for i in range(0, num_of_players[0] / 2):
            tpl = cur.fetchmany(2)
            matchups.append((tpl[0][0], tpl[0][1], tpl[1][0], tpl[1][1]))
        db.close()
        return matchups
    else:
        db.close()
        return None

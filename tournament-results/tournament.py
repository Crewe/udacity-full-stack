#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random
import math

BYE = -1
rand = random

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    q = "DELETE FROM matches;"
    db = connect()
    cur = db.cursor()
    cur.execute(q)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    q = "DELETE FROM players;"
    db = connect()
    cur = db.cursor()
    cur.execute(q)
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    q = "SELECT COUNT(*) FROM players;"
    db = connect()
    cur = db.cursor()
    cur.execute(q)
    count = [int(row[0]) for row in cur.fetchall()]
    db.close()
    return count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    q = ["INSERT INTO players (player_name) VALUES (%s) RETURNING player_id;",
         "INSERT INTO player_stats (player_id) VALUES (%s);"]
    db = connect()
    cur = db.cursor()
    cur.execute(q[0], [name,])
    player_id = [str(row[0]) for row in cur.fetchall()]
    db.commit()
    cur.execute(q[1], player_id)
    db.commit()
    db.close()


def playerStandings():
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
    q = "SELECT player_id, player_name, wins, matches FROM player_standings;"
    db = connect()
    cur = db.cursor()
    cur.execute(q)
    ranking = [( 
        int(row[0]),
        str(row[1]),
        int(row[2]),
        int(row[3]),
    ) for row in cur.fetchall()]
    db.close()
    return ranking

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    q = """
        INSERT INTO matches (player_id_A, player_id_B, winner_id)
        VALUES (%s, %s, %s);
        """
    win_q = "UPDATE player_stats SET wins = wins + 1 WHERE player_id = %s;"
    loss_q = "UPDATE player_stats SET losses = losses + 1 WHERE player_id = %s;"
    db = connect()
    cur = db.cursor()
    cur.execute(q, [winner, loser, winner,])
    cur.execute(win_q, [winner,])
    cur.execute(loss_q, [loser,])
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

def addEventPlayers():
    players = [('Matty Cowling'), 
                ('Ardley Marko'), 
                ('Blaxton Wethington'), 
                ('Kaveri Ferebee'),
                ('Kristen Dorsett'),
                ('Horatia Storey'), 
                ('Nanon Learned'),
                ('Mell Krantz'), 
                ('Cerise Swanner'), 
                ('Morgan Kohler'), 
                ('Teofilia Henkel'),
                ('Keelin Feller'),
                ('Lucia Aragon'), 
                ('Jed Nevins'), 
                ('Nimai Samuels'), 
                ('Asta Dunfee')]
    for p in players:
        registerPlayer(p)
    

def runRounds():
    """
    Perfarem the first round of matches. If theere's an odd number of players
    then one player will be given a Bye at random.
    """
    player_count = countPlayers()
    rounds = 0
    if player_count % 2 == 0 and player_count != 0:
        rounds = int(math.log(player_count, 2))
    elif player_count % 2 == 1 and player_count > 1:
        rounds = int(math.log(player_count + 1, 2))
        
    beginTournament(rounds, False)


def beginTournament(rounds, has_byes):
    for i in range(rounds):
        matchups = swissPairings()
        if has_byes:
            # The last registered person will always have the first bye.
            first_bye = matchups[len(matchups) - 1][0]
            if first_bye == match[0] and i == 0:
                    # First round bye
                    reportMatch(first_bye, BYE)
        else:
            for match in matchups:
                # Randomly decide who is the winner. 0 = player A wins.
                winner = int(rand.uniform(0, 2))
                reportMatch(match[2 if winner else 0], 
                            match[0 if winner else 2])

from tournament import *
import random
import math
import time

BYE = -1
MIN_CONTESTANTS = 2
MAX_CONTESTANTS = 16

rand = random

def addPlayers(event_id, contestants = MAX_CONTESTANTS):
    """
    Add up to 16 contestants to a tournament so that the simulation
    may be run with 2 to 16 players.
    Args:
      event_id: The id of the event they are registering for.
      contestats: the number of participating contestants [2, 16]
    """
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
    if contestants > MAX_CONTESTANTS or contestants < MIN_CONTESTANTS:
        contestants = 8
    for i in range(contestants):
        registerPlayer(event_id, players[i])
    

def runRounds(event_id):
    """
    Perform the first round of matches. If theere's an odd number of players
    then the last player registered given a Bye.
    """
    player_count = countPlayers(event_id)
    rounds = 0
    if player_count % 2 == 0 and player_count != 0:
        rounds = int(math.log(player_count, 2))
    elif player_count % 2 == 1 and player_count > 1:
        rounds = int(math.log(player_count + 1, 2))
        
    beginTournament(rounds, event_id, bool(player_count % 2))


def beginTournament(rounds, event_id, has_byes):
    for i in range(rounds):
        matchups = swissPairings(event_id)
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
                if winner >= 2:
                    winner = 1
                reportMatch(event_id, 
                            match[2 if winner else 0], 
                            match[0 if winner else 2],)


def runSim():
    #deleteEvents()
    eid = createEvent("Immortal Melee")
    addPlayers(eid)
    runRounds(eid)

    eid = createEvent("Rue Rampage")
    addPlayers(eid, 8)
    runRounds(eid)

runSim()

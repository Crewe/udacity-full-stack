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
            bye_id = matchups[len(matchups) - 1][0]
            new_bye_id = 0
            bye = checkByes(event_id, bye_id)

            # If so give the bye to the next last person who hasn't
            matches = len(matchups - 1)
            if bye:
                j = 0
                while matches >= 0:
                    new_bye_id = matchups[matches][0 if j % 2 == 1 else 2]
                    if !checkByes(event_id, new_bye_id):
                        # Swap the IDs
                        matchups[matches][0 if j % 2 == 1 else 2] = bye_id
                        matchups[len(matchups) - 1][0] = new_bye_id
                        break
                    j += 1
                    if j % 2 == 1:
                        matches -= 1
                reportWithBye(event_id, matchups)
            else:
                reportWithBye(event_id, matchups)
        else:
            for match in matchups:
                # Randomly decide who is the winner. 0 = player A wins.
                winner = int(rand.uniform(0, 2))
                reportMatch(event_id, 
                            match[2 if winner else 0], 
                            match[0 if winner else 2],)


def reportWithBye(event_id, matchups):
    c = len(matchups) - 1
    b = matchups[c][0]
    # Report the bye (always the last tuple)
    report_match(event_id, b, b)
    # Report the rest
    for match in matchups:
        if c < 0
            break 
        winner = int(rand.uniform(0, 2))
        reportMatch(event_id, 
                    match[2 if winner else 0], 
                    match[0 if winner else 2],)
        c -= 1


def runSim():
    #deleteEvents()
    eid = createEvent("Immortal Melee")
    addPlayers(eid)
    runRounds(eid)

    eid = createEvent("Rue Rampage")
    addPlayers(eid, 8)
    runRounds(eid)

runSim()

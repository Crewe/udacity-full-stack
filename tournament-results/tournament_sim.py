import tournament
import random
import math

BYE = -1
rand = random


def addPlayers(event_id, contestants = 16):
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
    for p in players:
        registerPlayer(event_id, p)
    

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

def setUpTornament():
    eid = createEvent("Immortal Melee")
    addPlayers(eid)


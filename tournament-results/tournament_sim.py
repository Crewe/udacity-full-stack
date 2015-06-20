from tournament import *
import random
import math
import time
import os
from report import TournamentReport

BYE = -1
MIN_CONTESTANTS = 2
MAX_CONTESTANTS = 16
REPORTING = True

rand = random
tr = TournamentReport()

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
        
    if REPORTING:
        tr.AddPlayerList(players[:contestants])


def simTournament(event_id, report_on = True):
    """
    Simulates a tournament from beginning to end based on the event id.
    By default it will generate an HTML report of the tournament.
    """
    REPORTING = report_on
    player_count = countPlayers(event_id)
    rounds = 0
    has_byes = False

    if player_count % 2 == 0 and player_count != 0:
        rounds = int(math.log(player_count, 2))
    elif player_count % 2 == 1 and player_count > 1:
        rounds = int(math.log(player_count + 1, 2))
        has_byes = True

    for i in range(rounds):
        matchups = swissPairings(event_id)

        if has_byes:
            # If the event requires byes (odd number of players) then take 
            # the last player and see if they have had a bye already. 
            # If they haven't find the next player who hasn't and swap them 
            # in the matchup list.
            player = [matchups[len(matchups) - 1][0], 
                      matchups[len(matchups) - 1][1]]
            nxt_player = [0,'']

            bye = CheckByes(event_id, player[0])
            matches = len(matchups) - 2
            if bye == True:
                j = 0
                while matches >= 0:
                    nxt_player[0] = matchups[matches][0 if j % 2 == 1 else 2]
                    nxt_player[1] = matchups[matches][1 if j % 2 == 1 else 3]
                    if CheckByes(event_id, nxt_player[0]) == False:
                        # Swap the players
                        matchups[matches][0 if j % 2 == 1 else 2] = player[0]
                        matchups[matches][1 if j % 2 == 1 else 3] = player[1]
                        matchups[len(matchups) - 1][0] = nxt_player[0]
                        matchups[len(matchups) - 1][1] = nxt_player[1]
                        break
                    j += 1
                    if j % 2 == 1:
                        matches -= 1
            tr.SetRound(i)
            reportWithBye(event_id, matchups)
        else:
            for match in matchups:
                # Randomly decide who is the winner. 0 = player A wins.
                winner = int(rand.uniform(0, 2))
                reportMatch(event_id, 
                            match[2 if winner else 0], 
                            match[0 if winner else 2])
                if REPORTING:
                    tr.SetRound(i)
                    tr.AddMatchResult(match[1], match[3],
                                      match[3 if winner else 1])
        if REPORTING:
            tr.AddFinalResults(playerStandings(event_id))


def reportWithBye(event_id, matchups):
    '''Report a match taking into account byes.'''
    c = len(matchups) - 2
    b = (matchups[c+1][0], matchups[c+1][1])
    # Report the bye (always the last tuple)
    reportMatch(event_id, b[0], b[0])
    if REPORTING:
        tr.AddMatchResult(b[1], 'BYE', b[1])
    # Report the rest
    for match in matchups:
        winner = int(rand.uniform(0, 2))
        reportMatch(event_id, 
                    match[2 if winner else 0], 
                    match[0 if winner else 2])
        if REPORTING:
            tr.AddMatchResult(match[1], match[3], match[3 if winner else 1])
        c -= 1
        if c < 0:
            break


def runSim():
    # 16 Player tournament
    event_name = "Immortal Melee"
    eid = createEvent(event_name)
    tr.Filename(event_name)
    tr.EventName(event_name)
    addPlayers(eid)
    simTournament(eid) 
    tr.WriteReport()

    # 8 Player tournament
    event_name = "Rue Rampage"
    tr.ClearReport()
    tr.Filename(event_name)
    tr.EventName(event_name)
    eid = createEvent(event_name)
    addPlayers(eid, 8)
    simTournament(eid)
    tr.WriteReport()

    # 11 Player tournament with byes
    event_name = "Bye Bye Battle"
    tr.ClearReport()
    tr.Filename(event_name)
    tr.EventName(event_name)
    eid = createEvent(event_name)
    addPlayers(eid, 11)
    simTournament(eid)
    tr.WriteReport()

runSim()

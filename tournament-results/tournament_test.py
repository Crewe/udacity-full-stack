#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeletePlayers():
    deletePlayers()
    print "1. Old players can be deleted."


def testDeleteMatches():
    deleteMatches()
    print "3. Old matches can be deleted."


def testDeleteEvents():
    createEvent("Swiss Showdown")
    createEvent("Battle in Bern")
    deleteEvents()
    c = countEvents()
    if c == '0':
        raise TypeError(
            "countEvents() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countEvents() should return 0.")
    eid = createEvent("Middleground Melee")
    deleteEvent(eid)
    c = countEvents()
    if c != 0:
        raise ValueError("After deleting, countEvents() should return 0.")
    print "2. After deleting, countEvents() returns zero."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "4. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. After deleting, countPlayers() returns zero."


def testRegister():
    deleteEvents()
    deleteMatches()
    deletePlayers()
    eid = createEvent("Tyrannical Tennis Masters")
    registerPlayer(eid, "Chandra Nalaar")
    c = countPlayers(eid)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "6. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    deleteEvents()
    eid = createEvent("Kenducky Derby")
    registerPlayer(eid, "Markov Chaney")
    registerPlayer(eid, "Joe Malik")
    registerPlayer(eid, "Mao Tsu-hsi")
    registerPlayer(eid, "Atlanta Hope")
    c = countPlayers(eid)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers(eid)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "7. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    deleteEvents()
    eid = createEvent("Formula 1 Trials")
    registerPlayer(eid, "Melpomene Murray")
    registerPlayer(eid, "Randy Schwartz")
    standings = playerStandings(eid)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "8. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    deleteEvents()
    eid = createEvent("Checkers Championships")
    registerPlayer(eid, "Bruno Walton")
    registerPlayer(eid, "Boots O'Neal")
    registerPlayer(eid, "Cathy Burton")
    registerPlayer(eid, "Diane Grant")
    standings = playerStandings(eid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(eid, id1, id2)
    reportMatch(eid, id3, id4)
    standings = playerStandings(eid)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "9. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    deleteEvents()
    eid = createEvent("Wife Carrying Nationals")
    registerPlayer(eid, "Twilight Sparkle")
    registerPlayer(eid, "Fluttershy")
    registerPlayer(eid, "Applejack")
    registerPlayer(eid, "Pinkie Pie")
    standings = playerStandings(eid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(eid, id1, id2)
    reportMatch(eid, id3, id4)
    pairings = swissPairings(eid)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "10. After one match, players with one win are paired."


if __name__ == '__main__':
    testDeletePlayers()
    testDeleteEvents()
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"

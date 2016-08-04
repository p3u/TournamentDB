#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def unpack_to_tuples(results):
    rows = results.fetchall()
    return [tuple(x) for x in rows]


def get_first(results):
    result = results.fetchone()
    return result


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def execute_query(*args, **kwargs):
    """Executes a query, opening and closing connections.
       If a function is passed, executes a function to the cursor and return
       the results"""
    conn = connect()
    c = conn.cursor()
    c.execute(*args)
    if "fn" in kwargs:
        result = kwargs["fn"](c)
        conn.commit()
        conn.close()
        return result
    else:
        conn.commit()
        conn.close()


def deleteMatches():
    """Remove all the match records from the database."""
    execute_query("""DELETE FROM matches;""")


def deletePlayers():
    """Remove all the player records from the database."""
    execute_query("DELETE FROM players;")


def countPlayers():
    """Returns the number of players currently registered."""
    result = execute_query("SELECT count(ID) FROM players;", fn=get_first)
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.

    Args:
      name: the player's full name.
    """
    execute_query("""INSERT INTO players (player_name) VALUES(%s);""", (name,))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    q = """SELECT players.id,
                  players.player_name,
                  sum(CASE WHEN matches.winner=players.ID then 1 else 0 end)
                  as wins,
                  count(matches.id) as games
           FROM players LEFT JOIN matches
           ON players.ID=matches.loser OR players.ID=matches.winner
           GROUP BY players.id
           ORDER BY wins DESC;"""
    result = execute_query(q, fn=unpack_to_tuples)

    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    execute_query("""INSERT INTO matches (winner, loser)
                     VALUES('%s', '%s');""", (winner, loser))


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
    standings = playerStandings()
    matches = []
    for i in xrange(0, len(standings), 2):
        matches.append((standings[i][0], standings[i][1],
                        standings[i+1][0], standings[i+1][1]))
    return matches

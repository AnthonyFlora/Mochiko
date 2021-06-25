#! /usr/bin/python


import numpy

# -- Analysis -----------------------------------------------------------------


# -- Initialize the game state ------------------------------------------------

NUM_MISSIONS = 5
NUM_ROUNDS_PER_MISSION = 5
NUM_ROUNDS = NUM_MISSIONS * NUM_ROUNDS_PER_MISSION

FIELDS = ['MISSION', 'STATUS', 'CAPTAIN', 'SPIES', 'PASS_VOTES', 'FAIL_VOTES',
          'TEAM0', 'TEAM1', 'TEAM2', 'TEAM3', 'TEAM4', 'TEAM5', 'TEAM6', 'TEAM7', 'TEAM8', 'TEAM9',
          'VOTE0', 'VOTE1', 'VOTE2', 'VOTE3', 'VOTE4', 'VOTE5', 'VOTE6', 'VOTE7', 'VOTE8', 'VOTE9']
NUM_FIELDS = len(FIELDS)
state = numpy.zeros([NUM_ROUNDS, NUM_FIELDS])
state = state.astype(int)

# -- Injection ----------------------------------------------------------------

state[:,1] = numpy.arange(0, NUM_ROUNDS)

# -- Display ------------------------------------------------------------------

numpy.set_printoptions(linewidth=200)

print FIELDS
print state


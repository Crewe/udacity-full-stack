Tournament Database
-------------------

A Python module that uses the PostgreSQL database to keep track of players and 
matches in a game tournament. 


In order to run this you will need Vagrant, Virtual Box, and Git, and assumes
you know a bit about Git and navigating command line interfaces.

Steps:
------

# Follow the steps found [here](https://www.udacity.com/wiki/ud197/install-vagrant) for installing vagrant.
# Then clone this project to a folder you wish to run it from
# Change directories to /tournament-results
# Enter the command: __vagrant up__ (If this is the first time you're doing this, you will need an active internet connection, it couldtake some time.)
# Followed by: __vagrant ssh__
# Chonge directories to /vagrant/tournament-results
# Run postgres, and connect to the default database by entering: __pgsql vagrant__
# Create the tournamt database by running the database creation script: __\i tournament.sql__
# Connect to the tournament database with __\c tournament;__
# Exit pgsql __\q__
# Run the unit test __python tournament_test.py__
# All tests should pass. (Additional were added to base set.)
# Run the simulation with __python tournament_sim.py__. It will generate an HTML report for the results of the tournaments "Immortal Melee", "Rue Rampage", and "Bye Bye Battle".

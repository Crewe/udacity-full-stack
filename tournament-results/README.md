Tournament Database
-------------------

A Python module that uses the PostgreSQL database to keep track of players and 
matches in a game tournament. 


In order to run this you will need Vagrant, Virtual Box, and Git, and assumes
you know a bit about Git and navigating command line interfaces.

Steps:
------

1. Follow the steps found [here](https://www.udacity.com/wiki/ud197/install-vagrant) for installing vagrant.
2. Then clone this project to a folder you wish to run it from
3. Change directories to /tournament-results
4. Enter the command: __vagrant up__ (If this is the first time you're doing this, you will need an active internet connection, it couldtake some time.)
5. Followed by: __vagrant ssh__
6. Chonge directories to /vagrant/tournament-results
7. Run postgres, and connect to the default database by entering: __pgsql vagrant__
8. Create the tournamt database by running the database creation script: __\i tournament.sql__
9. Connect to the tournament database with __\c tournament;__
10. Exit pgsql __\q__
11. Run the unit test __python tournament_test.py__
12. All tests should pass. (Additional were added to base set.)
13. Run the simulation with __python tournament_sim.py__. It will generate an HTML report for the results of the tournaments "Immortal Melee", "Rue Rampage", and "Bye Bye Battle".

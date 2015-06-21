Tournament Database
-------------------

A Python module that uses the PostgreSQL database to keep track of players and 
matches in a game tournament. 


In order to run this you will need Vagrant, Virtual Box, and Git, and assumes
you know a bit about Git and navigating command line interfaces.

Steps:
------

1. Follow the steps found [here](https://www.udacity.com/wiki/ud197/install-vagrant) for installing vagrant.
1. Then clone this project to a folder you wish to run it from
1. From the root directotry enter the command: __vagrant up__ (If this is the first time you're doing this, you will need an active internet connection, it couldtake some time.)
1. Change directories into */tournament-results*
1. Connect to the virtual machine with: __vagrant ssh__
1. Change directories to */vagrant/tournament-results*
1. Run postgres, and connect to the default database by entering: __pgsql vagrant__
1. Create the tournamt database by running the database creation script: __\i tournament.sql__
1. Test ability to connect to the tournament database with __\c tournament;__
1. Exit pgsql __\q__
1. Run the unit test __python tournament_test.py__
1. All tests should pass.
1. Run the simulation with __python tournament_sim.py__. It will generate an HTML report for the results of the tournaments "Immortal Melee", "Rue Rampage", and "Bye Bye Battle".

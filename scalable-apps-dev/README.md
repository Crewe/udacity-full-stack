Conference Central (ud858)
=========

This project is to develop a API server to support the [Conference Central](http://und-crewe-0001.appspot.com) conference organization app that exists on the web using Python. The API supports the following functionality found within the app: user authentication, user profiles, conference information, and various manners in which to query the data. The full conference API can be accessed via Google's [API Explorer](http://und-crewe-0001.appspot.com/_ah/api/explorer).

Task 1
------
**What where your design choices for session and speaker implementation?/Explain in a couple of papragraphs your design choices for session and speaker implementation.**

My design incorporated sessions as a child of a conference. This would make it easier to retrieve sessions of a conference from just having a conference key. For the speaker I opted to simply have the speaker as a string in the session, since looking up sessions by speaker would not be that difficult. However, if the speaker name needed correcting, then you'd have to fix them all manually.


Task 3
------
**Think about other types of queries that would be useful for this application. Describe the purpose of 2 new queries and write the code that would perform them.**

* A query that filters sessions by their duration. For someone who wishes to only find sessions that are an hour or less.

This was implemented in...

* Another query would be filtering sessions that occur between a certain time interval if you have a time slot you wish to fill, or keep open.

This was implemented in...

*Solve the following query related problem:*

**Let’s say that you don't like workshops and you don't like sessions after 7 pm. How would you handle a query for all non-workshop sessions before 7 pm? What is the problem for implementing this query? What ways to solve it did you think of?**

The problem would be the inequality filter on the session start time, and filtering out non-workshops, as you can only perform an inequality query on one property per query. One way around this would be obtaining the keys of all non-workshop entities, then performing an inequality query on the start time and displaying those results.

bubble-up
===========
bubble-up is an app for reccomending articles based on user's preferences
<br/>
_built at [Complicity - 2013](http://berlinergazette.de/symposium/complicity/) by 
[@brianabelson](http://twitter.com/brianabelson), [@annabelchurch](http://twitter.com/annabelchurch),
and [@pudo](http://twitter.com/pudo)_
<br/>

## How do I get started?
1. Create a [postgres](http://www.postgresql.com/) database called `news` (or whatever you want)
2. Create an environmental variable called `DATABASE_URL` with your database path, e.g. `export DATABASE_URL=postgresql://brian:mc@localhost:5432/news`
3. Build the database of newspapers using `build_newspaper_db.py`, which sources data from [NewspaperMap](http://www.newspapermap.com/)
4. Build the database of articles using `scrape_rss_feeds.py`
5. Run `web.py` to host the api

## What's in store?  
I'm hoping to build an intelligent way of determining article similarity via textual features _on-the-fly_.
<br/>
my experiments with this can be found in `topic_modeling/`
# officepong

Original Description:

> Your office plays ping pong (or foosball) and some people just won't shut up about how they won a match last week. You sort of remember it happening, but more clearly remember beating them 4 games in a row. It might be their turn to gloat, but you want some talking points too.
> 
> That's where OfficePong comes in. Set it up on someone's computer (or the cloud) and record all your games. It's simple to use from a phone, tablet, or laptop. Behind the scenes it grades matches using an aggressively-tuned ELO system. Whoever is on top today won't be there for long. Like playing doubles? Well we fudged some math so you can include those clown fiestas too. Since it ranks matches based on the score, even novices can get their revenge by gaining ELO on a lost game. If you don't see your score immediately on the leaderboard, don't worry. There's a 3 game minimum before it show up.

Six years after the original project was last touched, we picked it up and modernized it, pulling it into the Python `asyncio` age with the help of Quart, a Flask-compatible web framework for `asgi` instead of `wsgi`. The SQLalchemy extension for quart lacked documentation, so we switched to Tortoise ORM. We also added a Dockerfile for ease of development and deployment. The routes were also wrapped in a Quart `blueprint` to make including this in a larger Quart app easy. If you plan to do that and it's not working, please contact me.

## Install

This is a basic Python-based Quart webapp. Using the Dockerfile, it should run on almost any machine. It's self-contained, with a local SQLite database, but as there's no credentialing or write limitations, this application should not be made available on the public internet.

## Local Development

Note: We plan to create a development Dockerfile, it just hasn't happened yet.

```bash
sudo apt install python3-pip sqlite3
python3 -m venv ./venv/
./venv/bin/pip install -e .

QUART_APP=officepong venv/bin/quart --debug run
```

## Run

```bash
docker build -t officepong:latest .
docker run -p "5000:5000" -v `pwd`/app_data:/app officepong:latest
```

Navigate to http://localhost:5000/ in your browser. 

If you need to delete or change a player or score please do that directly through the database. Otherwise, you can do the following actions in the browser. The database is a basic sqlite instance with two tables (player and match). If you ever delete a match or update one's scores, click the Recalculate button on the website and it will automatically correct every player's ELO, games played, and non-score statistics in the matches.

If you need to rename a player, good luck.

## Update

If a new version ever comes out, pull, rebuild the Docker image and then recreate the container. Just make sure the DB is in a directory that is mounted inside.


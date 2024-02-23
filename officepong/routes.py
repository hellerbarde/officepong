"""
Handle routes for Quart website
"""
from datetime import datetime
from quart import redirect, Blueprint, render_template, request, url_for, current_app
from officepong import elo
from officepong.models import Player, Match


officepong_app = Blueprint('officepong', __name__, template_folder='templates')


@officepong_app.route('/register', methods=['POST'])
async def register():
    """ Register a new user by adding them to the database. """
    form = await request.form
    name = form['name']
    if not len(name):
        return redirect(url_for('officepong.index', error="The player name is missing"))
    await Player.create(
        name=name
    )
    return redirect(url_for('officepong.index', success="Player added"))


@officepong_app.route('/add_match', methods=['POST'])
async def add_match():
    """
    Store the result of the match in the database and update the players'
    elo scores.
    """

    form = await request.form
    # Extract fields from request fields
    win_names, lose_names = form.getlist('winner'), form.getlist('loser')
    win_score, lose_score = int(form['win_score']), int(form['lose_score'])

    # Minimize misclicks
    if lose_score + 2 > win_score or (win_score not in (11, 21) and lose_score + 2 != win_score):
        return redirect(url_for('officepong.index', error="The score is implausible."))
    
    # Don't add score if there's a problem with the names
    if not win_names or not lose_names:
        return redirect(url_for('officepong.index', error="The winner or the loser was not specified."))
    for name in win_names:
        if name in lose_names:
            return redirect(url_for('officepong.index', error="A winner is also part of the losers"))
    # I think this can never happen... But I'm not sure.
    for name in lose_names:
        if name in win_names:
            return redirect(url_for('officepong.index', error="A loser is also part of the winners"))

    # Map each player to their current elo and #games for easy use below
    players = {}
    for player in await Player.all():
        players[player.name] = {'elo': player.elo, 'games': player.games}

    # Figure out the elo and its change for the players
    win_elo = sum([players[name]['elo'] for name in win_names])
    lose_elo = sum([players[name]['elo'] for name in lose_names])
    actual, expected, delta = elo.calculate_delta(win_elo, lose_elo, win_score, lose_score, k_factor=current_app.config['ELO_K_FACTOR'])

    # Update elo and #games for both losers and winners
    for name in win_names:
        e = players[name]['elo'] + delta / len(win_names)
        g = players[name]['games'] + 1
        await Player.get(name=name).update(elo=e, games=g)
    for name in lose_names:
        e = players[name]['elo'] - delta / len(lose_names)
        g = players[name]['games'] + 1
        await Player.get(name=name).update(elo=e, games=g)

    # Add match to database
    win_str, lose_str = ','.join(win_names), ','.join(lose_names)
    match = await Match.create(
        winners=win_str, 
        losers=lose_str, 
        win_score=win_score, 
        lose_score=lose_score, 
        actual=actual, 
        expected=expected, 
        delta=delta
    )

    return redirect(url_for('officepong.index'))


@officepong_app.route('/recalculate', methods=['POST'])
async def recalculate():
    """
    Recalculate elo scores
    """

    # Get the initialization of every player in the database
    players = {}
    for player in await Player.all():
        players[player.name] = {'elo': current_app.config['ELO_START_VALUE'], 'games': 0}

    # Update each match
    for match in await Match.all().order_by("timestamp"):
        winners = match.winners.split(',')
        losers = match.losers.split(',')
        win_elo = sum([players[name]['elo'] for name in winners])
        lose_elo = sum([players[name]['elo'] for name in losers])
        actual, expected, delta = elo.calculate_delta(win_elo, lose_elo,
                                                      match.win_score, match.lose_score, k_factor=current_app.config['ELO_K_FACTOR'])
        # Update player totals
        for name in winners:
            players[name]['elo'] += delta / len(winners)
            players[name]['games'] += 1
        for name in losers:
            players[name]['elo'] -= delta / len(losers)
            players[name]['games'] += 1

        # Submit match
        await Match.get(timestamp=match.timestamp).update(
            actual=actual,
            expected=expected,
            delta=delta
        )

    # Update each player's elo and # of games played
    for name in players:
        await Player.get(name=name).update(
            elo=players[name]['elo'], 
            games=players[name]['games']
        )

    return redirect(url_for('officepong.index', success="Recalculation finished."))


@officepong_app.route('/')
async def index():
    """
    The main page of the site. Display the dashboard.
    """

    error_msg = request.args.get("error", "")
    success_msg = request.args.get("success", "")
    
    def convert_timestamp(timestamp):
        return datetime.fromtimestamp(int(timestamp)).strftime("%m-%d")

    matches = await Match.all()
    players = await Player.all()
    players_list = sorted(((player.elo, player.name, player.games) for player in players),
                          reverse=True)

    return await render_template('home.html', 
                                 matches=matches, 
                                 players=players_list,
                                 error_msg=f"{error_msg}",
                                 success_msg=f"{success_msg}",
                                 convert_timestamp=convert_timestamp,
                                 )


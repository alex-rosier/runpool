from flask import Flask, render_template, request, redirect, url_for

from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import secrets

from flask_mail import Mail, Message

TEAM_NAME_MAPPING = {
    'Arizona Diamondbacks': 'ARI',
    'Atlanta Braves': 'ATL',
    'Baltimore Orioles': 'BAL',
    'Boston Red Sox': 'BOS',
    'Chicago White Sox': 'CWS',
    'Chicago Cubs': 'CHC',
    'Cincinnati Reds': 'CIN',
    'Cleveland Guardians': 'CLE',
    'Colorado Rockies': 'COL',
    'Detroit Tigers': 'DET',
    'Houston Astros': 'HOU',
    'Kansas City Royals': 'KC',
    'Los Angeles Angels': 'LAA',
    'Los Angeles Dodgers': 'LAD',
    'Miami Marlins': 'MIA',
    'Milwaukee Brewers': 'MIL',
    'Minnesota Twins': 'MIN',
    'New York Yankees': 'NYY',
    'New York Mets': 'NYM',
    'Oakland Athletics': 'OAK',
    'Philadelphia Phillies': 'PHI',
    'Pittsburgh Pirates': 'PIT',
    'San Diego Padres': 'SD',
    'San Francisco Giants': 'SF',
    'Seattle Mariners': 'SEA',
    'St. Louis Cardinals': 'STL',
    'Tampa Bay Rays': 'TB',
    'Texas Rangers': 'TEX',
    'Toronto Blue Jays': 'TOR',
    'Washington Nationals': 'WAS'
}


mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/alexrosier/Projects/Apr-27-RUN-POOL/apr27_run_pool.db'
    db.init_app(app)

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your_email_password'
    mail.init_app(app)

    return app

db = SQLAlchemy()

def update_score(player_id, new_score):
    player = Player.query.get(player_id)
    if player:
        player.score = new_score
        db.session.commit()


app = create_app()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)
    team_id = Column(Integer, ForeignKey('team.id'))  # Add ForeignKey here
    team = relationship("Team", back_populates="users")  # Define the relationship

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    run_total = db.Column(db.Integer, nullable=False)
    game_date = db.Column(db.Date, nullable=False)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', back_populates='team', lazy=True)  # Define the relationship
    scores = db.relationship('Score', backref='team', lazy=True)
    run_totals = db.relationship('RunTotal', secondary='team_run_totals', back_populates='teams')

# Rest of the code remains unchanged.


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    token = db.Column(db.String(32), nullable=False, unique=True)  # Add the token field
    players = db.relationship('Player', backref='game', lazy=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = secrets.token_hex(16)  # Generate a random token when creating a game

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Change nullable to True
    non_registered_player_id = db.Column(db.Integer, db.ForeignKey('non_registered_player.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    user = db.relationship('User', backref='players')
    non_registered_player = db.relationship('NonRegisteredPlayer', backref='players')
    team = db.relationship('Team', backref='players')
    score = db.Column(db.Integer, nullable=True, default=0)  # Add the default value here

class GameScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

class NonRegisteredPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=True, default=0)  # Add the default value here

class RunTotal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    teams = db.relationship('Team', secondary='team_run_totals', back_populates='run_totals')

team_run_totals = db.Table('team_run_totals',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('run_total_id', db.Integer, db.ForeignKey('run_total.id'), primary_key=True)
)


@app.before_request
def create_tables():
    db.create_all()
    if not Team.query.first():
        teams = ['ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SD', 'SF', 'SEA', 'STL', 'TB', 'TEX', 'TOR', 'WAS']
        for name in teams:
            db.session.add(Team(name=name))
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        team_id = request.form['team_id']

                # Check if password and confirm password match
        if password != confirm_password:
            return "Passwords do not match"
        
        password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=name, email=email, password=password, team_id=team_id)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        game = Game(start_date=start_date)
        db.session.add(game)
        db.session.commit()

        team_id = request.form['team_id']
        player = Player(user_id=current_user.id, team_id=team_id, game_id=game.id)
        db.session.add(player)
        db.session.commit()

        return redirect(url_for('view_game', game_id=game.id, scorecard_token=game.token))
    
    # Add the following lines to print all game tokens in the database
        all_games = Game.query.all()
        for g in all_games:
            print(f"Game ID: {g.id}, Game token: {g.token}")

    teams = Team.query.all()
    return render_template('create_game.html', teams=teams)



@app.route('/game/<int:game_id>')
@login_required
def view_game(game_id):
    game = Game.query.get_or_404(game_id)
    teams = Team.query.all()
    players = Player.query.filter_by(game_id=game_id).all()
    scorecard_token = request.args.get('scorecard_token', '')
    return render_template('game.html', game=game, teams=teams, players=players, scorecard_token=scorecard_token)


@app.route('/game/<string:game_token>/scorecard')
def view_scorecard(game_token):
    print(f"Game token: {game_token}")  # Add this print statement
    game = Game.query.filter_by(token=game_token).first_or_404()
    players = Player.query.filter_by(game_id=game.id).all()

    for player in players:
        print(f"Player ID: {player.id}")  # Debug print
        if player.user_id is None and player.non_registered_player_id is not None:
            player.score = player.non_registered_player.score
            print(f"Non-registered player score: {player.score}")  # Debug print

    print(f"Players: {players}")  # Debug print
    return render_template('scorecard.html', game=game, players=players)



@app.route('/game/<int:game_id>/add_player', methods=['POST'])
@login_required
def add_player(game_id):
    game = Game.query.get_or_404(game_id)
    team_id = request.form['team_id']
    player_name = request.form['player_name']

    if Player.query.filter_by(game_id=game_id, team_id=team_id).first():
        return "The selected team is already taken by another player in this game. Please choose a different team.", 400

    user = User.query.filter_by(name=player_name).first()
    if user:
        player = Player(user_id=user.id, team_id=team_id, game_id=game.id, score=0)  # Add score=0 here
    else:
        non_registered_player = NonRegisteredPlayer(name=player_name)
        db.session.add(non_registered_player)
        db.session.flush()  # Flush the session to get the non_registered_player.id
        player = Player(non_registered_player_id=non_registered_player.id, team_id=team_id, game_id=game.id, score=0)  # Add score=0 here


    db.session.add(player)
    db.session.commit()

    return redirect(url_for('view_game', game_id=game.id))


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']

# Check if current password and new password are provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if current_password and new_password:
            # Verify current password
            if bcrypt.check_password_hash(current_user.password, current_password):
                # Update password
                current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            else:
                return "Incorrect current password"

        db.session.commit()
        return redirect(url_for('user_profile'))

    return render_template('profile.html', user=current_user)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            msg = Message('Password Reset Request',
                          sender='noreply@demo.com',
                          recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}
If you did not make this request, please ignore this email.
'''
            mail.send(msg)
        return "If an account with this email exists, a password reset link has been sent."
    return render_template('reset_password_request.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        return "The token is invalid or has expired."
    if request.method == 'POST':
        new_password = request.form['new_password']
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        return "Your password has been reset."
    return render_template('reset_password.html', token=token)


@app.route('/game/<int:game_id>/delete_player/<int:player_id>', methods=['POST'])
@login_required
def delete_player(game_id, player_id):
    player = Player.query.get_or_404(player_id)
    if player.game_id == game_id:
        db.session.delete(player)
        db.session.commit()
    return redirect(url_for('view_game', game_id=game_id))


## UPDATE PLAYER SCORE SECTION
# This function should be called after fetching and processing MLB game scores.

def update_player_scores():
    players = Player.query.all()
    for player in players:
        # Calculate the player's score based on the number of achieved run totals for their selected team.
        player.score = sum(score.run_total for score in player.team.scores)
    db.session.commit()


@app.route('/game/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)

    # Delete all players associated with the game
    Player.query.filter_by(game_id=game.id).delete()

    db.session.delete(game)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/test_gamescore')
def test_gamescore():
    # Create a new GameScore instance
    team = Team.query.first()  # Get the first team in the database
    gamescore = GameScore(team_id=team.id, score=10, date=datetime.today())
    
    # Add it to the database
    db.session.add(gamescore)
    db.session.commit()
    
    # Fetch it back from the database
    fetched_gamescore = GameScore.query.first()
    
    # Return a string representation of the fetched GameScore
    return f'Team ID: {fetched_gamescore.team_id}, Score: {fetched_gamescore.score}, Date: {fetched_gamescore.date}'


@app.route('/all_scores')
def all_scores():
    scores = GameScore.query.all()
    return '\n'.join(str(score.id) + ': ' + str(score.score) for score in scores)


def display_score(score):
    if score is None:
        return "N/A"
    else:
        return str(score)

app.jinja_env.filters['display_score'] = display_score


import statsapi
import schedule
import time
from datetime import datetime, timedelta

def get_final_scores(date):
    # Get the schedule for the specified date
    mlb_schedule = statsapi.schedule(date=date, sportId=1)
    
    # Check if there are any games scheduled for the specified date
    if not mlb_schedule:
        print(f"No games scheduled for {date}.")
        return
    
    # Loop through each game in the schedule
    for game in mlb_schedule:
        # Parse the summary string to get the team names and scores
        summary = game['summary']
        parts = summary.split(' - ')
        if len(parts) < 2:
            continue
        team1_info, team2_info = parts[1].split(' @ ')
        team1_name, team1_score = team1_info.split(' (')
        team2_name, team2_score = team2_info.split(' (', 1)

        team1_name = team1_name.strip()
        team2_name = team2_name.strip()

        team1_score = team1_score.rstrip(')')
        team2_score = team2_score.rstrip(') (Final)')

        print(f"Team 1: {team1_name}, Score: {team1_score}")
        print(f"Team 2: {team2_name}, Score: {team2_score}")

        with app.app_context():
            # Get the Team instances for the two teams
            team1 = Team.query.filter_by(name=TEAM_NAME_MAPPING[team1_name]).first()
            team2 = Team.query.filter_by(name=TEAM_NAME_MAPPING[team2_name]).first()

            if team1 is None or team2 is None:
                print(f"Could not find team(s) in database: {team1_name}, {team2_name}")
                continue

            # Create new GameScore instances for the two teams
            gamescore1 = GameScore(team_id=team1.id, score=int(team1_score), date=datetime.strptime(date, '%m/%d/%Y'))
            gamescore2 = GameScore(team_id=team2.id, score=int(team2_score), date=datetime.strptime(date, '%m/%d/%Y'))

            # Add the new GameScore instances to the database
            db.session.add(gamescore1)
            db.session.add(gamescore2)
        
        # Commit the changes to the database
            db.session.commit()



def job():
    # Get the current date and format it as "MM/DD/YYYY"
    current_date = (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')

    with app.app_context():
        get_final_scores(current_date)
        update_player_scores()  # Update player scores after fetching the MLB scores

import threading

def start_scheduler():
    # Schedule the job to run every day at a specific time (e.g., 8:00 AM)
    schedule.every().day.at("16:00").do(job)

    # Keep the script running and execute the scheduled job
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    # Start the Flask application
    app.run(debug=True)

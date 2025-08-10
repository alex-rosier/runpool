### copy of app_29_test_api.py to focus on error handling and validation

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime, date
import secrets
import pdp

from flask_mail import Mail, Message
import schedule
import time

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

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

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

    db.init_app(app)

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your_email_password'
    mail.init_app(app)

    # Secure session configuration
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True

    return app

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime
    now = datetime.now()
    
    # Get user's active games safely
    try:
        active_games = current_user.players if hasattr(current_user, 'players') else []
    except:
        active_games = []
    
    return render_template('dashboard.html', now=now, active_games=active_games)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)
    team_id = Column(Integer, ForeignKey('team.id'))  # Add ForeignKey here
    team = relationship("Team", back_populates="users")  # Define the relationship

class Score(db.Model): # Stores scores from real-life MLB games
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

    def games_played(self, game_id):
        if game_id is None:
            return 0

        # Get the start_date of the game
        game_start_date = Game.query.get(game_id).start_date

        # Count all unique GameScore instances for this team and this game since the start of the game
        games_played = db.session.query(GameScore.api_game_id).filter(
            GameScore.team_id == self.id,
            GameScore.game_id == game_id,
            GameScore.date >= game_start_date
        ).distinct().count()

        return games_played


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)  # Change this line
    token = db.Column(db.String(32), nullable=False, unique=True)
    players = db.relationship('Player', backref='game', lazy=True)
    scores = db.relationship('GameScore', backref='game', lazy=True)

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

    __table_args__ = (db.UniqueConstraint('user_id', 'non_registered_player_id', 'game_id', name='unique_player'),)


class GameScore(db.Model): # stores the scores achieved in a 13 Run Pool game
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)  # Add this line
    api_game_id = db.Column(db.Integer)  # Add this line
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    final = db.Column(db.Boolean, nullable=False, default=False)  # Add this line

class NonRegisteredPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=True, default=0)  # Add the default value here
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)


class RunTotal(db.Model): # Stores the run totals achieved by teams in 13 Run Pool games
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    teams = db.relationship('Team', secondary='team_run_totals', back_populates='run_totals')

team_run_totals = db.Table('team_run_totals',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('run_total_id', db.Integer, db.ForeignKey('run_total.id'), primary_key=True)
)

class TeamGameRunTotal(db.Model):
    __tablename__ = 'team_game_run_totals'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    run_total = db.Column(db.Integer, nullable=False)

    team = db.relationship('Team', backref=db.backref('team_game_run_totals', lazy=True))
    game = db.relationship('Game', backref=db.backref('team_game_run_totals', lazy=True))



@app.before_request
def create_tables():
    db.create_all()
    if not Team.query.first():
        teams = ['ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SD', 'SF', 'SEA', 'STL', 'TB', 'TEX', 'TOR', 'WAS']
        for name in teams:
            db.session.add(Team(name=name))

    # Ensure all possible run totals exist
    for i in range(0, 13):
        if not RunTotal.query.get(i):
            db.session.add(RunTotal(value=i))

    db.session.commit()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    numbers=1,  # need min. 2 digits
    nonletters=1,  # need min. 2 non-letter characters (digits, specials, anything)
)

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
            flash('Passwords do not match', 'error')
            return render_template('register_email.html')

        # Check if password meets the policy
        if policy.test(password):
            flash('Password is not strong enough. Please choose a stronger password.', 'error')
            return render_template('register_email.html')

        password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=name, email=email, password=password, team_id=team_id)
        db.session.add(user)

        try:
            db.session.commit()
            print("Successfully committed changes to user registration.")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Failed to commit changes to user registration: {e}")
            db.session.rollback()  # Rollback the session to a clean state
            flash('Registration failed. Please try again.', 'error')
            return render_template('register_email.html')
    return render_template('register.html')


@app.route('/register_email')
def register_email():
    return render_template('register_email.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login_new.html')
    return render_template('login_new.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Implement your password reset logic here
        pass
    return render_template('forgot_password.html')

@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        game = Game(start_date=start_date)
        print(f"Game before commit: {game.__dict__}")
        db.session.add(game)
        db.session.commit()
        print(f"Inserted game with ID: {game.id}")
        print(f"Game after commit: {game.__dict__}")

        # Add current user as first player
        current_user_team_id = request.form['team_id']
        current_user_player = Player(user_id=current_user.id, team_id=current_user_team_id, game_id=game.id)
        print(f"Current user player's game_id: {current_user_player.game_id}")
        db.session.add(current_user_player)

        # Retrieve player names and team IDs from the form
        player_names = request.form.getlist('player_names[]')
        team_ids = request.form.getlist('team_id[]')

        # Create additional players and add them to the game
        for name, team_id in zip(player_names, team_ids):
            if name.strip():  # Only process non-empty names
                # Create NonRegisteredPlayer first
                non_registered_player = NonRegisteredPlayer(name=name.strip(), team_id=team_id)
                db.session.add(non_registered_player)
                db.session.flush()  # Get the ID without committing
                
                # Create Player instance linking to NonRegisteredPlayer
                additional_player = Player(
                    user_id=None,  # No registered user
                    non_registered_player_id=non_registered_player.id,
                    team_id=team_id, 
                    game_id=game.id
                )
                print(f"Additional player: {name}, team_id: {team_id}, game_id: {game.id}")
                db.session.add(additional_player)

        # Attempt to commit all changes to the database
        try:
            db.session.commit()
            print(f"Successfully created game {game.id} with {len(player_names) + 1} players")
            flash(f'Game created successfully! Game ID: {game.id}', 'success')
            # Redirect to the game view page with the new game ID
            return redirect(url_for('view_game', game_id=game.id))
        except Exception as e:
            print(f"Failed to commit changes to game creation: {e}")
            db.session.rollback()
            flash('Failed to create game. Please try again.', 'error')
            return render_template('create_game_new.html', teams=teams)

    # Add the following lines to print all game tokens in the database
    all_games = Game.query.all()
    for g in all_games:
        print(f"Game ID: {g.id}, Game token: {g.token}")

    teams = Team.query.all()
    return render_template('create_game_new.html', teams=teams)



@app.route('/game/<int:game_id>')
@login_required
def view_game(game_id):
    game = Game.query.get_or_404(game_id)
    teams = Team.query.all()
    players = Player.query.filter_by(game_id=game_id).all()

    for player in players:
        if player.user_id is None and player.non_registered_player_id is not None:
            player.score = player.non_registered_player.score

    scorecard_token = request.args.get('scorecard_token', '')
    for team in teams:
        print(f'Team {team.name} games played: {team.games_played(game_id)}')
    return render_template('game.html', game=game, teams=teams, players=players, scorecard_token=scorecard_token)


@app.route('/game/<string:game_token>/scorecard')
def view_scorecard(game_token):
    game = Game.query.filter_by(token=game_token).first_or_404()
    teams = Team.query.all()  # Fetch all teams from the database
    players = Player.query.filter_by(game_id=game.id).all()
    team_run_totals = {}  # Create a new dictionary to store the run totals for each team

    # Fetch only the players that are part of the current game
    players = Player.query.filter_by(game_id=game.id).all()

    for player in players:
        if player.user_id is None and player.non_registered_player_id is not None:
            player.score = player.non_registered_player.score

    # Print the player scores
    for player in players:
        print(f"Player {player.id}: score = {player.score}")

    team_run_totals = {}  # Create a new dictionary to store the run totals for each team

    for team in teams:
        run_totals = db.session.query(TeamGameRunTotal.run_total).filter_by(
            team_id=team.id, 
            game_id=game.id
        ).all()
        run_totals = [total[0] for total in run_totals]  # Convert list of tuples to list of integers
        team_run_totals[team.id] = run_totals  # Store the run totals in the dictionary
        print(f'Team {team.name} run_totals: {run_totals}')

    return render_template('scorecard.html', game=game, teams=teams, players=players, team_run_totals=team_run_totals)



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
        player = Player(user_id=user.id, team_id=team_id, game_id=game.id)  # Add score=0 here
        print(f"Player's game_id: {player.game_id}")
    else:
        non_registered_player = NonRegisteredPlayer(name=player_name, team_id=team_id)
        db.session.add(non_registered_player)
        db.session.flush()  # Flush the session to get the non_registered_player.id
        player = Player(non_registered_player_id=non_registered_player.id, team_id=team_id, game_id=game.id)  # Add score=0 here

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
        # Update basic profile information
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        
        # Handle team selection
        team_id = request.form.get('team_id')
        if team_id and team_id != '0':
            team = Team.query.get(team_id)
            if team:
                current_user.team = team
            else:
                flash('Invalid team selected', 'error')
                return redirect(url_for('user_profile'))
        elif team_id == '0':
            current_user.team = None

        # Check if current password and new password are provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if current_password and new_password:
            # Verify current password
            if bcrypt.check_password_hash(current_user.password, current_password):
                # Update password
                current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                flash('Password updated successfully!', 'success')
            else:
                flash('Incorrect current password', 'error')
                return redirect(url_for('user_profile'))
        elif current_password or new_password:
            # User provided one but not both
            flash('Please provide both current and new password', 'error')
            return redirect(url_for('user_profile'))

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile. Please try again.', 'error')
            
        return redirect(url_for('user_profile'))

    # Get all teams for selection
    teams = Team.query.all()
    return render_template('profile.html', user=current_user, teams=teams)


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


@app.route('/auth/google')
def google_auth():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI')]
            }
        },
        scopes=['openid', 'email', 'profile']
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)


@app.route('/auth/google/callback')
def google_callback():
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI')]
                }
            },
            scopes=['openid', 'email', 'profile']
        )
        
        flow.fetch_token(authorization_response=request.url)
        
        # Get user info from Google
        id_info = id_token.verify_oauth2_token(
            flow.credentials.id_token, 
            requests.Request(), 
            os.getenv('GOOGLE_CLIENT_ID')
        )
        
        email = id_info['email']
        name = id_info.get('name', email.split('@')[0])
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # User exists, log them in
            login_user(user)
            flash(f'Welcome, {user.name}!', 'success')
        else:
            # Create new user
            user = User(
                name=name,
                email=email,
                password=bcrypt.generate_password_hash(secrets.token_urlsafe(32)).decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash(f'Welcome, {user.name}!', 'success')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('register'))


@app.route('/game/<int:game_id>/delete_player/<int:player_id>', methods=['POST'])
@login_required
def delete_player(game_id, player_id):
    player = Player.query.get_or_404(player_id)
    if player.game_id == game_id:
        db.session.delete(player)
        db.session.commit()
    return redirect(url_for('view_game', game_id=game_id))

@app.route('/game/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)

    # Delete all players associated with the game
    Player.query.filter_by(game_id=game.id).delete()
    GameScore.query.filter_by(game_id=game.id).delete()

    # Delete all TeamGameRunTotal instances associated with the game
    TeamGameRunTotal.query.filter_by(game_id=game.id).delete()

    db.session.delete(game)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/test_gamescore')
def test_gamescore():
    # Create a new GameScore instance
    team = Team.query.first()  # Get the first team in the database
    game = Game.query.first()  # Get the first game in the database
    gamescore = GameScore(team_id=team.id, game_id=game.id, score=10, date=datetime.today())

    # Add it to the database
    db.session.add(gamescore)
    db.session.commit()
    
    # Fetch it back from the database
    fetched_gamescore = GameScore.query.first()
    
    # Return a string representation of the fetched GameScore
    return f'Team ID: {fetched_gamescore.team_id}, Score: {fetched_gamescore.score}, Date: {fetched_gamescore.date}'

@app.route('/test_update_player_scores')
def test_update_player_scores():
    with app.app_context():
        update_player_scores()
    players = Player.query.all()
    return '\n'.join(str(player.id) + ': ' + str(player.score) for player in players)

@app.route('/test_gamescores/<int:game_id>/<date>')
def test_gamescores(game_id, date):
    # Convert the date string to a datetime.date object
    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Fetch all GameScore instances for the given game_id and date
    gamescores = GameScore.query.filter_by(game_id=game_id, date=date).all()

    # Create a string representation of each GameScore
    gamescore_strings = [f'Team ID: {gamescore.team_id}, Score: {gamescore.score}, Date: {gamescore.date}' for gamescore in gamescores]

    # Join all the strings with newline characters and return the result
    return '\n'.join(gamescore_strings)

@app.route('/test_gamescore/<int:game_id>/<int:team_id>/<date>')
def test_gamescored(game_id, team_id, date):
    # Convert the date string to a datetime.date object
    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Fetch all GameScore instances for the given game_id, team_id and date
    gamescores = GameScore.query.filter_by(game_id=game_id, team_id=team_id, date=date).all()

    # Create a string representation of each GameScore
    gamescore_strings = [f'Team ID: {gamescore.team_id}, Score: {gamescore.score}, Date: {gamescore.date}' for gamescore in gamescores]

    # Join all the strings with newline characters and return the result
    return '\n'.join(gamescore_strings)


@app.route('/test_team_gamescores/<int:team_id>/<date>')
def test_team_gamescores(team_id, date):
    # Convert the date string to a datetime.date object
    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Fetch all GameScore instances for the given team_id and date
    gamescores = GameScore.query.filter_by(team_id=team_id, date=date).all()

    # Create a string representation of each GameScore
    gamescore_strings = [f'Team ID: {gamescore.team_id}, Score: {gamescore.score}, Date: {gamescore.date}' for gamescore in gamescores]

    # Join all the strings with newline characters and return the result
    return '\n'.join(gamescore_strings)

@app.route('/test_gamescore_count/<int:game_id>/<int:team_id>')
def test_gamescore_count(game_id, team_id):
    # Count all GameScore instances for the given game_id and team_id
    gamescore_count = GameScore.query.filter_by(game_id=game_id, team_id=team_id).count()

    # Return the count
    return f'Number of GameScore instances for game ID {game_id} and team ID {team_id}: {gamescore_count}'



@app.route('/all_scores')
def all_scores():
    scores = GameScore.query.all()
    return '\n'.join(str(score.id) + ': ' + str(score.score) for score in scores)


@app.route('/test_scores')
def test_scores():
    scores = Score.query.all()
    return '\n'.join(str(score.id) + ': ' + str(score.score) for score in scores)

@app.route('/all_gamescores')
def all_gamescores():
    gamescores = GameScore.query.all()
    return '\n'.join(f'ID: {gamescore.id}, Team ID: {gamescore.team_id}, Game ID: {gamescore.game_id}, Score: {gamescore.score}, Date: {gamescore.date}' for gamescore in gamescores)


def display_score(score):
    if score is None:
        return "N/A"
    else:
        return str(score)

app.jinja_env.filters['display_score'] = display_score

## UPDATE PLAYER SCORE SECTION
# This function should be called after fetching and processing MLB game scores.

def update_player_scores():
    print("Updating player scores")
    
    try:
        # Get all players
        players = Player.query.all()

        # Loop through each player
        for player in players:
            try:
                # Print the player's score before the update
                print(f"Before update: Player {player.id}: score = {player.score}")
                
                # Get the player's team and game
                team = player.team
                game = player.game

                # Get all unique final scores of the player's team since the start of the game
                gamescores = GameScore.query.filter(
                    GameScore.team_id == team.id, 
                    GameScore.game_id == game.id, 
                    GameScore.date >= game.start_date
                ).all()
                unique_scores = set(gamescore.score for gamescore in gamescores)

                # Calculate the player's score
                new_score = len(unique_scores)

                # If the player is a registered user, update the score in the Player model
                if player.user_id is not None:
                    player.score = new_score
                # If the player is a non-registered user, update the score in the NonRegisteredPlayer model
                elif player.non_registered_player_id is not None:
                    non_registered_player = NonRegisteredPlayer.query.get(player.non_registered_player_id)
                    if non_registered_player:
                        non_registered_player.score = new_score

                # Print the player's score after the update
                print(f"After update: Player {player.id}: score = {new_score}")

            except Exception as e:
                print(f"Error updating player {player.id}: {e}")
                continue

        # Commit all changes at once
        db.session.commit()
        print("Successfully committed all player score changes to database.")
        
    except Exception as e:
        print(f"Failed to update player scores: {e}")
        db.session.rollback()


def update_scorecard():
    print("Updating scorecard")

    # Fetch scores
    current_date = (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')

    # Get all games
    games = Game.query.all()

    # Loop through each game
    for game in games:
        try:
            # Fetch scores for the current game
            scores = get_final_scores(current_date, game.id)
            print(f"Scores for game id {game.id}: {scores}")

            # Check if scores is not None and not empty
            if scores:

                # Loop through each score
                for gamescore in scores:
                    print(f"GameScore: {gamescore}, gamescore.team_id: {gamescore.team_id}")

                    # Get all team_ids
                    all_team_ids = [team.id for team in Team.query.all()]

                    # Check if the gamescore's team_id is in the list of all_team_ids
                    if gamescore.team_id in all_team_ids:

                        # Check if the score is not already in the game's run_totals
                        existing_score = TeamGameRunTotal.query.filter_by(
                            team_id=gamescore.team_id, 
                            game_id=game.id, 
                            run_total=gamescore.score
                        ).first()
                        print(f'Existing score for team_id {gamescore.team_id} and game_id {game.id}: {existing_score}')

                        # If the score doesn't exist yet for this team in this game, create a new entry
                        if existing_score is None:
                            team_game_run_total = TeamGameRunTotal(
                                team_id=gamescore.team_id, 
                                game_id=game.id, 
                                run_total=gamescore.score
                            )
                            print(f"Adding new score {gamescore.score} for team_id {gamescore.team_id} in game {game.id}")
                            db.session.add(team_game_run_total)

        except Exception as e:
            print(f"Error processing game {game.id}: {e}")
            continue

    # Commit all changes at once
    try:
        db.session.commit()
        print("Successfully committed changes to database for updating scorecard.")
    except Exception as e:
        print(f"Failed to update scorecard changes to database: {e}")
        db.session.rollback()


def validate_gamescore_data(team_id, game_id, score, date):
    
    # Check if team_id is not None and is an integer

    if not isinstance(team_id, int):
        return False, "Invalid team_id"

    # Check if game_id is not None and is an integer

    if not isinstance(game_id, int):
        return False, "Invalid game_id"

    # Check if score is not None and is an integer

    if not isinstance(score, int):
        return False, "Invalid score"

    # Check if date is not None and is a datetime.date instance

    if not isinstance(date, datetime):
        return False, "Invalid date"

    return True, "Valid data"


import statsapi
import schedule
import time
from datetime import datetime, timedelta


def get_final_scores(date, game_id):
    print(f"get_final_scores called with date={date} and game_id={game_id}")
    print(f"Fetching scores for {date}")
    
    if game_id is None:
        print("Error: game_id is None")
        return []

    # Get the game ID and start_date of the 13 Run Pool game
    game = Game.query.get(game_id)
    if not game:
        print(f"Error: Game with ID {game_id} not found")
        return []
        
    game_start_date = game.start_date
    print(f"Game ID: {game_id}")
    print(f"Game start date: {game_start_date}")

    # Get the schedule for the specified date
    try:
        mlb_schedule = statsapi.schedule(date=date, sportId=1)
    except Exception as e:
        print(f"Error fetching MLB schedule: {e}")
        return []

    # Check if there are any games scheduled for the specified date
    if not mlb_schedule:
        print(f"No games scheduled for {date}.")
        return []
    
    # Create a list to store the scores
    scores = []
    date_obj = datetime.strptime(date, '%m/%d/%Y')

    # Loop through each game in the schedule
    for mlb_game in mlb_schedule:
        try:
            # Get the unique game ID from the API
            api_game_id = mlb_game['game_id']
            print(f"API Game ID: {api_game_id}")
            
            # Check if the game was completed after the creation of the 13 Run Pool game
            game_datetime = datetime.strptime(mlb_game['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')
            if game_start_date is not None and game_datetime <= game_start_date:
                print(f"Skipping game {api_game_id} - completed before pool game start")
                continue

            # Parse the summary string to get the team names and scores
            summary = mlb_game['summary']
            print(f"Game summary: {summary}")

            # Skip games that are "Scheduled"
            if 'Scheduled' in summary:
                print(f"Skipping scheduled game {api_game_id}")
                continue
            
            parts = summary.split(' - ')
            if len(parts) < 2:
                print(f"Could not parse summary: {summary}")
                continue
                
            team1_info, team2_info = parts[1].split(' @ ')
            
            # Check if the team info strings contain a score
            if ' (' not in team1_info or ' (' not in team2_info:
                print(f"Could not parse scores from summary: {summary}")
                continue

            team1_name, team1_score = team1_info.split(' (')
            team2_name, team2_score = team2_info.split(' (', 1)

            team1_name = team1_name.strip()
            team2_name = team2_name.strip()
            team1_score = team1_score.rstrip(')')
            team2_score = team2_score.rstrip(') (Final)')

            print(f"Team 1: {team1_name}, Score: {team1_score}")
            print(f"Team 2: {team2_name}, Score: {team2_score}")

            # Get the Team instances for the two teams
            team1 = Team.query.filter_by(name=TEAM_NAME_MAPPING.get(team1_name)).first()
            team2 = Team.query.filter_by(name=TEAM_NAME_MAPPING.get(team2_name)).first()

            if team1 is None or team2 is None:
                print(f"Could not find team(s) in database: {team1_name}, {team2_name}")
                continue

            # Check if GameScore instances already exist for the same team, game, date, and score
            existing_gamescore1 = GameScore.query.filter_by(
                team_id=team1.id, 
                game_id=game_id, 
                date=date_obj, 
                api_game_id=api_game_id, 
                score=int(team1_score)
            ).first()
            
            existing_gamescore2 = GameScore.query.filter_by(
                team_id=team2.id, 
                game_id=game_id, 
                date=date_obj, 
                api_game_id=api_game_id, 
                score=int(team2_score)
            ).first()

            # Create new GameScore instances only if they don't exist
            if existing_gamescore1 is None:
                try:
                    valid, message = validate_gamescore_data(team1.id, game_id, int(team1_score), date_obj)
                    if not valid:
                        print(f"Validation failed for team1: {message}")
                        continue

                    gamescore1 = GameScore(
                        team_id=team1.id, 
                        game_id=game_id, 
                        api_game_id=api_game_id, 
                        score=int(team1_score), 
                        date=date_obj
                    )
                    print(f"Adding GameScore to database: {gamescore1}")
                    db.session.add(gamescore1)
                    scores.append(gamescore1)
                except Exception as e:
                    print(f"Error creating GameScore for team1: {e}")
                    continue

            if existing_gamescore2 is None:
                try:
                    valid, message = validate_gamescore_data(team2.id, game_id, int(team2_score), date_obj)
                    if not valid:
                        print(f"Validation failed for team2: {message}")
                        continue

                    gamescore2 = GameScore(
                        team_id=team2.id, 
                        game_id=game_id, 
                        api_game_id=api_game_id, 
                        score=int(team2_score), 
                        date=date_obj
                    )
                    print(f"Adding GameScore to database: {gamescore2}")
                    db.session.add(gamescore2)
                    scores.append(gamescore2)
                except Exception as e:
                    print(f"Error creating GameScore for team2: {e}")
                    continue

        except Exception as e:
            print(f"Error processing MLB game: {e}")
            continue

    # Commit all changes at once
    if scores:
        try:
            db.session.commit()
            print(f"Successfully committed {len(scores)} new GameScore instances")
        except Exception as e:
            print(f"Failed to commit GameScore changes: {e}")
            db.session.rollback()
            return []

    return scores

import threading

# Create a lock object
job_lock = threading.Lock()

def job():
    global job_lock

    # Check if the lock is locked, i.e., the job is already running
    if job_lock.locked():
        print(f"Job is already running.")
        return

    # Lock the lock
    job_lock.acquire()

    try:
        print(f"Running job at {datetime.now()}")
        # Get the current date and format it as "MM/DD/YYYY"
        current_date = (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')

        with app.app_context():
            # Get all games
            games = Game.query.all()
            for game in games:
                get_final_scores(current_date, game.id)
            update_scorecard()  # Move this line outside of the loop
            update_player_scores()  # Update player scores after fetching the MLB scores
    finally:
        # Release the lock
        job_lock.release()

def start_scheduler():
    # Check if the job is already scheduled
    if not schedule.get_jobs():
        # Schedule the job to run every day at a specific time (e.g., 8:00 AM)
        schedule.every().day.at("21:09:10").do(job)

    # Keep the script running and execute the scheduled job
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    # Start the Flask application on port 5001 (5000 is used by macOS AirPlay)
    app.run(debug=True, port=5001)

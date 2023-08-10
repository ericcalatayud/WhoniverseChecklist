import os
import csv
from sqlalchemy import Column, Integer, String, text, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from flask import Flask, render_template, redirect, session, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

db_host = os.getenv('DB_HOST', '34.175.107.217')
db_user = os.getenv('DB_USER', 'ua3f8sxgh5ouk')
db_password = os.getenv('DB_PASSWORD', 'nanoerik00who')
db_name = os.getenv('DB_NAME', 'db7wbjghd927hc')

app = Flask(__name__)
app.secret_key = '¿9.12del22#'
connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
engine = create_engine(connection_string, pool_pre_ping=True)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Category(db.Model):
    __tablename__ = 'categories'
    id_category = Column(Integer, primary_key=True)
    category = Column(String(255), nullable=False)

class Option(db.Model):
    __tablename__ = 'options'
    id_option = Column(Integer, primary_key=True)
    option = Column(String(255), nullable=False)
    id_category = Column(Integer, ForeignKey('categories.id_category'), nullable=False)

class Season(db.Model):
    __tablename__ = 'seasons'
    id_season = Column(Integer, primary_key=True)
    season = Column(String(255), nullable=False)
    id_option = Column(Integer, ForeignKey('options.id_option'), nullable=False)

class Episode(db.Model):
    __tablename__ = 'episodes'
    id_episode = Column(String(25), primary_key=True)
    episode = Column(String(255), nullable=False)
    id_season = Column(Integer, ForeignKey('seasons.id_season'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class EpisodesWatched(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_episode = db.Column(db.String(25), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def is_user_logged_in():
    return 'user' in session

@app.route('/')
def index():
    if is_user_logged_in():
        return redirect(url_for('whoniverse'))
    else:
        return redirect(url_for('login'))
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        hashed_password = generate_password_hash(password, method='sha256')

        # Crear un nuevo usuario en la base de datos
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_email = request.form['username_email']
        password = request.form['password']
        user = User.query.filter_by(username=username_email).first() or User.query.filter_by(email=username_email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('whoniverse'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/check_login')
def check_login():
    if current_user.is_authenticated:
        return jsonify({"status": "authenticated"})
    else:
        return jsonify({"status": "not_authenticated"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/whoniverse')
@login_required
def whoniverse():
    return render_template('whoniverse.html')

@app.route('/api/options/<category_id>')
@login_required
def get_options(category_id):
    with engine.connect() as con:
        query = text("SELECT * FROM options WHERE id_category = :id_category")
        result = con.execute(query, id_category=category_id)

        options = [dict(row) for row in result]
        return jsonify(options)

@app.route('/api/seasons/<option_id>')
@login_required
def get_seasons(option_id):
    with engine.connect() as con:
        query = text("SELECT * FROM seasons WHERE id_option = :id_option")
        result = con.execute(query, id_option=option_id)

        seasons = [dict(row) for row in result]
        return jsonify(seasons)

@app.route('/api/episodes/<season_id>')
@login_required
def get_episodes(season_id):
    with engine.connect() as con:
        query = text("SELECT * FROM episodes WHERE id_season = :id_season")
        result = con.execute(query, id_season=season_id)

        episodes = [dict(row) for row in result]
        return jsonify(episodes)

@app.route('/api/episode_watched', methods=['POST'])
@login_required
def mark_episode_watched():
    id_episode = request.json['id_episode']
    episode_watched = EpisodesWatched(id_user=current_user.id, id_episode=id_episode)
    db.session.add(episode_watched)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/episodes_watched')
@login_required
def get_episodes_watched():
    episodes_watched = EpisodesWatched.query.filter_by(id_user=current_user.id).all()
    return jsonify([episode.id_episode for episode in episodes_watched])

@app.route('/api/episode_unwatched', methods=['POST'])
@login_required
def unmark_episode_watched():
    id_episode = request.json['id_episode']
    episode_watched = EpisodesWatched.query.filter_by(id_user=current_user.id, id_episode=id_episode).first()
    if episode_watched:
        db.session.delete(episode_watched)
        db.session.commit()
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Episode not found"}), 404

if __name__ == '__main__':
    with app.app_context():        
        app.run(debug=True)

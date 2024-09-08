from flask import Flask, abort, render_template, request, redirect, url_for, flash, jsonify, Blueprint, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from math import ceil, sqrt
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import requests
import os
import random
import uuid
from sqlalchemy.exc import IntegrityError, PendingRollbackError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with your own secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chrono.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Configuring the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB
@app.errorhandler(413)
def file_too_large(e):
    return "File is too large. Maximum upload size is 1MB.", 413
@app.errorhandler(400)
def invalid_file_type(e):
    return "Invalid file type. Only image files (png, jpg, jpeg, gif) are allowed.", 400
migrate = Migrate(app, db)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
clubs_bp = Blueprint('clubs', __name__)

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class UploadForm(FlaskForm):
    photo = FileField('Upload Profile Picture')
    submit = SubmitField('Upload')

# Form for uploading banner picture
class BannerForm(FlaskForm):
    banner = FileField('Upload Banner Image')
    submit = SubmitField('Upload')

@app.route('/dp', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        original_filename = secure_filename(form.photo.data.filename)
        _, file_extension = os.path.splitext(original_filename)
        if allowed_file(file_extension):
            new_filename = f"dp_{current_user.id}{file_extension}"
            upload_folder = app.config['UPLOADED_PHOTOS_DEST']
        
            # Debug: print the paths
            print("Upload Folder:", upload_folder)
            print("Filename:", new_filename)
        
            # Ensure the upload directory exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                print("Directory created:", upload_folder)
        
            filepath = os.path.join(upload_folder, new_filename)
            print("Filepath:", filepath)  # Debug: print the filepath
        
            # Save the file
            try:
                form.photo.data.save(filepath)
                print("File saved successfully.")
            except Exception as e:
                print("Error saving file:", str(e))  # Debug: print the error
        
            current_user.profile_image = new_filename
            db.session.commit()

            flash('Photo uploaded successfully', 'success')
            return redirect(url_for('home'))    
        else:
            abort(400)  # Invalid file type
    return render_template('dp.html', form=form, )

# Route for uploading banner image
@app.route('/upload_banner', methods=['GET', 'POST'])
@login_required
def upload_banner():
    form = BannerForm()
    if form.validate_on_submit():
        filename = secure_filename(form.banner.data.filename)
        upload_folder = app.config['UPLOADED_BANNERS_DEST']
        
        # Ensure the upload directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        form.banner.data.save(filepath)
        
        current_user.banner_image = filename
        db.session.commit()
        
        flash('Banner image uploaded successfully', 'success')
        return redirect(url_for('profile'))
    return render_template('upload_banner.html', form=form)

search_bp = Blueprint('search', __name__, url_prefix='/search')

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    xp_count = db.Column(db.Integer, default=0)
    birthdate = db.Column(db.Date, nullable=False)
    display_name = db.Column(db.String(150), default='Chrono-user ')
    bio = db.Column(db.Text)
    youtube = db.Column(db.Text, nullable=False, default="N/A")
    facebook = db.Column(db.Text, nullable=False, default="N/A")
    twitter = db.Column(db.Text, nullable=False, default="N/A")
    insta = db.Column(db.Text, nullable=False, default="N/A")
    tiktok = db.Column(db.Text, nullable=False, default="N/A")
    level = db.Column(db.Integer, default=0)
    profile_image = db.Column(db.String(150), nullable=True, default='Default.png')
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    league = db.Column(db.String(80), nullable=False, default='Tantalum')
    yt_badge = db.Column(db.Boolean, default=False)
    account_type = db.Column(db.Text, default='Free')
    club_name = db.Column(db.String(150))
    # Relationship with the club
    club = db.relationship('Club', backref=db.backref('members', lazy=True), foreign_keys=[club_id])
    # Relationship with followers
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    # Relationship with users being followed
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
                                
class Schedule(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = {'extend_existing': True}  # Add this line to avoid the table redefinition error
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))  # Ensure this matches your actual column name and type
    date = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.Integer)
    type = db.Column(db.String(50))
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each club
    name = db.Column(db.String(100), nullable=False)  # Club name
    description = db.Column(db.Text)  # Club description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the club was created
    codename = db.Column(db.String(50), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    other_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Another foreign key

    creator = db.relationship('User', foreign_keys=[creator_id])
    other_user = db.relationship('User', foreign_keys=[other_user_id])

class UserClub(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # ID of the user
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), primary_key=True)  # ID of the club
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the user joined the club
    role = db.Column(db.String(50), default='member')  # User role in the club (e.g., member, admin)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.Column(db.PickleType, nullable=False)
    answer = db.Column(db.String(50), nullable=False)

class ClubAnnouncements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcer = db.Column(db.Integer, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    date = db.Column(db.Text, nullable=False)

    club = db.relationship('Club', foreign_keys=[club_id])

class ClubEvents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    date = db.Column(db.Text, nullable=False)

    club = db.relationship('Club', foreign_keys=[club_id])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    if request.method == 'POST':
        description = request.form.get('description')
        date_str = request.form.get('date')
        priority = request.form.get('priority')
        type = request.form.get('type')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            new_task = Schedule(description=description, date=date, priority=priority, type=type, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('manage_tasks'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')

    tasks = Schedule.query.filter_by(user_id=current_user.id).order_by(Schedule.date.asc()).all()
    tasks_completed = Schedule.query.filter_by(user_id=current_user.id, done=True).count()
    tasks_total = Schedule.query.filter_by(user_id=current_user.id).count()

    tasks_completed_percent = int(tasks_completed / tasks_total * 100) if tasks_total > 0 else 0
    len_t = len(tasks)

    return render_template('tasks.html', tasks=tasks, tasks_completed=tasks_completed,
                           tasks_completed_percent=tasks_completed_percent, len_t=len_t)

# Callback to reload user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            birthdate = request.form['birthdate']
            birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()

            # Check if username or email already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('Username or Email already exists. Please choose another.', 'error')
                return render_template('registration_error.html')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, email=email, password=hashed_password, birthdate=birthdate)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')
    except IntegrityError:
        return render_template('registration_error.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for home page
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect( url_for( 'dashboard' ))
    else:
        return render_template('index.html')

@app.route('/api/tasks/first_three', methods=['GET'])
@login_required
def get_first_three_tasks():
    tasks = Schedule.query.filter_by(user_id=current_user.id).order_by(Schedule.date).limit(5).all()
    return jsonify([{ 'description': Schedule.description, 'date': Schedule.date.strftime('%Y-%m-%d')} for task in tasks])

def get_users_by_league(league):
    return User.query.filter_by(league=current_user.league).all().limit(25)

# Route for dashboard page
@app.route('/dashboard/')
@login_required
def dashboard():
    league = current_user.league
    task_count = 0
    users = User.query.filter_by(league=current_user.league).limit(25).all()
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    for i in schedules:
        task_count += 1                
    first_three_tasks = Schedule.query.filter_by(user_id=current_user.id).order_by(Schedule.date).limit(5).all()
    return render_template('dashboard.html', schedules=schedules, tasks=first_three_tasks, username=current_user.username, task_count=task_count, users=users, league=current_user.league)

@app.route('/mark_task_done/<int:task_id>', methods=['POST'])
@login_required
def mark_task_done(task_id):
    task = Schedule.query.get_or_404(task_id)
    task.done = True
    current_user.xp_count += 10
    current_user.league = determine_league(current_user.xp_count)
    db.session.commit()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks'))

# Example Route to Render tasks.html
@app.route('/tasks')
def tasks():
    tasks = Schedule.query.all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/update_xp/<int:xp>', methods=['POST'])
@login_required
def update_xp(xp):
    current_user.xp_count += xp
    db.session.commit()
    return jsonify({'message': 'XP updated successfully'})

@app.route('/progress')
@login_required
def progress():
    xp_earned = current_user.xp_count

    if xp_earned <= 100:
        level = 0
        level_xp = 100
    elif xp_earned <= 250:
        level = 1
        level_xp = 250
    elif xp_earned <= 500:
        level = 2
        level_xp = 500
    elif xp_earned <= 800:
        level = 3
        level_xp = 800
    elif xp_earned <= 1200:
        level = 4
        level_xp = 1200
    elif xp_earned <= 1700:
        level = 5
        level_xp = 1700
    elif xp_earned <= 2300:
        level = 6
        level_xp = 2300
    elif xp_earned <= 3000:
        level = 7
        level_xp = 3000
    elif xp_earned <= 3800:
        level = 8
        level_xp = 3800
    elif xp_earned <= 4700:
        level = 9
        level_xp = 4700
    elif xp_earned <= 5700:
        level = 10
        level_xp = 5700
    elif xp_earned <= 6800:
        level = 11
        level_xp = 6800
    elif xp_earned <= 8000:
        level = 12
        level_xp = 8000
    elif xp_earned <= 9300:
        level = 13
        level_xp = 9300
    elif xp_earned <= 10700:
        level = 14
        level_xp = 10700
    elif xp_earned <= 12200:
        level = 15
        level_xp = 12200
    elif xp_earned <= 13800:
        level = 16
        level_xp = 13800
    elif xp_earned <= 15500:
        level = 17
        level_xp = 15500
    elif xp_earned <= 17300:
        level = 18
        level_xp = 17300
    elif xp_earned <= 19200:
        level = 19
        level_xp = 19200
    elif xp_earned <= 21200:
        level = 20
        level_xp = 21200
    elif xp_earned <= 23300:
        level = 21
        level_xp = 23300
    elif xp_earned <= 25500:
        level = 22
        level_xp = 25500
    elif xp_earned <= 27800:
        level = 23
        level_xp = 27800
    elif xp_earned <= 30200:
        level = 24
        level_xp = 30200
    elif xp_earned <= 32700:
        level = 25
        level_xp = 32700
    elif xp_earned <= 35300:
        level = 26
        level_xp = 35300
    elif xp_earned <= 38000:
        level = 27
        level_xp = 38000
    elif xp_earned <= 40800:
        level = 28
        level_xp = 40800
    elif xp_earned <= 43700:
        level = 29
        level_xp = 43700
    elif xp_earned <= 46700:
        level = 30
        level_xp = 46700
    elif xp_earned <= 49800:
        level = 31
        level_xp = 49800
    elif xp_earned <= 53000:
        level = 32
        level_xp = 53000
    elif xp_earned <= 56300:
        level = 33
        level_xp = 56300
    elif xp_earned <= 59700:
        level = 34
        level_xp = 59700
    elif xp_earned <= 63200:
        level = 35
        level_xp = 63200
    elif xp_earned <= 66800:
        level = 36
        level_xp = 66800
    elif xp_earned <= 70500:
        level = 37
        level_xp = 70500
    elif xp_earned <= 74300:
        level = 38
        level_xp = 74300
    elif xp_earned <= 78200:
        level = 39
        level_xp = 78200
    elif xp_earned <= 82200:
        level = 40
        level_xp = 82200
    elif xp_earned <= 86300:
        level = 41
        level_xp = 86300
    elif xp_earned <= 90500:
        level = 42
        level_xp = 90500
    elif xp_earned <= 94800:
        level = 43
        level_xp = 94800
    elif xp_earned <= 99200:
        level = 44
        level_xp = 99200
    elif xp_earned <= 103700:
        level = 45
        level_xp = 103700
    elif xp_earned <= 108300:
        level = 46
        level_xp = 108300
    elif xp_earned <= 113000:
        level = 47
        level_xp = 113000
    elif xp_earned <= 117800:
        level = 48
        level_xp = 117800
    elif xp_earned <= 122700:
        level = 49
        level_xp = 122700
    elif xp_earned <= 125000:
        level = 50
        level_xp = 125000


    xp_percent = int(xp_earned / level_xp * 100) if level_xp >= 0 else 0
    current_user.level = level
    db.session.commit()

    return render_template('progress.html', xp_earned=xp_earned, xp_percent=xp_percent, level=level, level_xp=level_xp)

@app.route('/lvlmobile')
@login_required
def lvl_mobile():
    xp_earned = current_user.xp_count

    if xp_earned <= 100:
        level = 0
        level_xp = 100
    elif xp_earned <= 250:
        level = 1
        level_xp = 250
    elif xp_earned <= 500:
        level = 2
        level_xp = 500
    elif xp_earned <= 800:
        level = 3
        level_xp = 800
    elif xp_earned <= 1200:
        level = 4
        level_xp = 1200
    elif xp_earned <= 1700:
        level = 5
        level_xp = 1700
    elif xp_earned <= 2300:
        level = 6
        level_xp = 2300
    elif xp_earned <= 3000:
        level = 7
        level_xp = 3000
    elif xp_earned <= 3800:
        level = 8
        level_xp = 3800
    elif xp_earned <= 4700:
        level = 9
        level_xp = 4700
    elif xp_earned <= 5700:
        level = 10
        level_xp = 5700
    elif xp_earned <= 6800:
        level = 11
        level_xp = 6800
    elif xp_earned <= 8000:
        level = 12
        level_xp = 8000
    elif xp_earned <= 9300:
        level = 13
        level_xp = 9300
    elif xp_earned <= 10700:
        level = 14
        level_xp = 10700
    elif xp_earned <= 12200:
        level = 15
        level_xp = 12200
    elif xp_earned <= 13800:
        level = 16
        level_xp = 13800
    elif xp_earned <= 15500:
        level = 17
        level_xp = 15500
    elif xp_earned <= 17300:
        level = 18
        level_xp = 17300
    elif xp_earned <= 19200:
        level = 19
        level_xp = 19200
    elif xp_earned <= 21200:
        level = 20
        level_xp = 21200
    elif xp_earned <= 23300:
        level = 21
        level_xp = 23300
    elif xp_earned <= 25500:
        level = 22
        level_xp = 25500
    elif xp_earned <= 27800:
        level = 23
        level_xp = 27800
    elif xp_earned <= 30200:
        level = 24
        level_xp = 30200
    elif xp_earned <= 32700:
        level = 25
        level_xp = 32700
    elif xp_earned <= 35300:
        level = 26
        level_xp = 35300
    elif xp_earned <= 38000:
        level = 27
        level_xp = 38000
    elif xp_earned <= 40800:
        level = 28
        level_xp = 40800
    elif xp_earned <= 43700:
        level = 29
        level_xp = 43700
    elif xp_earned <= 46700:
        level = 30
        level_xp = 46700
    elif xp_earned <= 49800:
        level = 31
        level_xp = 49800
    elif xp_earned <= 53000:
        level = 32
        level_xp = 53000
    elif xp_earned <= 56300:
        level = 33
        level_xp = 56300
    elif xp_earned <= 59700:
        level = 34
        level_xp = 59700
    elif xp_earned <= 63200:
        level = 35
        level_xp = 63200
    elif xp_earned <= 66800:
        level = 36
        level_xp = 66800
    elif xp_earned <= 70500:
        level = 37
        level_xp = 70500
    elif xp_earned <= 74300:
        level = 38
        level_xp = 74300
    elif xp_earned <= 78200:
        level = 39
        level_xp = 78200
    elif xp_earned <= 82200:
        level = 40
        level_xp = 82200
    elif xp_earned <= 86300:
        level = 41
        level_xp = 86300
    elif xp_earned <= 90500:
        level = 42
        level_xp = 90500
    elif xp_earned <= 94800:
        level = 43
        level_xp = 94800
    elif xp_earned <= 99200:
        level = 44
        level_xp = 99200
    elif xp_earned <= 103700:
        level = 45
        level_xp = 103700
    elif xp_earned <= 108300:
        level = 46
        level_xp = 108300
    elif xp_earned <= 113000:
        level = 47
        level_xp = 113000
    elif xp_earned <= 117800:
        level = 48
        level_xp = 117800
    elif xp_earned <= 122700:
        level = 49
        level_xp = 122700
    elif xp_earned <= 125000:
        level = 50
        level_xp = 125000


    xp_percent = int(xp_earned / level_xp * 100) if level_xp >= 0 else 0
    current_user.level = level
    db.session.commit()

    return render_template('lvlm.html', xp_earned=xp_earned, xp_percent=xp_percent, level=level, level_xp=level_xp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/resources')
@login_required
def resources():
    return render_template('resources.html')

@app.route('/resources/academics')
@login_required
def resources_academics():
    return render_template('/resources/academics.html')

@app.route('/resources/academics/grade6')
@login_required
def resources_academics_grade6():
    return render_template('/resources/academics/grade6.html')

@app.route('/resources/academics/grade7')
@login_required
def resources_academics_grade7():
    return render_template('/resources/academics/grade7.html')

@app.route('/resources/academics/grade8')
@login_required
def resources_academics_grade8():
    return render_template('/resources/academics/grade8.html')

@app.route('/resources/academics/grade9')
@login_required
def resources_academics_grade9():
    return render_template('/resources/academics/grade9.html')

@app.route('/resources/academics/grade10')
@login_required
def resources_academics_grade10():
    return render_template('/resources/academics/grade10.html')
    
@app.route('/resources/academics/grade11')
@login_required
def resources_academics_grade11():
    return render_template('/resources/academics/grade11.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/settings')
@login_required
def settings():
    user = User.query.get(current_user.id)
    form = UploadForm()    
    if form.validate_on_submit():
        filename = secure_filename(form.photo.data.filename)
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
        form.photo.data.save(filepath)
        
        current_user.profile_image = filename
        db.session.commit()
        
        flash('Profile picture updated successfully', 'success')
    return render_template('edit_profile.html', user=user, form=form)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(current_user.id)
    form = UploadForm()
    user.display_name = request.form.get('display_name')
    user.bio = request.form.get('bio')
    user.youtube = request.form.get('youtube')
    user.facebook = request.form.get('facebook')
    user.twitter = request.form.get('twitter')
    user.insta = request.form.get('insta')
    user.tiktok = request.form.get('tiktok')
    
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = profile_picture.filename
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_image = User(profile_picture=filename, user_id=user.id)
            db.session.add(new_image)
            db.session.commit()
    
    if 'banner_picture' in request.files:
        banner_picture = request.files['banner_picture']
        if banner_picture and allowed_file(banner_picture.filename):
            filename = secure_filename(banner_picture.filename)
            banner_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.banner_picture = filename
    
    if request.method == 'POST':
        current_user.display_name = request.form.get('display_name')
        current_user.bio = request.form.get('bio')
        current_user.youtube = request.form.get('youtube')
        current_user.facebook = request.form.get('facebook')
        current_user.twitter = request.form.get('twitter')
        current_user.insta = request.form.get('insta')
        current_user.tiktok = request.form.get('tiktok')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_profile.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required  # Ensure the user is logged in
def follow_user(user_id):
    action = request.json.get('action')
    user = User.query.get_or_404(user_id)
    follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()

    if action == 'follow' and not follow:
        new_follow = Follow(follower_id=current_user.id, followed_id=user.id)
        db.session.add(new_follow)
        db.session.commit()
        return jsonify({'status': 'success', 'action': 'follow'})
    elif action == 'unfollow' and follow:
        db.session.delete(follow)
        db.session.commit()
        return jsonify({'status': 'success', 'action': 'unfollow'})
    return jsonify({'status': 'error'})

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    is_following = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first() is not None
    followers = user.followers.all()  # Fetch all followers
    follower_users = [User.query.get(f.follower_id) for f in followers]
    level = user.level  # Fetch all followers
    profile_image = str(user.profile_image)
    xp_earned = user.xp_count

    if xp_earned <= 100:
        level = 0
        level_xp = 100
    elif xp_earned <= 250:
        level = 1
        level_xp = 250
    elif xp_earned <= 500:
        level = 2
        level_xp = 500
    elif xp_earned <= 800:
        level = 3
        level_xp = 800
    elif xp_earned <= 1200:
        level = 4
        level_xp = 1200
    elif xp_earned <= 1700:
        level = 5
        level_xp = 1700
    elif xp_earned <= 2300:
        level = 6
        level_xp = 2300
    elif xp_earned <= 3000:
        level = 7
        level_xp = 3000
    elif xp_earned <= 3800:
        level = 8
        level_xp = 3800
    elif xp_earned <= 4700:
        level = 9
        level_xp = 4700
    elif xp_earned <= 5700:
        level = 10
        level_xp = 5700
    elif xp_earned <= 6800:
        level = 11
        level_xp = 6800
    elif xp_earned <= 8000:
        level = 12
        level_xp = 8000
    elif xp_earned <= 9300:
        level = 13
        level_xp = 9300
    elif xp_earned <= 10700:
        level = 14
        level_xp = 10700
    elif xp_earned <= 12200:
        level = 15
        level_xp = 12200
    elif xp_earned <= 13800:
        level = 16
        level_xp = 13800
    elif xp_earned <= 15500:
        level = 17
        level_xp = 15500
    elif xp_earned <= 17300:
        level = 18
        level_xp = 17300
    elif xp_earned <= 19200:
        level = 19
        level_xp = 19200
    elif xp_earned <= 21200:
        level = 20
        level_xp = 21200
    elif xp_earned <= 23300:
        level = 21
        level_xp = 23300
    elif xp_earned <= 25500:
        level = 22
        level_xp = 25500
    elif xp_earned <= 27800:
        level = 23
        level_xp = 27800
    elif xp_earned <= 30200:
        level = 24
        level_xp = 30200
    elif xp_earned <= 32700:
        level = 25
        level_xp = 32700
    elif xp_earned <= 35300:
        level = 26
        level_xp = 35300
    elif xp_earned <= 38000:
        level = 27
        level_xp = 38000
    elif xp_earned <= 40800:
        level = 28
        level_xp = 40800
    elif xp_earned <= 43700:
        level = 29
        level_xp = 43700
    elif xp_earned <= 46700:
        level = 30
        level_xp = 46700
    elif xp_earned <= 49800:
        level = 31
        level_xp = 49800
    elif xp_earned <= 53000:
        level = 32
        level_xp = 53000
    elif xp_earned <= 56300:
        level = 33
        level_xp = 56300
    elif xp_earned <= 59700:
        level = 34
        level_xp = 59700
    elif xp_earned <= 63200:
        level = 35
        level_xp = 63200
    elif xp_earned <= 66800:
        level = 36
        level_xp = 66800
    elif xp_earned <= 70500:
        level = 37
        level_xp = 70500
    elif xp_earned <= 74300:
        level = 38
        level_xp = 74300
    elif xp_earned <= 78200:
        level = 39
        level_xp = 78200
    elif xp_earned <= 82200:
        level = 40
        level_xp = 82200
    elif xp_earned <= 86300:
        level = 41
        level_xp = 86300
    elif xp_earned <= 90500:
        level = 42
        level_xp = 90500
    elif xp_earned <= 94800:
        level = 43
        level_xp = 94800
    elif xp_earned <= 99200:
        level = 44
        level_xp = 99200
    elif xp_earned <= 103700:
        level = 45
        level_xp = 103700
    elif xp_earned <= 108300:
        level = 46
        level_xp = 108300
    elif xp_earned <= 113000:
        level = 47
        level_xp = 113000
    elif xp_earned <= 117800:
        level = 48
        level_xp = 117800
    elif xp_earned <= 122700:
        level = 49
        level_xp = 122700
    elif xp_earned <= 125000:
        level = 50
        level_xp = 125000


    xp_percent = int(xp_earned / level_xp * 100) if level_xp >= 0 else 0
    return render_template('profile.html', username=username, xp_earned=xp_earned, level_xp=level_xp, xp_percent=xp_percent, user=user, is_following=is_following, followers=follower_users, level=level, profile_image=profile_image)

@app.route('/followers/<int:user_id>')
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    followers = user.followers.all()  # Fetch all followers
    follower_users = [User.query.get(f.follower_id) for f in followers]
    len_f = len(follower_users)
    
    return render_template('followers.html', user=user, followers=follower_users, len_f=len_f)

@search_bp.route('/users', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip()

    if query:
        # Perform search in database
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    else:
        users = []

    return render_template('search_results.html', query=query, users=users)

app.register_blueprint(search_bp)

@clubs_bp.route('/clubs', methods=['GET'])
def list_clubs():
    clubs = Club.query.all()    
    query = request.args.get('q', '')
    if query:
        clubs = Club.query.filter(Club.name.ilike(f'%{query}%')).all()
    else:
        clubs = Club.query.all()

    return render_template('clubs/list.html', clubs=clubs)

@clubs_bp.route('/clubs/create', methods=['GET', 'POST'])
def create_club():
    is_exist = False
    try:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            codename = request.form['codename']
            creator_id = current_user.id  # Assuming you're using Flask-Login
            new_club = Club(name=name, description=description, creator_id=creator_id, codename=codename)
            current_user.club_name = codename
            db.session.add(new_club)
            db.session.commit()
            return redirect(url_for('clubs.list_clubs'))
        return render_template('/clubs/create.html')
    except (IntegrityError, PendingRollbackError):
        db.session.rollback()
        return render_template('/clubs/alreadycc.html')

@clubs_bp.route('/clubs/<int:club_id>', methods=['GET'])
@login_required
def view_club(club_id):
    club = Club.query.get_or_404(club_id)
    msg = ClubAnnouncements.query.all()
    events = ClubEvents.query.filter_by(club_id=club.id).all()
    annz = []
    ian = len(annz)
    for i in msg:
        if i.club_id == club.id:
            annz.append(i)
    annx = sorted(annz, key=lambda i: i.id, reverse=True)
    anns = annx[:6]
    if len(annz) >= 7:
        old_ann = ClubAnnouncements.query.filter_by(club_id=club.id).first()
        db.session.delete(old_ann)
        db.session.commit()
    if len(events) >= 6:
        old_event = ClubEvents.query.filter_by(club_id=club.id).first()
        db.session.delete(old_event)
        db.session.commit()
    if club.codename == current_user.club_name:
        current_user.club_id = club_id
        db.session.commit()
    users = User.query.all()
    members = []
    for user in users:
        if user.club_id == club.id:
            members.append(user)
    top_members = sorted(members, key=lambda user: user.xp_count, reverse=True)
    top6_members = top_members[:6]
    imem = len(members)
    return render_template('clubs/detail.html', club=club, users=users, members=members, top6_members=top6_members, anns=anns, imem=imem, events=events, ian=ian)

@clubs_bp.route('/announce/<int:club_id>', methods=['POST'])
@login_required
def announce(club_id):
    club = Club.query.get_or_404(club_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        announcer = current_user.username
        club_id = club.id
        date = datetime.now().date()
        new_announce = ClubAnnouncements(title=title, content=content, announcer=announcer, club_id=club_id, date=date)
        db.session.add(new_announce)
        db.session.commit()
    return redirect(url_for('clubs.view_club', club_id=club.id))

@clubs_bp.route('/events/<int:club_id>', methods=['POST'])
@login_required
def events(club_id):
    club = Club.query.get_or_404(club_id)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        club_id = club.id
        date = request.form['date']
        new_event = ClubEvents(title=title, description=description, club_id=club_id, date=date)
        db.session.add(new_event)
        db.session.commit()
    return redirect(url_for('clubs.view_club', club_id=club.id))

@clubs_bp.route('/join/<int:club_id>', methods=['POST'])
@login_required
def join_club(club_id):
    club = Club.query.get_or_404(club_id)
    if current_user.club_id:
        flash("You must leave your current club before joining a new one.", "warning")
        return redirect(url_for('clubs.view_club', club_id=current_user.club_id))

    current_user.club_id = club.id
    db.session.commit()
    flash(f"Successfully joined the club: {club.name}", "success")
    return redirect(url_for('clubs.view_club', club_id=club.id))

@clubs_bp.route('/leave', methods=['POST'])
@login_required
def leave_club():
    if current_user.club_id is None:
        flash("You are not currently in any club.", "warning")
        return redirect(url_for('clubs.list_clubs'))  # Adjust this URL to your profile or home page

    current_user.club_id = None
    current_user.club_name = None
    db.session.commit()
    flash("Successfully left the club.", "success")
    return redirect(url_for('clubs.list_clubs'))  # Adjust this URL to your profile or home page

app.register_blueprint(clubs_bp)

def determine_league(xp_count):
    # Define your league logic based on xp_count
    if xp_count < 100:
        return 'Tantalum'
    elif xp_count < 500:
        return 'Copper'
    elif xp_count < 1000:
        return 'Bronze'
    elif xp_count < 2000:
        return 'Silver'
    elif xp_count < 3000:
        return 'Gold'
    elif xp_count < 4000:
        return 'Platinum'
    elif xp_count < 5000:
        return 'Diamond'
    elif xp_count < 6000:
        return 'Master'
    else:
        return 'Grandmaster'

@app.route('/leaderboard/<league_name>')
def league_leaderboard(league_name):
    users = User.query.filter_by(league=league_name).order_by(User.xp_count.desc()).all()
    return render_template('leaderboard.html', users=users, league_name=league_name)

@app.route('/youtube-test')
def quiz():
    if current_user.yt_badge:
        return render_template('already_passed.html')  # Redirect to a page indicating they can't retake the quiz

    questions = Question.query.all()
    selected_questions = random.sample([q.id for q in questions], 1)
    session['quiz_questions'] = selected_questions
    session['current_question_index'] = 0
    return render_template('ytt.html')

@app.route('/next_question', methods=['GET'])
@login_required
def next_question():
    if 'quiz_questions' not in session or 'current_question_index' not in session:
        return jsonify({'error': 'Quiz session not found'}), 400

    index = session['current_question_index']
    if index >= len(session['quiz_questions']):
        return jsonify({'error': 'No more questions'}), 400

    question_id = session['quiz_questions'][index]
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    session['current_question_index'] += 1
    return jsonify({
        'id': question.id,
        'question': question.question,
        'options': question.options
    })

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    try:
        data = request.json
        answers = data.get('questions', [])
        intentional = data.get('intentional', True)
        
        # Ensure you have the logic to handle answers
        correct_answers_count = 0
        total_questions = len(answers)
        passing_score = 0.8 * total_questions
        
        for answer in answers:
            question = Question.query.get(answer['id'])
            if question and answer['selected'] == question.answer:
                correct_answers_count += 1

        passed = correct_answers_count >= passing_score

        # Handle quiz result based on intentional flag
        if not intentional:
            passed = False  # Force fail if not intentional

        # Optionally, update user XP here
        if passed:
            current_user.xp_count += 100
            current_user.yt_badge = True
            db.session.commit()

        return jsonify({'passed': passed})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while processing the quiz.'}), 500

@app.route('/study/time')
@login_required
def timev():
    return render_template('/study/thome.html')

@app.route('/study/timer1800')
@login_required
def timer1800():
    return render_template('/study/t1.html')

@app.route('/study/timer2700')
@login_required
def timer2700():
    return render_template('/study/t2.html')

@app.route('/study/timer3600')
@login_required
def timer3600():
    return render_template('/study/t3.html')

@app.route('/study/timer7200')
@login_required
def timer7200():
    return render_template('/study/t4.html')

@app.route('/study/timer10800')
@login_required
def timer10800():
    return render_template('/study/t5.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)        # Run the app on all available interfaces and the specified port

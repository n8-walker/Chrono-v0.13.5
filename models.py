from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    account_type = db.Column(db.Text, default='Free')
    # User Activity
    xp_count = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    display_name = db.Column(db.String(150), default='Chrono-user')
    bio = db.Column(db.Text)
    career = db.Column(db.Text)
    level = db.Column(db.Integer, default=0)
    profile_image = db.Column(db.String(150), nullable=True, default='Default.png')
    club_id = db.Column(db.Integer, db.ForeignKey('club.id', ondelete='CASCADE'))
    league = db.Column(db.String(80), nullable=False, default='Tantalum')
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
                        
class UserSocialMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    youtube = db.Column(db.Text, nullable=False, default="Not_Set")
    facebook = db.Column(db.Text, nullable=False, default="Not_Set")
    twitter = db.Column(db.Text, nullable=False, default="Not_Set")
    insta = db.Column(db.Text, nullable=False, default="Not_Set")
    tiktok = db.Column(db.Text, nullable=False, default="Not_Set")
    # Importing Users
    creator = db.relationship('User', foreign_keys=[user])

class Tasks(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}  # Add this line to avoid the table redefinition error
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))  # Ensure this matches your actual column name and type
    date = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.Integer)
    type = db.Column(db.String(50))
    done = db.Column(db.Boolean, default=False)
    # Importing Users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each club
    name = db.Column(db.String(100), nullable=False)  # Club name
    description = db.Column(db.Text)  # Club description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the club was created
    codename = db.Column(db.String(50), unique=True, nullable=False)
    superadmin = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    admin = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    moderator = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    creator = db.relationship('User', foreign_keys=[superadmin])
    admn = db.relationship('User', foreign_keys=[admin])
    mod = db.relationship('User', foreign_keys=[moderator])

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

class Badges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    usr = db.relationship('User', foreign_keys=[user])
    badge_count = db.Column(db.Integer, default=0)
    youtube = db.Column(db.Boolean, default=False)

class Lovers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lover = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    got_loved = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

class AdditionalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    DNL = db.Column(db.Integer, default=11)
    last_task_date = db.Column(db.DateTime, default=datetime.utcnow)
    prev_task_date = db.Column(db.DateTime)
    # Importing Users
    creator = db.relationship('User', foreign_keys=[user])

class UserActiviy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    streak = db.Column(db.Integer, default=0)
    # Importing Users
    creator = db.relationship('User', foreign_keys=[user])

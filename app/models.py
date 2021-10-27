from app import login
from datetime import datetime
from hashlib import md5
from app import db
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for, current_app
import os
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from app.search import add_to_index, remove_from_index, query_index

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class Vote(db.Model):
    __tablename__ = 'vote'
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    vote = db.Column(db.SmallInteger)
    status = db.Column(db.SmallInteger)
    voter = db.relationship("User", back_populates="votedposts")
    voted = db.relationship("Post", back_populates="voters")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    hasavatar = db.Column(db.SmallInteger)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    votedposts = db.relationship("Vote", back_populates="voter", lazy='dynamic', cascade="all, delete-orphan")
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def avatar(self, size):
        if self.hasavatar is None or self.hasavatar == 0:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
        else:
            return url_for('static', filename=f'images/avatars/{self.id}.png')
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f"<User {self.username}>"
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=8640):
        return jwt.encode({'reset password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'], algorithm='HS256')

    def vote(self, post_id, value, status):
        prev_v=0
        prev_s=0
        try:
            obj = self.votedposts.filter(Vote.post_id == post_id).one()
            prev_v = obj.vote
            prev_s = obj.status
            self.votedposts.remove(obj)
        except MultipleResultsFound as e:
            print("Database Error, multiple values found for post vote")
            obj = self.votedposts.filter(Vote.post_id == post_id).first()
            prev_v = obj.vote
            prev_s = obj.status
            self.votedposts.remove(obj)
        except NoResultFound as e:
            pass
        ballot=Vote(voter_id=self.id, post_id=post_id, vote=value, status=status)
        post=Post.query.get(post_id)
        post.incrating(value-prev_v)
        post.incfavs(status-prev_s)
        db.session.add(ballot)
        db.session.commit()
        
    def getvote(self, post_id):
        try:
            obj = self.votedposts.filter(Vote.post_id == post_id).one()
            vote=obj.vote
            status = obj.status or 0
            return [vote, status]
        except MultipleResultsFound as e:
            print("Database Error, multiple values found for post vote")
            obj = self.votedposts.filter(Vote.post_id == post_id).first()
            vote=obj.vote
            status = obj.status or 0
            return [vote,status]
        except NoResultFound as e:
            return [0,0]


    def has_voted(self, post_id):
        return self.votedposts.filter(
            Vote.post_id == post_id).count() > 0


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithm=['HS256'])['reset password']
        except:
            return
        return User.query.get(id)
        
class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    voters = db.relationship("Vote", back_populates="voted", lazy='dynamic', cascade="all, delete-orphan")
    rating = db.Column(db.Integer, default=0)
    favs = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)

    def incrating(self, val):
        self.rating+=val

    def incfavs(self, val):
        self.favs+=val

    def incviews(self, val):
        self.views+=val
        

    def __repr__(self):
        return f"<Post {self.body}>"




@login.user_loader
def load_user(id):
    return User.query.get(int(id))
from .database import db

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String,unique=True, nullable = False)
    name = db.Column(db.String, nullable = False)

class Trackers(db.Model):
    __tablename__ = 'trackers'
    tracker_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    name = db.Column(db.String,nullable = False)
    description = db.Column(db.String)
    tracker_type= db.Column(db.String, nullable=False)
    settings = db.Column(db.String)
    created_by = db.Column(db.Integer,nullable = False)
    last_tracked = db.Column(db.DateTime)
    last_log = db.Column(db.String)

class Logs(db.Model):
    __tablename__ = 'logs'
    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    luser_id = db.Column(db.Integer,db.ForeignKey('users.user_id'),nullable=False )
    ltracker_id = db.Column(db.Integer,db.ForeignKey('trackers.tracker_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable = False)
    value = db.Column(db.String, nullable = False)
    note =  db.Column(db.String, nullable = False)


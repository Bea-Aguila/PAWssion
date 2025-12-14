from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime

db = SQLAlchemy()

# ----------------- Users (Admin + Regular User) -----------------
class User(db.Model):
     
    __table_args__ = (
       CheckConstraint(
            "(role = 'admin') OR (role != 'admin' AND age >= 18)",
            name='check_age_for_users'
        ),
    )
     
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False, default='Not set')
    last_name = db.Column(db.String(100), nullable=False, default='Not set')
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(20), nullable=False, default='Not set')
    address = db.Column(db.String(200), nullable=False, default='Not set')
    age = db.Column(db.Integer, nullable=True, default=None)
    gender = db.Column(db.String(10), nullable=False, default='Not set')
    role = db.Column(db.String(20),  nullable=False, default='user')
    password = db.Column(db.String(200), nullable=False)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    adoption_requests = db.relationship('AdoptionRequest', backref='user', lazy=True)


# ----------------- Shelters -----------------
class Shelter(db.Model):
    id = db.Column(db.Integer, primary_key=True,  nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    website = db.Column(db.String(150), unique=True, nullable=True)
    date_established = db.Column(db.String(50), nullable=False)
    shelter_type = db.Column(db.String(50), nullable=False)
    approved = db.Column(db.Boolean, nullable=True, default=None)
    role = db.Column(db.String(20),  nullable=False, default="shelter")
    password = db.Column(db.String(200), nullable=False)
    animals = db.relationship('Animal', backref='shelter', lazy=True)
    notifications = db.relationship('Notification', backref='shelter', lazy=True)


# ----------------- Animals -----------------
class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True,  nullable=False, unique=True)
    name = db.Column(db.String(50))
    age = db.Column(db.String(20))
    breed = db.Column(db.String(50), nullable=False)  
    gender = db.Column(db.String(10), nullable=False) 
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image1 = db.Column(db.String(200), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=False)
    adoption_requests = db.relationship('AdoptionRequest', backref='animal', lazy=True)   
    
# ----------------- Adoption Requests -----------------
class AdoptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True,  nullable=False, unique=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)


# ----------------- Notifications -----------------
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True,  nullable=False, unique=True)
    message = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    read = db.Column(db.Boolean, default=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=True)
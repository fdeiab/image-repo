"""
author: Fattima Deiab

This file defines and creates the tables required.

User Table - stores the data given when a user 
             creates an account (username, email,
             the hash value of their password, and a
             relationship to the images posted by them)

Images Table - stores the data about an image 
               posted to the repository (image 
               name, the username that posted it, 
               date posted, and the view setting
               of that photo 
               (False = Public Viewing, True = Private))
"""

from imagerepo import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(25), unique = True, nullable = False)
	userEmail = db.Column(db.String(100), unique = True, nullable = False)
	userPass = db.Column(db.String(64), nullable = False)
	imagesPosted = db.relationship('Images', backref='owner', lazy=True)

	def __repr__(self):
		return f"User: {self.username}, {self.userEmail}\n"


class Images(db.Model):
	imageID = db.Column(db.Integer, primary_key = True)
	userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
	imageName = db.Column(db.String(50), nullable = False)
	datePosted = db.Column(db.DateTime, nullable = False, default = datetime.now)
	privStatus = db.Column(db.Boolean, nullable = False, default = False)

	def __repr__(self):
		return f"Image: owner:{self.userID} imageID:{self.imageID} {self.imageName}, Status:{self.privStatus}\n"
	
# create the tables
db.create_all()

"""
author: Fattima Deiab

Initialization file for the package imagerepo
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import json 
app = Flask(__name__)

app.config["SECRET_KEY"] = '0103d54bae7f51f619f9b64f9c18510a851616d720cc88d6299b0528addd03d2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['UPLOAD_PATH'] = 'imagerepo/static/userimgs'
db = SQLAlchemy(app) # database used to hold user's and their posted images 
bcrypt = Bcrypt(app) # module used for hashing 
login_manager = LoginManager(app) # manages users login sessions 
login_manager.login_view = "login"
login_manager.login_message_category = 'info'
from imagerepo import routes

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "CaoMy"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ncvnhv@localhost/shopcm2?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app=app)

admin = Admin(app=app, name="QUAN LY BAN HANG", template_mode="bootstrap3")

login = LoginManager(app=app)
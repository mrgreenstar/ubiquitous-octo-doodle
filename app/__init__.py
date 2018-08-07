from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
from app.rsaC import rsaDM
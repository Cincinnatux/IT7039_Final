from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from jinja2 import ChoiceLoader, FileSystemLoader
import os
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS  # Optional, if needed for cross-origin requests

app = Flask(
    __name__,
    template_folder='assignment/templates',
    static_folder='assignment/static'
)

# Load environment variables (if using python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

# Configure secret key for flashing messages
app.config['SECRET_KEY'] = 'your_secure_secret_key_here'  # Replace with a secure key in production

# Configure the absolute path for the SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure Jinja2 template loader
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(app.root_path, 'assignment', 'templates')),  # ./assignment/templates
    FileSystemLoader(os.path.join(app.root_path, 'templates'))  # ./templates
])

# Optional: Enable CORS if your frontend is served from a different origin
# CORS(app)

# Set up logging
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Model Definitions
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

class ParentCompany(db.Model):
    __tablename__ = 'parent_companies'
    parent_company_id = db.Column(db.Integer, primary_key=True)
    parent_company_name = db.Column(db.String(100), unique=True, nullable=False)
    website = db.Column(db.String(100))
    address_1 = db.Column(db.String(100))
    address_2 = db.Column(db.String(100))
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    postal_code = db.Column(db.String(15))
    country = db.Column(db.String(30))

    distilleries = db.relationship('Distillery', backref='parent_company', lazy=True)

    def __repr__(self):
        return f"<ParentCompany {self.parent_company_name}>"

class Distillery(db.Model):
    __tablename__ = 'distilleries'
    dsp = db.Column(db.String(15), primary_key=True)
    distillery_name = db.Column(db.String(100), unique=True, nullable=False)
    parent_company_id = db.Column(db.Integer, db.ForeignKey('parent_companies.parent_company_id'), nullable=False)
    website = db.Column(db.String(100))
    address_1 = db.Column(db.String(100))
    address_2 = db.Column(db.String(100))
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    postal_code = db.Column(db.String(15))
    country = db.Column(db.String(30))

    brands = db.relationship('Brand', backref='distillery', lazy=True)

    def __repr__(self):
        return f"<Distillery {self.distillery_name}>"

class Brand(db.Model):
    __tablename__ = 'brands'
    brand_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(30))
    distillery_id = db.Column(db.String(15), db.ForeignKey('distilleries.dsp'), nullable=False)

    bottles = db.relationship('Bottle', backref='brand', lazy=True)

    def __repr__(self):
        return f"<Brand {self.brand_name}>"

class Bottle(db.Model):
    __tablename__ = 'bottles'
    bottle_id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.brand_id'), nullable=False)  # Corrected ForeignKey
    expression = db.Column(db.String(100))
    volume_ml = db.Column(db.Integer)
    proof = db.Column(db.Float)
    stated_age = db.Column(db.Float)
    estimated_age = db.Column(db.Float)
    primary_grain = db.Column(db.String(15))
    primary_grain_percentage = db.Column(db.Float)
    secondary_grain = db.Column(db.String(15))
    secondary_grain_percentage = db.Column(db.Float)
    tertiary_grain = db.Column(db.String(15))
    tertiary_grain_percentage = db.Column(db.Float)
    quaternary_grain = db.Column(db.String(15))
    quaternary_grain_percentage = db.Column(db.Float)
    source = db.Column(db.String(100))
    price_paid = db.Column(db.Float)
    srp = db.Column(db.Float)
    date_purchased = db.Column(db.Date)
    date_distilled = db.Column(db.Date)
    date_bottled = db.Column(db.Date)
    date_opened = db.Column(db.Date)
    date_emptied = db.Column(db.Date)
    single_barrel = db.Column(db.Boolean)
    chill_filtered = db.Column(db.Boolean)
    bottled_in_bond = db.Column(db.Boolean)
    peated = db.Column(db.Boolean)
    finished = db.Column(db.Boolean)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f"<Bottle {self.expression}>"
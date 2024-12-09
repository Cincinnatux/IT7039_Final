from datetime import datetime
# from enum import Enum
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_cors import CORS  # Optional, if needed for cross-origin requests
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from jinja2 import ChoiceLoader, FileSystemLoader
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import Enum as SqlEnum
from wtforms import StringField, IntegerField, FloatField, DateField
from wtforms.validators import DataRequired, Optional
import os
import random

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
    
    def to_dict(self):
        return {
            'parent_company_id': self.parent_company_id,
            'parent_company_name': self.parent_company_name,
            'website': self.website,
            'address_1': self.address_1,
            'address_2': self.address_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country
        }

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
    
    def to_dict(self):
        return {
            'dsp' : self.dsp,
            'distillery_name' : self.distillery_name,
            'parent_company_id' : self.parent_company_id,
            'website' : self.website,
            'address_1' : self.address_1,
            'address_2' : self.address_2,
            'city' : self.city,
            'state' : self.state,
            'postal_code' : self.postal_code,
            'country' : self.country
        }

class Brand(db.Model):
    __tablename__ = 'brands'
    brand_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    distillery_id = db.Column(db.String(15), db.ForeignKey('distilleries.dsp'), nullable=False)

    bottles = db.relationship('Bottle', backref='brand', lazy=True)

    def __repr__(self):
        return f"<Brand {self.brand_name}>"
    
    def to_dict(self):
        return {
            'brand_id' : self.brand_id,
            'brand_name' : self.brand_name,
            'category' : self.category,
            'distillery_id' : self.distillery_id
        }

# class BrandCategory(Enum):
#    BOURBON = "Bourbon"
#    RYE = "Rye"
#    AMERICAN_SINGLE_MALT = "American Single Malt"
#    SCOTCH_SINGLE_MALT = "Scotch Single Malt"
#    JAPANESE_SINGLE_MALT = "Japanese Single Malt"
#    INDIAN_SINGLE_MALT = "Indian Single Malt"
#    AMERICAN_WHISKEY = "American Whiskey"
#    FINISHED_BOURBON = "Finished Bourbon"
#    FINISHED_RYE = "Finished Rye"
#    LIGHT_WHISKEY = "Light Whiskey"
#    CORN_WHISKEY = "Corn Whiskey"
#    FLAVORED_WHISKEY = "Flavored Whiskey"
#    SCOTCH_BLEND = "Scotch Blend"
#    IRISH_WHISKEY = "Irish Whiskey"
#    JAPANESE_BLEND = "Japanese Blend"
#    INDIAN_BLEND = "Indian Blend"

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
    
    def to_dict(self):
        return {
            'bottle_id' : self.bottle_id,
            'brand_id' : self.brand_id,
            'expression' : self.expression,
            'brand_name' : self.brand.brand_name,
            'category' : self.brand.category,
            'volume_ml' : self.volume_ml,
            'proof' : self.proof,
            'stated_age' : self.stated_age,
            'estimated_age' : self.estimated_age,
            'primary_grain' : self.primary_grain,
            'primary_grain_percentage' : self.primary_grain_percentage,
            'secondary_grain' : self.secondary_grain,
            'secondary_grain_percentage' : self.secondary_grain_percentage,
            'tertiary_grain' : self.tertiary_grain,
            'tertiary_grain_percentage' : self.tertiary_grain_percentage,
            'quaternary_grain' : self.quaternary_grain,
            'quaternary_grain_percentage' : self.quaternary_grain_percentage,
            'source' : self.source,
            'price_paid' : self.price_paid,
            'srp' : self.srp,
            'date_purchased': self.date_purchased.isoformat() if self.date_purchased else None,
            'date_distilled': self.date_distilled.isoformat() if self.date_distilled else None,
            'date_bottled': self.date_bottled.isoformat() if self.date_bottled else None,
            'date_opened': self.date_opened.isoformat() if self.date_opened else None,
            'date_emptied': self.date_emptied.isoformat() if self.date_emptied else None,
            'single_barrel': self.single_barrel,
            'chill_filtered' : self.chill_filtered,
            'bottled_in_bond' : self.bottled_in_bond,
            'peated' : self.peated,
            'finished' : self.finished,
            'notes' : self.notes
        }
    
# Routes Definitions

@app.route('/assignment', methods=['POST', 'GET'])  # Existing Todo route
def index():
    if request.method == 'POST':
        task_content = request.form['content']  # References our form's 'content' input
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment')
        except Exception as e:
            db.session.rollback()
            flash('There was an issue adding your task.', 'error')
            app.logger.error(f"Error adding task: {e}", exc_info=True)
            return redirect('/assignment')
        
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/assignment/delete/<int:id>', methods=['POST'])
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
        if request.is_json:
            return jsonify({'success': True}), 200
        else:
            return redirect('/assignment')
    except Exception as e:
        db.session.rollback()
        flash('There was a problem deleting that task.', 'error')
        app.logger.error(f"Error deleting task: {e}", exc_info=True)
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error deleting task.'}), 400
        else:
            return redirect('/assignment')
    
@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
       task.content = request.form['content'] 
       try:
           db.session.commit()
           flash('Task updated successfully!', 'success')
           return redirect('/assignment')
       except Exception as e:
           db.session.rollback()
           flash('There was an issue updating your task.', 'error')
           app.logger.error(f"Error updating task: {e}", exc_info=True)
           return redirect('/assignment')
    else:
        return render_template('update.html', task=task)

@app.route('/final')
def final():
    return redirect(url_for('new_entry'))

@app.route('/new_entry', methods=['GET'])
def new_entry():
    # Fetch data for dropdowns
    parent_companies = ParentCompany.query.all()
    distilleries = Distillery.query.all()
    brands = Brand.query.all()
    return render_template('new_entry.html', parent_companies=parent_companies, distilleries=distilleries, brands=brands)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search_records', methods=['POST'])
def search_records():
    data = request.form
    table = data.get('table')

    if not table:
        app.logger.warning("No table specified in search_records.")
        return jsonify({'success': False, 'error': 'No table specified.'}), 400

    try:
        if table == 'parent_company':
            name = data.get('parent_company_name', '').strip()
            city = data.get('city', '').strip()
            country = data.get('country', '').strip()

            query = ParentCompany.query
            if name:
                query = query.filter(ParentCompany.parent_company_name.ilike(f'%{name}%'))
            if city:
                query = query.filter(ParentCompany.city.ilike(f'%{city}%'))
            if country:
                query = query.filter(ParentCompany.country.ilike(f'%{country}%'))

            results = query.all()
            results = [record.to_dict() for record in results]

        elif table == 'distillery':
            distillery_name = data.get('distillery_name', '').strip()
            parent_company_id = data.get('parent_company_id', '').strip()
            country = data.get('country', '').strip()

            query = Distillery.query
            if distillery_name:
                query = query.filter(Distillery.distillery_name.ilike(f'%{distillery_name}%'))
            if parent_company_id:
                query = query.filter(Distillery.parent_company_id == parent_company_id)
            if country:
                query = query.filter(Distillery.country.ilike(f'%{country}%'))

            results = query.all()
            results = [record.to_dict() for record in results]

        elif table == 'brand':
            brand_name = data.get('brand_name', '').strip()
            category = data.get('category', '').strip()
            distillery_id = data.get('distillery_id', '').strip()

            query = Brand.query
            if brand_name:
                query = query.filter(Brand.brand_name.ilike(f'%{brand_name}%'))
            if category:
                query = query.filter(Brand.category.ilike(f'%{category}%'))
            if distillery_id:
                query = query.filter(Brand.distillery_id == distillery_id)

            results = query.all()
            results = [record.to_dict() for record in results]

        elif table == 'bottle':
            expression = data.get('expression', '').strip()
            brand_id = data.get('brand_id', '').strip()
            country = data.get('country', '').strip()

            query = Bottle.query
            if expression:
                query = query.filter(Bottle.expression.ilike(f'%{expression}%'))
            if brand_id:
                query = query.filter(Bottle.brand_id == brand_id)
            if country:
                query = query.filter(Bottle.country.ilike(f'%{country}%'))

            results = query.all()
            results = [record.to_dict() for record in results]

        else:
            app.logger.warning(f"Invalid table specified in search_records: {table}")
            return jsonify({'success': False, 'error': 'Invalid table specified.'}), 400

        return jsonify({'success': True, 'results': results}), 200

    except Exception as e:
        app.logger.error(f"Error in search_records: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An error occurred during the search.'}), 500

# New Routes for Adding Entities

@app.route('/add_parent_company', methods=['POST'])
def add_parent_company():
    parent_company_name = request.form.get('parent_company_name').strip()
    website = request.form.get('website').strip()
    address_1 = request.form.get('address_1').strip()
    address_2 = request.form.get('address_2').strip()
    city = request.form.get('city').strip()
    state = request.form.get('state').strip()
    postal_code = request.form.get('postal_code').strip()
    country = request.form.get('country').strip()

    if not parent_company_name:
        flash('Parent Company Name is required.', 'error')
        app.logger.warning("Parent Company Name is missing.")
        return jsonify({'success': False, 'error': 'Parent Company Name is required.'}), 400

    # Check if the ParentCompany already exists
    existing_company = ParentCompany.query.filter_by(parent_company_name=parent_company_name).first()
    if existing_company:
        flash('Parent Company already exists.', 'error')
        app.logger.warning(f"Attempted to add duplicate Parent Company: {parent_company_name}")
        return jsonify({'success': False, 'error': 'Parent Company already exists.'}), 400

    new_company = ParentCompany(
        parent_company_name=parent_company_name,
        website=website,
        address_1=address_1,
        address_2=address_2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country
    )

    try:
        db.session.add(new_company)
        db.session.commit()
        app.logger.info(f"Parent Company added successfully: {parent_company_name}")
        return jsonify({
            'success': True,
            'parent_company_id': new_company.parent_company_id,
            'parent_company_name': new_company.parent_company_name
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding Parent Company: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error adding Parent Company: ' + str(e)
        }), 500

    # return redirect(url_for('new_entry'))

@app.route('/add_distillery', methods=['POST'])
def add_distillery():
    dsp = request.form.get('dsp').strip()
    distillery_name = request.form.get('distillery_name').strip()
    parent_company_id = request.form.get('parent_company_id').strip()
    website = request.form.get('website').strip()
    address_1 = request.form.get('address_1').strip()
    address_2 = request.form.get('address_2').strip()
    city = request.form.get('city').strip()
    state = request.form.get('state').strip()
    postal_code = request.form.get('postal_code').strip()
    country = request.form.get('country').strip()

    if not dsp or not distillery_name or not parent_company_id:
        flash('DSP, Distillery Name, and Parent Company are required.', 'error')
        app.logger.warning("DSP, Distillery Name, or Parent Company ID is missing.")
        return jsonify({'success': False, 'error': 'Distillery Name is required.'}), 400

    # Check if the Distillery already exists
    existing_distillery = Distillery.query.filter_by(dsp=dsp).first()
    if existing_distillery:
        flash('Distillery with this DSP already exists.', 'error')
        app.logger.warning(f"Attempted to add duplicate Distillery with DSP: {dsp}")
        return jsonify({'success': False, 'error': 'That Distillery already exists.'}), 400

    new_distillery = Distillery(
        dsp=dsp,
        distillery_name=distillery_name,
        parent_company_id=parent_company_id,
        website=website,
        address_1=address_1,
        address_2=address_2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country
    )

    try:
        db.session.add(new_distillery)
        db.session.commit()
        app.logger.info(f"Distillery added successfully: {distillery_name}")
        return jsonify({
            'success': True,
            'dsp': new_distillery.dsp,
            'distillery_name': new_distillery.distillery_name
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding Distillery: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error adding Distillery: ' + str(e)
        }), 500
    
    # return redirect(url_for('new_entry'))

@app.route('/add_brand', methods=['POST'])
def add_brand():
    brand_name = request.form.get('brand_name').strip()
    category = request.form.get('category').strip()
    distillery_id = request.form.get('distillery_id').strip()

    if not brand_name or not distillery_id:
        flash('Brand Name and Distillery are required.', 'error')
        app.logger.warning("Brand Name or Distillery ID is missing.")
        return jsonify({'success': False, 'error': 'Brand is required.'}), 400

    # Check if the Brand already exists
    existing_brand = Brand.query.filter_by(brand_name=brand_name, distillery_id=distillery_id).first()
    if existing_brand:
        flash('Brand with this name already exists for the selected Distillery.', 'error')
        app.logger.warning(f"Attempted to add duplicate Brand: {brand_name} for Distillery ID: {distillery_id}")
        return jsonify({'success': False, 'error': 'That Brand already exists.'}), 400

    new_brand = Brand(
        brand_name=brand_name,
        category=category,
        distillery_id=distillery_id
    )

    try:
        db.session.add(new_brand)
        db.session.commit()
        app.logger.info(f"Brand added successfully: {brand_name}")
        return jsonify({
            'success': True,
            'brand_id': new_brand.brand_id,
            'brand_name': new_brand.brand_name
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding Brand: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error adding Brand: ' + str(e)
        }), 500
    
    # return redirect(url_for('new_entry'))

@app.route('/add_bottle', methods=['POST'])
def add_bottle():
    try:
        brand_id = request.form.get('brand_id')
        expression = request.form.get('expression').strip()
        volume_ml = request.form.get('volume_ml')
        proof = request.form.get('proof')
        stated_age = request.form.get('stated_age')
        estimated_age = request.form.get('estimated_age')
        primary_grain = request.form.get('primary_grain').strip()
        primary_grain_percentage = request.form.get('primary_grain_percentage')
        secondary_grain = request.form.get('secondary_grain').strip()
        secondary_grain_percentage = request.form.get('secondary_grain_percentage')
        tertiary_grain = request.form.get('tertiary_grain').strip()
        tertiary_grain_percentage = request.form.get('tertiary_grain_percentage')
        quaternary_grain = request.form.get('quaternary_grain').strip()
        quaternary_grain_percentage = request.form.get('quaternary_grain_percentage')
        source = request.form.get('source').strip()
        price_paid = request.form.get('price_paid')
        srp = request.form.get('srp')
        date_purchased = request.form.get('date_purchased')
        date_distilled = request.form.get('date_distilled')
        date_bottled = request.form.get('date_bottled')
        date_opened = request.form.get('date_opened')
        date_emptied = request.form.get('date_emptied')
        single_barrel = request.form.get('single_barrel') == 'on'
        chill_filtered = request.form.get('chill_filtered') == 'on'
        bottled_in_bond = request.form.get('bottled_in_bond') == 'on'
        peated = request.form.get('peated') == 'on'
        finished = request.form.get('finished') == 'on'
        notes = request.form.get('notes').strip()
        
        # Helper function to parse dates
        def parse_date(date_str):
            if date_str:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return None
            return None
        
        # Convert date strings to date objects
        date_purchased = parse_date(date_purchased)
        date_distilled = parse_date(date_distilled)
        date_bottled = parse_date(date_bottled)
        date_opened = parse_date(date_opened)
        date_emptied = parse_date(date_emptied)
        
        # Create a new Bottle instance
        new_bottle = Bottle(
            brand_id=brand_id,
            expression=expression,
            volume_ml=int(volume_ml) if volume_ml else None,
            proof=float(proof) if proof else None,
            stated_age=float(stated_age) if stated_age else None,
            estimated_age=float(estimated_age) if estimated_age else None,
            primary_grain=primary_grain,
            primary_grain_percentage=float(primary_grain_percentage) if primary_grain_percentage else None,
            secondary_grain=secondary_grain,
            secondary_grain_percentage=float(secondary_grain_percentage) if secondary_grain_percentage else None,
            tertiary_grain=tertiary_grain,
            tertiary_grain_percentage=float(tertiary_grain_percentage) if tertiary_grain_percentage else None,
            quaternary_grain=quaternary_grain,
            quaternary_grain_percentage=float(quaternary_grain_percentage) if quaternary_grain_percentage else None,
            source=source,
            price_paid=float(price_paid) if price_paid else None,
            srp=float(srp) if srp else None,
            date_purchased=date_purchased,
            date_distilled=date_distilled,
            date_bottled=date_bottled,
            date_opened=date_opened,
            date_emptied=date_emptied,
            single_barrel=single_barrel,
            chill_filtered=chill_filtered,
            bottled_in_bond=bottled_in_bond,
            peated=peated,
            finished=finished,
            notes=notes
        )
        
        db.session.add(new_bottle)
        db.session.commit()
        
        flash('Bottle added successfully!', 'success')
        app.logger.info(f"Bottle added successfully: {expression}")
        return jsonify({'success': True, 'bottle_id': new_bottle.bottle_id, 'expression': new_bottle.expression}), 201
    except Exception as e:
        db.session.rollback()
        flash('Error adding Bottle: ' + str(e), 'error')
        app.logger.error(f"Error adding Bottle: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error adding Bottle.'}), 500
    
@app.route('/analyze_inventory', methods=['GET'])
def analyze_inventory():
    try:
        # Query all bottles
        all_bottles = Bottle.query.all()
        total_bottles = len(all_bottles)
        
        # Query bottles without date_emptied
        bottles_not_emptied = Bottle.query.filter(Bottle.date_emptied == None).all()
        total_not_emptied = len(bottles_not_emptied)
        
        # Example: Categorize bottles by brand for the first pie chart
        brand_counts = db.session.query(Brand.brand_name, db.func.count(Bottle.bottle_id))\
            .join(Bottle, Brand.brand_id == Bottle.brand_id)\
            .group_by(Brand.brand_name).all()
        
        # Example: Categorize bottles not emptied by brand for the second pie chart
        brand_not_emptied_counts = db.session.query(Brand.brand_name, db.func.count(Bottle.bottle_id))\
            .join(Bottle, Brand.brand_id == Bottle.brand_id)\
            .filter(Bottle.date_emptied == None)\
            .group_by(Brand.brand_name).all()
        
        # Prepare data for Chart.js
        chart1_labels = [brand for brand, count in brand_counts]
        chart1_values = [count for brand, count in brand_counts]
        
        chart2_labels = [brand for brand, count in brand_not_emptied_counts]
        chart2_values = [count for brand, count in brand_not_emptied_counts]
        
        return render_template('analyze_inventory.html',
                               total_bottles=total_bottles,
                               total_not_emptied=total_not_emptied,
                               chart1_labels=chart1_labels,
                               chart1_values=chart1_values,
                               chart2_labels=chart2_labels,
                               chart2_values=chart2_values)
    except Exception as e:
        app.logger.error(f"Error rendering analyze_inventory: {e}", exc_info=True)
        return render_template('500.html'), 500

# Route to render random_flight.html
@app.route('/api/random_flight', methods=['GET'])
def random_flight():
    try:
        # Query bottles where date_emptied is NULL
        available_bottles = Bottle.query.filter(Bottle.date_emptied == None).all()
        total_available = len(available_bottles)
        
        if total_available == 0:
            return jsonify({'success': False, 'message': 'No bottles available without a date_emptied.'}), 200
        
        # Randomly select 4 bottles
        selected_bottles = random.sample(available_bottles, min(4, total_available))
        bottles_data = [bottle.to_dict() for bottle in selected_bottles]
        
        return jsonify({'success': True, 'bottles': bottles_data}), 200
    except Exception as e:
        app.logger.error(f"Error fetching random flight: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An error occurred while fetching bottles.'}), 500

# Error Handlers

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"Internal Server Error: {error}", exc_info=True)
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f"Page Not Found: {request.url}")
    return render_template('404.html'), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
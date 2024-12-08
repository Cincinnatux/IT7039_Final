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
        return redirect('/assignment')
    except Exception as e:
        db.session.rollback()
        flash('There was a problem deleting that task.', 'error')
        app.logger.error(f"Error deleting task: {e}", exc_info=True)
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

@app.route('/analyze_inventory')
def analyze_inventory():
    return render_template('analyze_inventory.html')

@app.route('/random_flight')
def random_flight():
    return render_template('random_flight.html')

@app.route('/')
def home():
    return render_template('home.html')

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
        return redirect(url_for('new_entry'))

    # Check if the ParentCompany already exists
    existing_company = ParentCompany.query.filter_by(parent_company_name=parent_company_name).first()
    if existing_company:
        flash('Parent Company already exists.', 'error')
        app.logger.warning(f"Attempted to add duplicate Parent Company: {parent_company_name}")
        return redirect(url_for('new_entry'))

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
        flash('Parent Company added successfully!', 'success')
        app.logger.info(f"Parent Company added successfully: {parent_company_name}")
    except Exception as e:
        db.session.rollback()
        flash('Error adding Parent Company: ' + str(e), 'error')
        app.logger.error(f"Error adding Parent Company: {e}", exc_info=True)

    return redirect(url_for('new_entry'))

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
        return redirect(url_for('new_entry'))

    # Check if the Distillery already exists
    existing_distillery = Distillery.query.filter_by(dsp=dsp).first()
    if existing_distillery:
        flash('Distillery with this DSP already exists.', 'error')
        app.logger.warning(f"Attempted to add duplicate Distillery with DSP: {dsp}")
        return redirect(url_for('new_entry'))

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
        flash('Distillery added successfully!', 'success')
        app.logger.info(f"Distillery added successfully: {distillery_name}")
    except Exception as e:
        db.session.rollback()
        flash('Error adding Distillery: ' + str(e), 'error')
        app.logger.error(f"Error adding Distillery: {e}", exc_info=True)

    return redirect(url_for('new_entry'))

@app.route('/add_brand', methods=['POST'])
def add_brand():
    brand_name = request.form.get('brand_name').strip()
    category = request.form.get('category').strip()
    distillery_id = request.form.get('distillery_id').strip()

    if not brand_name or not distillery_id:
        flash('Brand Name and Distillery are required.', 'error')
        app.logger.warning("Brand Name or Distillery ID is missing.")
        return redirect(url_for('new_entry'))

    # Check if the Brand already exists
    existing_brand = Brand.query.filter_by(brand_name=brand_name, distillery_id=distillery_id).first()
    if existing_brand:
        flash('Brand with this name already exists for the selected Distillery.', 'error')
        app.logger.warning(f"Attempted to add duplicate Brand: {brand_name} for Distillery ID: {distillery_id}")
        return redirect(url_for('new_entry'))

    new_brand = Brand(
        brand_name=brand_name,
        category=category,
        distillery_id=distillery_id
    )

    try:
        db.session.add(new_brand)
        db.session.commit()
        flash('Brand added successfully!', 'success')
        app.logger.info(f"Brand added successfully: {brand_name}")
    except Exception as e:
        db.session.rollback()
        flash('Error adding Brand: ' + str(e), 'error')
        app.logger.error(f"Error adding Brand: {e}", exc_info=True)

    return redirect(url_for('new_entry'))

@app.route('/add_bottle', methods=['POST'])
def add_bottle():
    brand_id = request.form.get('brand_id').strip()
    expression = request.form.get('expression').strip()
    volume_ml = request.form.get('volume_ml').strip()
    proof = request.form.get('proof').strip()
    stated_age = request.form.get('stated_age').strip()
    estimated_age = request.form.get('estimated_age').strip()
    primary_grain = request.form.get('primary_grain').strip()
    primary_grain_percentage = request.form.get('primary_grain_percentage').strip()
    secondary_grain = request.form.get('secondary_grain').strip()
    secondary_grain_percentage = request.form.get('secondary_grain_percentage').strip()
    tertiary_grain = request.form.get('tertiary_grain').strip()
    tertiary_grain_percentage = request.form.get('tertiary_grain_percentage').strip()
    quaternary_grain = request.form.get('quaternary_grain').strip()
    quaternary_grain_percentage = request.form.get('quaternary_grain_percentage').strip()
    source = request.form.get('source').strip()
    price_paid = request.form.get('price_paid').strip()
    srp = request.form.get('srp').strip()
    date_purchased = request.form.get('date_purchased').strip()
    date_distilled = request.form.get('date_distilled').strip()
    date_bottled = request.form.get('date_bottled').strip()
    date_opened = request.form.get('date_opened').strip()
    date_emptied = request.form.get('date_emptied').strip()
    single_barrel = True if request.form.get('single_barrel') == 'on' else False
    chill_filtered = True if request.form.get('chill_filtered') == 'on' else False
    bottled_in_bond = True if request.form.get('bottled_in_bond') == 'on' else False
    peated = True if request.form.get('peated') == 'on' else False
    finished = True if request.form.get('finished') == 'on' else False
    notes = request.form.get('notes').strip()

    if not brand_id:
        flash('Brand is required.', 'error')
        app.logger.warning("Brand ID is missing.")
        return redirect(url_for('new_entry'))

    # Convert numerical fields to appropriate types
    try:
        volume_ml = int(volume_ml) if volume_ml else None
        proof = float(proof) if proof else None
        stated_age = float(stated_age) if stated_age else None
        estimated_age = float(estimated_age) if estimated_age else None
        primary_grain_percentage = float(primary_grain_percentage) if primary_grain_percentage else None
        secondary_grain_percentage = float(secondary_grain_percentage) if secondary_grain_percentage else None
        tertiary_grain_percentage = float(tertiary_grain_percentage) if tertiary_grain_percentage else None
        quaternary_grain_percentage = float(quaternary_grain_percentage) if quaternary_grain_percentage else None
        price_paid = float(price_paid) if price_paid else None
        srp = float(srp) if srp else None
    except ValueError as ve:
        flash('Invalid numerical input.', 'error')
        app.logger.warning(f"Invalid numerical input: {ve}")
        return redirect(url_for('new_entry'))

    new_bottle = Bottle(
        brand_id=brand_id,
        expression=expression,
        volume_ml=volume_ml,
        proof=proof,
        stated_age=stated_age,
        estimated_age=estimated_age,
        primary_grain=primary_grain,
        primary_grain_percentage=primary_grain_percentage,
        secondary_grain=secondary_grain,
        secondary_grain_percentage=secondary_grain_percentage,
        tertiary_grain=tertiary_grain,
        tertiary_grain_percentage=tertiary_grain_percentage,
        quaternary_grain=quaternary_grain,
        quaternary_grain_percentage=quaternary_grain_percentage,
        source=source,
        price_paid=price_paid,
        srp=srp,
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

    try:
        db.session.add(new_bottle)
        db.session.commit()
        flash('Bottle added successfully!', 'success')
        app.logger.info(f"Bottle added successfully: {expression}")
    except Exception as e:
        db.session.rollback()
        flash('Error adding Bottle: ' + str(e), 'error')
        app.logger.error(f"Error adding Bottle: {e}", exc_info=True)

    return redirect(url_for('new_entry'))

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
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, url_for, request, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from jinja2 import ChoiceLoader, FileSystemLoader
import os

app = Flask(
    __name__,
    template_folder='assignment/templates',
    static_folder='assignment/static'
)

# Bifurcate my project components
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(app.root_path, 'assignment', 'templates')), # ./assignment/templates
    FileSystemLoader(os.path.join(app.root_path, 'templates'))  # ./templates
])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)  # Initialize the database
migrate = Migrate(app, db)  # Initialize Flask-Migrate

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
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.brand_id'), nullable=False)
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

# Uncomment the following two lines to create the db tables:
# with app.app_context():
#    db.create_all()

@app.route('/assignment', methods=['POST', 'GET'])  # This allows us to send data to our database
def index():
    if request.method == 'POST':
        task_content = request.form['content']  # References our form's 'content' input
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment')
        except:
            return 'There was an issue adding your task'
        
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()  # .all could also be .first
        return render_template('index.html', tasks=tasks)

@app.route('/assignment/delete/<int:id>', methods=['POST'])
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment')
    except:
        return 'There was a problem deleting that task'
    
@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
       task.content = request.form['content'] 
       try:
           db.session.commit()
           return redirect('/assignment')
       except:
           return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)

@app.route('/final')
def final():
    return render_template('new_entry.html')

@app.route('/new_entry')  # New route for the new_entry page
def new_entry():
    return render_template('new_entry.html')

@app.route('/analyze_inventory')  # New route for analyze_inventory page
def analyze_inventory():
    return render_template('analyze_inventory.html')

@app.route('/random_flight')  # New route for random_flight page
def random_flight():
    return render_template('random_flight.html')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
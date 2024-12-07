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
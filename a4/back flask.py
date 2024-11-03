from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    works = db.relationship('Work', backref='owner', lazy=True)

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    works = Work.query.all()
    return render_template('portfolio.html', works=works)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_work = Work(title=title, description=description, user_id=1)  # Assuming user_id=1 for simplicity
        db.session.add(new_work)
        db.session.commit()
        return redirect(url_for('portfolio'))
    return render_template('add_work.html')

if __name__ == '__main__':
    with app.app_context():  # Create application context
        db.create_all()  # Create database tables
    app.run(debug=True)
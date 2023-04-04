from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/cleanblogs"
# create the extension
db = SQLAlchemy(app);
# db.init_app(app)

class Contacts(db.Model):
    # name, email, phone, message, date
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12))

@app.route('/')
def root():  # put application's code here
    return render_template('index.html')

@app.route('/home')
def home():  # put application's code here
    return render_template('index.html')

@app.route('/about')
def about():  # put application's code here
    name = "Ankush Chavan"
    return render_template('about.html', name=name)

@app.route('/contact', methods = ['POST', 'GET'])
def contact():  # put application's code here
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        entry = Contacts(name=name, email=email, phone=phone, message=message, date=datetime.now())
        db.session.add(entry);
        db.session.commit();
    # else:
    return render_template('contact.html')

@app.route('/post')
def post():  # put application's code here
    return render_template('post.html')
if __name__ == '__main__':
    app.run()

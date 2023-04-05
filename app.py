from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json


with open('config.json', 'r') as c:
    params = json.load(c)['params']

locale_server = True;
app = Flask(__name__)
# Configuring the email setup to contact forms
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_username'],
    MAIL_PASSWORD=params['gmail_password']
)
mail = Mail(app)

if(locale_server):
    # configure the MYSQL database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

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
class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    sub_title = db.Column(db.String(100), nullable=False)
    posted_by = db.Column(db.String(20), nullable=False)
    posted_at = db.Column(db.String(12), nullable=False)
    post_content = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(25), unique=False, nullable=False)

@app.route('/')
def root():  # put application's code here
    return render_template('index.html', params=params)

@app.route('/home')
def home():  # put application's code here
    return render_template('index.html', params=params)

@app.route('/about')
def about():  # put application's code here
    name = "Ankush Chavan"
    return render_template('about.html', name=name, params=params)

@app.route('/contact', methods = ['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        entry = Contacts(name=name, email=email, phone=phone, message=message, date=datetime.now())
        db.session.add(entry);
        db.session.commit();
        mail.send_message('Blog: New message from' + " " + name,
                          sender=email,
                          recipients=[params['gmail_username'], "ankush.neosoft@gmail.com"],
                          body=message + "\n" + phone
                          )
    return render_template('contact.html', params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post_details = Posts.query.filter_by(slug=post_slug).first();
    return render_template('post.html', params=params, post_details=post_details)

if __name__ == '__main__':
    app.run()

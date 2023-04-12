from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail
import json
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


with open('config.json', 'r') as c:
    params = json.load(c)['params']

locale_server = True
app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config['UPLOAD_FOLDER'] = params['upload_location']
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
def root():
    posts_list = Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html', params=params, posts=posts_list, is_auth=session['user'])
@app.route('/home')
def home():
    posts_list = Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html', params=params, posts=posts_list, is_auth=session['user'])

@app.route('/about')
def about():
    name = "Ankush Chavan"
    return render_template('about.html', name=name, params=params, is_auth=session['user'])

@app.route('/dashboard')
def dashboard():
    if 'user' in session and session['user'] == params['admin_username']:
        post_list = Posts.query.all()
        return render_template( 'dashboard.html', params=params, posts=post_list, is_auth=session['user'])
    return redirect('/login')


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
    return render_template('contact.html', params=params, is_auth=session['user'])

@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post_details = Posts.query.filter_by(slug=post_slug).first();
    return render_template('post.html', params=params, post_details=post_details, is_auth=session['user'])

@app.route('/login', methods=["GET","POST"])
def login():
    if 'user' in session and session['user'] == params['admin_username']:
        return redirect('/dashboard')
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == params['admin_username'] and password == params['admin_password']:
            session['user'] = username
            return redirect('/dashboard')
    return render_template('login.html', params=params, is_auth=session['user'])

@app.route('/post-add', methods=['GET', 'POST'])
def post_add():
    if 'user' in session and session['user'] == params['admin_username']:
        if request.method == 'POST':
            title = request.form['title']
            sub_title = request.form['sub_title']
            posted_by = request.form['posted_by']
            post_content = request.form['post_content']
            slug = request.form['slug']

            post_form = Posts(title=title, sub_title=sub_title, post_content=post_content, posted_by=posted_by, slug=slug, posted_at=datetime.now())
            db.session.add(post_form)
            db.session.commit()
        action_name = 'Add'
        return render_template('post-add-edit.html', params=params, action_name=action_name, action='/post-add',
                               post='None', is_auth=session['user'])

@app.route('/post-edit/<string:post_id>', methods=['GET', 'POST'])
def post_edit(post_id):
    if 'user' in session and session['user'] == params['admin_username']:
        if request.method == 'POST':
            title = request.form['title']
            sub_title = request.form['sub_title']
            posted_by = request.form['posted_by']
            post_content = request.form['post_content']
            slug = request.form['slug']
            if post_id == 0:
                post_form = Posts(title=title, sub_title=sub_title, post_content=post_content, posted_by=posted_by, slug=slug, posted_at=datetime.now())
                db.session.add(post_form)
                db.session.commit()
            else:
                post_form = Posts.query.filter_by(post_id=post_id).first()
                post_form.title = title
                post_form.sub_title = sub_title
                post_form.posted_by = posted_by
                post_form.post_content = post_content
                post_form.slug = slug
                db.session.commit()
                return redirect('/post-edit/'+post_id)

        action_name = "Edit"
        action = '/post-edit/'+post_id
        post_data = Posts.query.filter_by(post_id=post_id).first()
        return render_template('post-add-edit.html', params=params, action=action, action_name=action_name,
                               post=post_data, is_auth=session['user'])

@app.route('/logout')
def logout():
    if 'user' in session and session['user'] == params['admin_username']:
        session['user'] = None
    return redirect('/login')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_username']:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return "file uploaded successfully"
    return redirect('/login')

if __name__ == '__main__':
    app.run()

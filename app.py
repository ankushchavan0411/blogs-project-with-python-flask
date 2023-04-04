from flask import Flask, render_template

app = Flask(__name__)


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

@app.route('/contact')
def contact():  # put application's code here
    return render_template('contact.html')

@app.route('/post')
def post():  # put application's code here
    return render_template('post.html')
if __name__ == '__main__':
    app.run()

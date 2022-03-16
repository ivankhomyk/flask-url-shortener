import random
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from string import ascii_uppercase, ascii_lowercase
from typing import NoReturn


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class URLs(db.Model):
    """
    A representation of a URL, which is stored in a database
    """
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(5))

    def __init__(self, long, short):
        """
        :param long: standard link, provided by a user
        :param short: short version of a link, created by the app
        """
        self.long = long
        self.short = short


@app.before_first_request
def create_tables() -> NoReturn:
    """
    Creates tables in a database for storing info about URLs
    :return: NoReturn
    """
    db.create_all()


def shorten_url() -> str:
    """
    Shortens a standard link by means of randomly-generated combination of letters
    :return: str
    """
    letters = ascii_uppercase + ascii_lowercase
    while True:
        random_letters = random.choices(letters, k=5)
        random_letters = "".join(random_letters)
        short_url = URLs.query.filter_by(short=random_letters).first()
        if not short_url:
            return random_letters


@app.route('/', methods=['POST', 'GET'])
def home():
    """
    Main function with the help of which user can input a standard function,
    and then be redirected to get a short link
    """
    if request.method == 'POST':
        url_received = request.form["name"]
        found_url = URLs.query.filter_by(long=url_received).first()
        # if url already exists in a database, return it
        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))
        # generating a new url, since it doesn't exist
        else:
            short_url = shorten_url()
            new_url = URLs(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('home.html')


@app.route('/display/<url>')
def display_short_url(url):
    """
    Function returns a displayed page with a short URL
    :param url: randomly-generated unique key for distinguishing the URL
    """
    return render_template('shorturl.html', short_url_display=url)


@app.route('/<short_url>')
def redirection(short_url):
    """
    Redirects a user to the initial URL via its shorter representation
    :param short_url: shorter version of the initial URL
    """
    long_url = URLs.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>URL does not exist yet</h1>'


if __name__ == '__main__':
    app.run(port=5000, debug=False)

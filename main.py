from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
import requests

app = Flask(__name__)

#Database setup
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collection.db'

db = SQLAlchemy(app)

movie_API_key = "46fb1ec5b38db8b5d893a3e41effb0a2"
movie_API_url = "https://api.themoviedb.org/3/search/movie"
movie_detail_API_url = "https://api.themoviedb.org/3/movie/"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.Text)
    img_url = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Title: {}>'.format(self.title)

    def __init__(self, movie_detail):
        self.title = movie_detail['title']
        self.img_url = movie_detail['img_url']
        self.year = movie_detail['year']
        self.description = movie_detail['description']
        self.rating = 0
        self.ranking = 10
        self.review = 'Please leave some review.'
        print("Moive successfully created.")


Bootstrap(app)

app.app_context().push()

class EditForm(FlaskForm):

    rating = FloatField(label='Your Rating out of 10 e.g. 7.5',
                        validators=[DataRequired(), NumberRange(min=0, max=10, message="out of range")])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')

class AddForm(FlaskForm):
    movie_title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()

    for key, val in enumerate(movies):
        val.ranking = len(movies) - key
    print(movies)
    db.session.commit()
    return render_template("index.html", movies=movies)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = EditForm(request.form)
    id = request.args.get('id')
    movie = Movie.query.get(id)

    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)

@app.route("/delete")
def delete():
    id = request.args.get('id')
    movie = Movie.query.get(id)
    print(movie)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = request.form.get('movie_title')
        params = {
            'api_key': movie_API_key,
            'language': 'en-US',
            'query': movie_title,
        }
        result = requests.get(movie_API_url, params=params)
        movie_list = result.json()['results']
        print(result.json()['results'])
        return render_template('select.html', movies=movie_list)
    return render_template('add.html', form=form)

@app.route("/select/<int:movie_id>")
def select(movie_id):
    print(movie_id)
    params = {
        'api_key': movie_API_key,
        'language': 'en-US',
    }
    url = movie_detail_API_url + str(movie_id)
    result = requests.get(url, params=params).json()
    movie_detail = {
        'title': result['original_title'],
        'img_url': f'https://www.themoviedb.org/t/p/w300_and_h450_bestv2/{result["poster_path"]}',
        'year': result['release_date'].split('-')[0],
        'description': result['overview'],
    }
    new_movie = Movie(movie_detail)
    db.session.add(new_movie)
    db.session.commit()
    print(new_movie.id)
    return redirect(url_for('edit', id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)

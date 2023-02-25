
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schem = MovieSchema()
director_schem = DirectorSchema()
genre_schem = GenreSchema()
movies_schem = MovieSchema(many=True)
directors_schem = MovieSchema(many=True)
genres_schem = MovieSchema(many=True)

movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id_args = request.args.get('director_id')
        genre_id_args = request.args.get('genre_id')
        if director_id_args and genre_id_args:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id_args, Movie.director_id == director_id_args).all()
            return movies_schem.dump(movies)
        if director_id_args:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id_args).all()
            return movies_schem.dump(movies)
        if director_id_args:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id_args).all()
            return movies_schem.dump(movies)
        else:
            result = db.session.query(Movie).all()
            return movies_schem.dump(result), 200

    def post(self):
        req = request.json()
        result = Movie(**req)
        with db.session.begin():
            db.session.add(result)
        return '', 201


@movies_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        if db.session.query(Movie).get(id):
            result = db.session.query(Movie).get(id)
            return movie_schem.dump(result), 200
        else:
            return '', 404

    def delete(self, id):
        if db.session.query(Movie).get(id):
            result = db.session.query(Movie).get(id)
            db.session.delete(result)
            db.session.commit()
            return '', 204
        else:
            return '', 404



if __name__ == '__main__':
    app.run(debug=True)

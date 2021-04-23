from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

HOST_URL = "https://t2-antonia-christensen.herokuapp.com/"

class ArtistModel(db.Model):
    id = db.Column(db.String(22), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    albums = db.Column(db.String(200), nullable=False)
    tracks = db.Column(db.String(200), nullable=False)
    self_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Artist(id = {id}, name = {name}, age = {age}, albums = {albums}, tracks = {tracks}, self = {lself_url})"

#db.create_all()

artist_post_args = reqparse.RequestParser()
artist_post_args.add_argument("name", type=str, help="Name of the artist is required", required=True)
artist_post_args.add_argument("age", type=int, help="Age of the arstist is required", required=True)

artist_fields = {
    'id': fields.String,
    'name': fields.String,
    'age': fields.Integer,
    'albums': fields.String,
    'tracks': fields.String,
    'self': fields.String(attribute='self_url')
}


class Artist(Resource):
    @marshal_with(artist_fields)
    def get(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="Could not find artist with that id...")
        return result
    
    def delete(self, video_id):
        return "", 204

class ArtistList(Resource):
    @marshal_with(artist_fields)
    def get(self):
        result = ArtistModel.query.all()
        if not result:
            abort(404, message="No artists")
        return result
    
    @marshal_with(artist_fields)
    def post(self):
        args = artist_post_args.parse_args()
        artist_id = b64encode(args['name'].encode()).decode('utf-8')
        if len(artist_id) > 22:
            artist_id = artist_id[0:21]
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if result:
            abort(409, message="Artist id taken...")
        albums_url = HOST_URL + "artists/" + artist_id +"/albums"
        tracks_url = HOST_URL + "artists/" + artist_id +"/tracks"
        artist_url = HOST_URL + "artists/" + artist_id 
        artist = ArtistModel(id=artist_id, name=args['name'], age=args['age'],albums= albums_url,tracks= tracks_url,self_url=artist_url)
        db.session.add(artist)
        db.session.commit()
        return artist, 201


class Home(Resource):
    def get(self):
        return "Welcome to my API"

api.add_resource(Home, "/")
api.add_resource(Artist, "/artists/<string:artist_id>")
api.add_resource(ArtistList, "/artists")

if __name__ == "__main__":
    app.run(debug=True)

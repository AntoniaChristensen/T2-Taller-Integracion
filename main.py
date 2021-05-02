from flask import Flask, request
from flask_restful import Api, Resource, abort, fields, marshal_with
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
        return f"Artist(id = {id}, name = {name}, age = {age}, albums = {albums}, tracks = {tracks}, self = {self_url})"

class AlbumModel(db.Model):
    id = db.Column(db.String(22), primary_key=True)
    artist_id = db.Column(db.String(22), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    tracks = db.Column(db.String(200), nullable=False)
    self_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Album(id = {id}, artist_id = {artist_id},  genre = {genre}, artist = {artist}, tracks = {tracks}, self = {self_url})"

class TrackModel(db.Model):
    id = db.Column(db.String(22), primary_key=True)
    album_id = db.Column(db.String(22), nullable=False)
    artist_id = db.Column(db.String(22), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    times_played = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200), nullable=False)
    self_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Track(id = {id}, album_id = {album_id}, artist_id = {artist_id},  name = {name}, artist = {artist}, duration = {duration}, times_played = {times_played}, album = {album}, self = {self_url})"

#db.create_all()

def non_string(s):
    if not isinstance(s,str):
        raise TypeError("Must be a string")
    return s

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
            abort(404, message="Artist doesn't exist")
        return result
    
    def delete(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="Artist doesn't exist")
        albums = AlbumModel.query.filter_by(artist_id=artist_id).all()
        if albums:
            for album in albums:
                db.session.delete(album)
        songs = TrackModel.query.filter_by(artist_id=artist_id).all()
        if songs:
            for track in songs:
                db.session.delete(track)        
        db.session.delete(result)
        db.session.commit()
        return "", 204

class ArtistList(Resource):
    @marshal_with(artist_fields)
    def get(self):
        result = ArtistModel.query.all()
        if not result:
            lista = []
            return lista, 200
        return result
    
    @marshal_with(artist_fields)
    def post(self):
        args = request.get_json()
        if "name" not in args.keys():
            abort(400, message="Must include name")
        if "age" not in args.keys():
            abort(400, message="Must include age")
        if not isinstance(args["name"], str):
            abort(400, message="Name must be a string")
        if not isinstance(args["age"], int):
            abort(400, message="Age must be an integer")
        artist_id = b64encode(args['name'].encode()).decode('utf-8')
        if len(artist_id) > 22:
            artist_id = artist_id[0:22]
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if result:
            return result, 409
        albums_url = HOST_URL + "artists/" + artist_id +"/albums"
        tracks_url = HOST_URL + "artists/" + artist_id +"/tracks"
        artist_url = HOST_URL + "artists/" + artist_id 
        artist = ArtistModel(id=artist_id, name=args['name'], age=args['age'],albums= albums_url,tracks= tracks_url,self_url=artist_url)
        db.session.add(artist)
        db.session.commit()
        return artist, 201

album_fields = {
    'id': fields.String,
    'artist_id': fields.String,
    'name': fields.String,
    'genre': fields.String,
    'artist': fields.String,
    'tracks': fields.String,
    'self': fields.String(attribute='self_url')
}

class Album(Resource):
    @marshal_with(album_fields)
    def get(self, album_id):
        result = AlbumModel.query.filter_by(id=album_id).first()
        if not result:
            abort(404, message="Album doesn't exist")
        return result
    
    def delete(self, album_id):
        result = AlbumModel.query.filter_by(id=album_id).first()
        if not result:
            abort(404, message="Album doesn't exist")
        tracks = TrackModel.query.filter_by(album_id=album_id).all()
        if tracks:
            for song in tracks:
                db.session.delete(song)
        db.session.delete(result)
        db.session.commit()
        return "", 204

class AlbumList(Resource):
    @marshal_with(album_fields)
    def get(self):
        result = AlbumModel.query.all()
        if not result:
            return "", 200
        return result

class AlbumArtist(Resource):
    @marshal_with(album_fields)
    def get(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(404, message="Artist doesn't exist")
        result = AlbumModel.query.filter_by(artist_id=artist_id).all()
        if not result:
            return "", 200
        return result

    @marshal_with(album_fields)
    def post(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(422, message="Artist doesn't exist")
        args = request.get_json()
        if "name" not in args.keys():
            abort(400, message="Must include name")
        if "genre" not in args.keys():
            abort(400, message="Must include genre")
        if not isinstance(args["name"], str):
            abort(400, message="Name must be a string")
        if not isinstance(args["genre"], str):
            abort(400, message="Genre must be a string")
        to_encode = args['name'] + ":" + artist_id
        album_id = b64encode(to_encode.encode()).decode('utf-8')
        if len(album_id) > 22:
            album_id = album_id[0:22]
        result = AlbumModel.query.filter_by(id=album_id).first()
        if result:
            return result, 409
        artist_url = HOST_URL + "artists/" + artist_id 
        tracks_url = artist_url + "/tracks"
        album_url = HOST_URL + "albums/" + album_id 
        album = AlbumModel(id=album_id, artist_id=artist_id, name=args['name'], genre=args['genre'],artist= artist_url,tracks= tracks_url,self_url=album_url)
        db.session.add(album)
        db.session.commit()
        return album, 201
    

    def put(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(404, message="Artist doesn't exist")
        songs = TrackModel.query.filter_by(artist_id=artist_id).all()
        if not songs:
            return "", 200
        for track in songs:
            track.times_played += 1
        db.session.commit()
        return "", 200

track_fields = {
    'id': fields.String,
    'album_id': fields.String,
    'name': fields.String,
    'duration': fields.Float,
    'times_played': fields.Integer,
    'artist': fields.String,
    'album': fields.String,
    'self': fields.String(attribute='self_url')
}

class Track(Resource):
    @marshal_with(track_fields)
    def get(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="Track doesn't exist")
        return result
    
    def put(self, track_id):
        track_exists = TrackModel.query.filter_by(id=track_id).first()
        if not track_exists:
            abort(404, message="Track doesn't exist")
        track_exists.times_played += 1
        db.session.commit()
        return "", 200
    
    def delete(self, track_id):
        track = TrackModel.query.filter_by(id=track_id).first()
        if not track:
            abort(404, message="Track doesn't exist")
        db.session.delete(track)
        db.session.commit()
        return "", 204

class TrackList(Resource):
    @marshal_with(track_fields)
    def get(self):
        result = TrackModel.query.all()
        if not result:
            return "", 200
        return result

class TrackArtist(Resource):
    @marshal_with(track_fields)
    def get(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(404, message="Artist doesn't exist")
        result = TrackModel.query.filter_by(artist_id=artist_id).all()
        if not result:
            return "", 200
        return result

class TrackAlbum(Resource):
    @marshal_with(track_fields)
    def get(self, album_id):
        album_exists = AlbumModel.query.filter_by(id=album_id).first()
        if not album_exists:
            abort(404, message="Album doesn't exist")
        result = TrackModel.query.filter_by(album_id=album_id).all()
        if not result:
            return "", 200
        return result

    @marshal_with(track_fields)
    def post(self, album_id):
        album_exists = AlbumModel.query.filter_by(id=album_id).first()
        if not album_exists:
            abort(422, message="Album doesn't exist")
        args = request.get_json()
        if "name" not in args.keys():
            abort(400, message="Must include name")
        if "duration" not in args.keys():
            abort(400, message="Must include duration")
        if not isinstance(args["name"], str):
            abort(400, message="Name must be a string")
        if not isinstance(args["duration"], float):
            abort(400, message="Duration must be a float")
        to_encode = args['name'] + ":" + album_id
        track_id = b64encode(to_encode.encode()).decode('utf-8')
        if len(track_id) > 22:
            track_id = track_id[0:22]
        result = TrackModel.query.filter_by(id=track_id).first()
        if result:
            return result, 409
        artist_id = album_exists.artist_id
        artist_url = HOST_URL + "artists/" + artist_id 
        album_url = HOST_URL + "albums/" + album_id
        track_url = HOST_URL + "tracks/" + track_id
        track = TrackModel(id=track_id, album_id=album_id, artist_id=artist_id, name=args['name'], duration=args['duration'],times_played= 0, artist= artist_url,album= album_url,self_url=track_url)
        db.session.add(track)
        db.session.commit()
        return track, 201
    
    def put(self, album_id):
        album_exists = AlbumModel.query.filter_by(id=album_id).first()
        if not album_exists:
            abort(404, message="Album doesn't exist")
        songs = TrackModel.query.filter_by(album_id=album_id).all()
        if not songs:
            return "", 200
        for track in songs:
            track.times_played += 1
        db.session.commit()
        return "", 200
    
    

class Home(Resource):
    def get(self):
        return "Welcome to my API"

api.add_resource(Home, "/")
api.add_resource(Artist, "/artists/<string:artist_id>")
api.add_resource(ArtistList, "/artists")
api.add_resource(Album, "/albums/<string:album_id>")
api.add_resource(AlbumList, "/albums")
api.add_resource(AlbumArtist, "/artists/<string:artist_id>/albums", "/artists/<string:artist_id>/albums/play")
api.add_resource(TrackArtist, "/artists/<string:artist_id>/tracks")
api.add_resource(Track, "/tracks/<string:track_id>", "/tracks/<string:track_id>/play")
api.add_resource(TrackList, "/tracks")
api.add_resource(TrackAlbum, "/albums/<string:album_id>/tracks", "/albums/<string:album_id>/tracks/play")

if __name__ == "__main__":
    app.run(debug=True)

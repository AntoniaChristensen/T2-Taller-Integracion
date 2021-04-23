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
    duration = db.Column(db.Integer, nullable=False)
    times_played = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200), nullable=False)
    self_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Track(id = {id}, album_id = {album_id}, artist_id = {artist_id},  name = {name}, artist = {artist}, duration = {duration}, times_played = {times_played}, album = {album}, self = {self_url})"

#db.create_all()

artist_post_args = reqparse.RequestParser()
artist_post_args.add_argument("name", type=str, help="Name of the artist is required", required=True)
artist_post_args.add_argument("age", type=int, help="Age of the artist is required", required=True)

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
    
    def delete(self, artist_id):
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

album_post_args = reqparse.RequestParser()
album_post_args.add_argument("name", type=str, help="Name of the album is required", required=True)
album_post_args.add_argument("genre", type=str, help="Genre of the album is required", required=True)

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
            abort(404, message="Could not find album with that id...")
        return result
    
    def delete(self, artist_id):
        return "", 204

class AlbumList(Resource):
    @marshal_with(album_fields)
    def get(self):
        result = AlbumModel.query.all()
        if not result:
            abort(404, message="No albums")
        return result

class AlbumArtist(Resource):
    @marshal_with(album_fields)
    def get(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(422, message="Artist doesn't exist")
        result = AlbumModel.query.filter_by(artist_id=artist_id).all()
        if not result:
            abort(404, message="No albums for that artist")
        return result

    @marshal_with(album_fields)
    def post(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(422, message="Artist doesn't exist")
        args = album_post_args.parse_args()
        album_id = b64encode(args['name'].encode()).decode('utf-8')
        if len(album_id) > 22:
            album_id = album_id[0:21]
        result = AlbumModel.query.filter_by(id=album_id).first()
        if result:
            abort(409, message="Album id taken...")
        
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
            abort(200, message="No songs for that artist")
        for track in songs:
            track.times_played += 1
        db.session.commit()
        return "", 200

track_post_args = reqparse.RequestParser()
track_post_args.add_argument("name", type=str, help="Name of the track is required", required=True)
track_post_args.add_argument("duration", type=int, help="Duration of the track is required", required=True)

track_fields = {
    'id': fields.String,
    'album_id': fields.String,
    'name': fields.String,
    'duration': fields.Integer,
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
            abort(404, message="Could not find track with that id...")
        return result
    
    def delete(self, track_id):
        return "", 204

class TrackList(Resource):
    @marshal_with(track_fields)
    def get(self):
        result = TrackModel.query.all()
        if not result:
            abort(404, message="No tracks")
        return result

class TrackArtist(Resource):
    @marshal_with(album_fields)
    def get(self, artist_id):
        artist_exists = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist_exists:
            abort(422, message="Artist doesn't exist")
        result = TracksModel.query.filter_by(artist_id=artist_id).all()
        if not result:
            abort(404, message="No tracks for that artist")
        return result

class TrackAlbum(Resource):
    @marshal_with(track_fields)
    def get(self, album_id):
        album_exists = AlbumModel.query.filter_by(id=album_id).first()
        if not album_exists:
            abort(422, message="Album doesn't exist")
        result = TrackModel.query.filter_by(album_id=album_id).all()
        if not result:
            abort(404, message="No tracks for that album")
        return result

    @marshal_with(track_fields)
    def post(self, album_id):
        album_exists = AlbumModel.query.filter_by(id=album_id).first()
        if not album_exists:
            abort(422, message="Album doesn't exist")
        args = tracks_post_args.parse_args()
        track_id = b64encode(args['name'].encode()).decode('utf-8')
        if len(track_id) > 22:
            track_id = track_id[0:21]
        result = TrackModel.query.filter_by(id=track_id).first()
        if result:
            abort(409, message="Track id taken...")
        
        artist_url = HOST_URL + "artists/" + artist_id 
        album_url = HOST_URL + "albums/" + album_id
        track_url = HOST_URL + "tracks/" + track_id
        artist_id = album_exists.artist_id
        track = TrackModel(id=track_id, album_id=album_id, artist_id=artist_id, name=args['name'], duration=args['duration'],times_played= 0, artist= artist_url,album= album_url,self_url=track_url)
        db.session.add(track)
        db.session.commit()
        return track, 201
    
    def put(self, album_id):
        album_exists = AlbumModel.query.filter_by(id=album_id).first()
        if not album_exists:
            abort(404, message="Album doesn't exist")
        songs = TrackModel.query.filter_by(album_id=track_id).all()
        if not songs:
            abort(200, message="No songs in that album")
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
api.add_resource(Track , "/tracks/<string:track_id>", "/tracks/<string:track_id>/play")
api.add_resource(TrackList, "/tracks")
api.add_resource(TrackAlbum, "/albums/<string:album_id>/tracks", "/albums/<string:album_id>/tracks/play")

if __name__ == "__main__":
    app.run(debug=True)

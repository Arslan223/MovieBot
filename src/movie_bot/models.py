from dataclasses import dataclass
from datetime import datetime
import typing as tp

from peewee import (
    ForeignKeyField,
    CharField,
    IntegerField,
    FloatField,
    BooleanField,
    TextField,
    DateTimeField,
    Model,
    PostgresqlDatabase,
    SqliteDatabase
)
import os

db = PostgresqlDatabase(
    os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PW"],
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"]
)
# db = SqliteDatabase(
#     "movie_bot"
# )


class User(Model):
    tg_id = IntegerField(unique=True, verbose_name="Telegram ID")

    class Meta:
        database = db
        table_name = "users"


class Movie(Model):
    movie_type = CharField(verbose_name="Movie Type", max_length=1024)
    film_id = IntegerField(unique=True, verbose_name="Film ID")
    name = CharField(verbose_name="Name", null=True, max_length=1024)
    name_en = CharField(verbose_name="Name in english", null=True, max_length=1024)
    year = CharField(verbose_name="Year", null=True, max_length=1024)
    description = CharField(default="", verbose_name="Description", null=True, max_length=1024)
    length = CharField(verbose_name="Movie length", null=True, max_length=1024)
    countries = TextField(verbose_name="Countries")
    genres = TextField(verbose_name="Genres", null=True)
    rating = FloatField(verbose_name="Rating", null=True)
    poster_url = TextField(verbose_name="Poster URL")
    searched_torrents = BooleanField(default=False, verbose_name="Torrents are searched?")

    class Meta:
        database = db
        table_name = "movies"


class Torrent(Model):
    movie = ForeignKeyField(Movie, backref="torrents")
    title = CharField(verbose_name="Title")
    torrent_link = TextField(verbose_name="Torrent file link")

    class Meta:
        database = db
        table_name = "torrents"


class SearchInstance(Model):
    search_query = TextField(verbose_name="Search query")

    class Meta:
        database = db
        table_name = "search_instances"


class SearchHistoryConnection(Model):
    search_instance = ForeignKeyField(SearchInstance, backref="user_connections")
    user = ForeignKeyField(User, backref="search_history")

    class Meta:
        database = db
        table_name = "search_history_connections"


class MovieSearchInstanceConnection(Model):
    movie = ForeignKeyField(Movie, backref="search_instance_connections")
    search_instance = ForeignKeyField(SearchInstance, backref="movie_connections")

    class Meta:
        database = db
        table_name = "movie_search_instance_connections"


class MovieUserConnection(Model):
    movie = ForeignKeyField(Movie, backref="user_connections")
    user = ForeignKeyField(User, backref="movie_connections")
    counter = IntegerField(default=0, verbose_name="Movie count rate")

    class Meta:
        database = db
        table_name = "movie_user_connections"


class FavouriteConnection(Model):
    movie = ForeignKeyField(Movie, backref="favourite_connections")
    user = ForeignKeyField(User, backref="favourite_movie_connections")

    class Meta:
        database = db
        table_name = "favourite_connections"


db.create_tables([
    User,
    Movie,
    Torrent,
    SearchInstance,
    MovieSearchInstanceConnection,
    MovieUserConnection,
    FavouriteConnection,
    SearchHistoryConnection
])

import typing as tp

from .models import Movie


def simplify_by_key(iterable: tp.Iterable, key: str) -> tp.Iterable[str]:
    for obj in iterable:
        yield obj[key]


def get_movie_instance(raw_movie: dict):
    movie = Movie.get_or_none(film_id=raw_movie["filmId"])
    if movie is not None:
        return movie

    name_ru = raw_movie["nameRu"] if "nameRu" in raw_movie.keys() else None
    name_original = raw_movie["nameOriginal"] if "nameOriginal" in raw_movie.keys() else None
    name_en = raw_movie["nameEn"] if "nameEn" in raw_movie.keys() else None
    if name_ru == "null":
        name_ru = None
    if name_original == "null":
        name_original = None
    if name_en == "null":
        name_en = None

    name = None
    if name_ru is not None:
        name = name_ru
    elif name_original is not None:
        name = name_original
    elif name_en is not None:
        name = name_en

    rating = raw_movie["rating"] if "rating" in raw_movie.keys() else None
    if rating == "null":
        rating = None

    movie = Movie(
        movie_type="Сериал" if raw_movie["type"] == "TV_SERIES" else "Фильм",
        film_id=raw_movie["filmId"] if "filmId" in raw_movie.keys() else None,
        name=name,
        name_en=name_original if name_original is not None else name_en,
        year=raw_movie["year"] if "year" in raw_movie.keys() else "",
        description=(raw_movie["description"][:800] + "...") if "description" in raw_movie.keys() else None,
        length=raw_movie["filmLength"] if "filmLength" in raw_movie.keys() else None,
        countries=", ".join(simplify_by_key(raw_movie["countries"], "country")),
        genres=", ".join(simplify_by_key(raw_movie["genres"], "genre")),
        rating=rating,
        poster_url=raw_movie["posterUrl"] if "posterUrl" in raw_movie.keys() else None
    )
    movie.save()

    return movie


def to_movie_instances(raw_movies: dict, max_movies: int = 5) -> tp.Iterable[Movie]:
    counter = 0
    for raw_movie in raw_movies["films"]:
        counter += 1

        yield get_movie_instance(raw_movie)

        if counter >= max_movies:
            break

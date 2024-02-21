from functools import wraps
import aiohttp
import asyncio
import typing as tp
import json

from Python_ARQ import ARQ

from .settings import KPSettings, ARQSettings
from .models import Movie, Torrent
from .utils import to_movie_instances

kp_settings = KPSettings()
arq_settings = ARQSettings()


def kp_url_from(endpoint: str) -> str:
    return kp_settings.kp_base_url + endpoint


def with_kinopoisk() -> tp.Callable:
    def wrapper(func: tp.Callable) -> tp.Callable:
        @wraps(func)
        async def wrapped(*args):
            async with aiohttp.ClientSession(headers={
                'X-API-KEY': kp_settings.kp_api_token,
                'Content-Type': 'application/json'
            }) as session:
                return await func(*args, session=session)

        return wrapped

    return wrapper


def with_arq() -> tp.Callable:
    def wrapper(func: tp.Callable) -> tp.Callable:
        @wraps(func)
        async def wrapped(*args):
            async with aiohttp.ClientSession() as session:
                arq = ARQ(
                    arq_settings.arq_api_url,
                    arq_settings.arq_api_key,
                    session
                )

                return await func(*args, arq=arq)

        return wrapped

    return wrapper


async def make_torrent(magnet: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=arq_settings.torr_conv_url, data={"magnet": magnet},
                                allow_redirects=False) as response:
            return str(response.headers['Location'])


@with_arq()
async def gen_torrents(movie: Movie, arq):
    if movie.movie_type == "Сериал":
        query = "{} complete".format(movie.name_en)
    else:
        query = "{} {}".format(movie.name_en, movie.year)

    torrent_search_instance = await arq.torrent(query)

    for torrent in torrent_search_instance.result[:arq_settings.arq_max_torrents]:
        try:
            torrent_inst = Torrent(title=torrent.name, torrent_link=(await make_torrent(torrent.magnet)), movie=movie)
            torrent_inst.save()
        except AttributeError:
            pass
    movie.searched_torrents = True
    movie.save()


@with_kinopoisk()
async def get_films(keyword: str, session: aiohttp.ClientSession) -> tp.Iterable[Movie]:
    async with session.get(kp_url_from("/v2.1/films/search-by-keyword"), params={"keyword": keyword}) as response:
        return to_movie_instances(
            json.loads(await response.text()),
            max_movies=kp_settings.kp_max_movies
        )


@with_kinopoisk()
async def get_film_info(kinopoisk_id: int, session: aiohttp.ClientSession) -> dict:
    async with session.get(kp_url_from(f"/v2.2/films/{str(kinopoisk_id)}")) as response:
        return json.loads(await response.text())


async def main():
    print(await get_films("Venom"))
    print(await get_films("остров собак"))
    print(await get_films("магия лунного света"))
    print(await get_films("Мстители: война бесконечности"))
    print(await get_films("город в котором меня нет"))
    print(await get_films("как витька чеснок вез леху штыря в дом инвалидов"))


if __name__ == "__main__":
    asyncio.run(main())

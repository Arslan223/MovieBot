from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

import typing as tp

from .settings import TGSettings, TGTextTemplates
from .wrappers import get_films, get_film_info, gen_torrents
from .utils import get_movie_instance
from .models import (User, Movie, SearchInstance, MovieSearchInstanceConnection,
                     FavouriteConnection, SearchHistoryConnection,
                     MovieUserConnection)

tg_settings = TGSettings()
tg_text_templates = TGTextTemplates()

app = Client(
    "bot",
    api_id=tg_settings.tg_api_id,
    api_hash=tg_settings.tg_api_hash,
    bot_token=tg_settings.tg_bot_token,
    workdir="."
)


async def generate_films_keyboard(query: tp.Optional[str], user: User, search_instance: SearchInstance = None):
    if search_instance is None:
        search_instance = SearchInstance.get_or_none(search_query=query)
    inline_buttons = []
    if search_instance is None:
        search_instance = SearchInstance(search_query=query)
        search_instance.save()
        search_history_connection = SearchHistoryConnection(user=user, search_instance=search_instance)
        search_history_connection.save()
        for movie in await get_films(query):
            movie_search_instance_connection = MovieSearchInstanceConnection(
                movie=movie,
                search_instance=search_instance
            )
            movie_search_instance_connection.save()

            movie_user_connection = MovieUserConnection.get_or_none(movie=movie, user=user)
            if movie_user_connection is None:
                movie_user_connection = MovieUserConnection(movie=movie, user=user)
                movie_user_connection.save()

    for movie_connection in search_instance.movie_connections:
        inline_buttons.append([
            InlineKeyboardButton(
                text=(", ".join((movie_connection.movie.name, movie_connection.movie.year))),
                callback_data=f"show_movie:{search_instance.id}:{movie_connection.movie.film_id}"
            )
        ])

    return inline_buttons


async def generate_torrents_keyboard(movie: Movie):
    if not movie.searched_torrents:
        await gen_torrents(movie)

    inline_buttons = []
    for torrent in movie.torrents:
        inline_buttons.append([
            InlineKeyboardButton(
                text=torrent.title,
                url=torrent.torrent_link
            )
        ])

    return inline_buttons


async def generate_history_keyboard(user: User, page: int):
    inline_buttons = []
    for search_history_conn in (user.search_history
            .paginate(page, 5)):
        inline_buttons.append([
            InlineKeyboardButton(
                text=search_history_conn.search_instance.search_query,
                callback_data=f'show_search_instance:{search_history_conn.search_instance.id}:'
            )
        ])

    arrow_buttons = []
    if page > 1:
        arrow_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"show_history:{str(page - 1)}"
            )
        )
    arrow_buttons.append(
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"show_history:{str(page + 1)}"
        )
    )

    return inline_buttons + [arrow_buttons]


async def generate_stats_keyboard(user: User, page: int):
    inline_buttons = []
    for movie_conn in (user.movie_connections
            .where(MovieUserConnection.counter > 0)
            .order_by(MovieUserConnection.counter.desc())
            .paginate(page, 5)):
        inline_buttons.append([
            InlineKeyboardButton(
                text="{} | {}, {}".format(movie_conn.counter, movie_conn.movie.name, movie_conn.movie.year),
                callback_data=f'show_movie:-1:{str(movie_conn.movie.film_id)}'
            )
        ])

    arrow_buttons = []
    if page > 1:
        arrow_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"show_stats:{str(page - 1)}"
            )
        )
    arrow_buttons.append(
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"show_stats:{str(page + 1)}"
        )
    )

    return inline_buttons + [arrow_buttons]


@app.on_message(filters.command(['start']))
async def on_start_command(client, message):
    user = User.get_or_none(tg_id=message.from_user.id)
    if user is None:
        user = User(tg_id=message.from_user.id)
        user.save()
    await message.reply(tg_text_templates.start_message)


@app.on_message(filters.command(['help']))
async def on_start_command(client, message):
    user = User.get_or_none(tg_id=message.from_user.id)
    if user is None:
        user = User(tg_id=message.from_user.id)
        user.save()
    await message.reply(tg_text_templates.help_message)


@app.on_message(filters.command(['history']))
async def on_history_command(client, message):
    user = User.get_or_create(tg_id=message.from_user.id)
    user = User.get(tg_id=message.from_user.id)
    history_keyboard = await generate_history_keyboard(user, 1)
    await message.reply_photo(
        photo=tg_text_templates.search_history_photo_url,
        reply_markup=InlineKeyboardMarkup(history_keyboard)
    )


@app.on_callback_query(filters.regex(r"^show_history:[0-9]+$"))
async def on_show_history(client, query):
    payload = query.data.split(":")
    page = int(payload[1])

    user = User.get_or_create(tg_id=query.from_user.id)
    user = User.get(tg_id=query.from_user.id)

    history_keyboard = await generate_history_keyboard(user, page)
    await query.edit_message_media(
        media=InputMediaPhoto(tg_text_templates.search_history_photo_url),
        reply_markup=InlineKeyboardMarkup(history_keyboard)
    )


@app.on_message(filters.command(['stats']))
async def on_history_command(client, message):
    user = User.get_or_create(tg_id=message.from_user.id)
    user = User.get(tg_id=message.from_user.id)
    stats_keyboard = await generate_stats_keyboard(user, 1)
    await message.reply_photo(
        photo=tg_text_templates.stats_photo_url,
        reply_markup=InlineKeyboardMarkup(stats_keyboard)
    )


@app.on_callback_query(filters.regex(r"^show_stats:[0-9]+$"))
async def on_show_stats(client, query):
    payload = query.data.split(":")
    page = int(payload[1])

    user = User.get_or_create(tg_id=query.from_user.id)
    user = User.get(tg_id=query.from_user.id)

    stats_keyboard = await generate_stats_keyboard(user, page)
    await query.edit_message_media(
        media=InputMediaPhoto(tg_text_templates.stats_photo_url),
        reply_markup=InlineKeyboardMarkup(stats_keyboard)
    )


@app.on_message(filters.text)
async def search_query(client, message):
    user = User.get_or_create(tg_id=message.from_user.id)
    user = User.get(tg_id=message.from_user.id)
    films_keyboard = await generate_films_keyboard(message.text, user)
    await message.reply_photo(
        photo=tg_text_templates.results_photo_url,
        reply_markup=InlineKeyboardMarkup(films_keyboard)
    )


@app.on_callback_query(filters.regex(r"^show_search_instance:[0-9]+:(wo_back)?$"))
async def on_show_search_instance(client, query):
    payload = query.data.split(":")
    search_instance_id = int(payload[1])

    user = User.get_or_create(tg_id=query.from_user.id)
    user = User.get(tg_id=query.from_user.id)
    films_keyboard = await generate_films_keyboard(None, user,
                                                   search_instance=SearchInstance.get(id=search_instance_id))
    if payload[2] != "wo_back":
        films_keyboard.append([
            InlineKeyboardButton(
                text="↩️️",
                callback_data="show_history:1"
            )
        ])
    await query.edit_message_media(
        media=InputMediaPhoto(tg_text_templates.results_photo_url),
        reply_markup=InlineKeyboardMarkup(films_keyboard)
    )


@app.on_callback_query(filters.regex(r"^show_movie:[0-9]+:[0-9]+$"))
async def on_show_movie_callback(client, query):
    user = User.get_or_create(tg_id=query.from_user.id)
    user = User.get(tg_id=query.from_user.id)

    payload = query.data.split(":")
    search_instance_id = int(payload[1])

    if search_instance_id == -1:  # user came here from stats page
        back_button = [
            InlineKeyboardButton(
                text="↩️️",
                callback_data=f"show_stats:1"
            )
        ]
    else:
        back_button = [
            InlineKeyboardButton(
                text="↩️️",
                callback_data=f"show_search_instance:{search_instance_id}:wo_back"
            )
        ]

    movie_id = int(payload[2])
    movie = Movie.get_or_none(film_id=movie_id)
    if movie is None:
        raw_movie = await get_film_info(movie_id)
        movie = get_movie_instance(raw_movie)

    movie_user_conn = MovieUserConnection.get(movie=movie, user=user)
    movie_user_conn.counter += 1
    movie_user_conn.save()

    message_text = tg_text_templates.movie_info.format(
        movie_type=movie.movie_type,
        movie_year=movie.year,
        movie_name=movie.name,
        movie_countries=movie.countries,
        movie_rating=movie.rating,
        movie_genres=movie.genres,
        movie_description=movie.description,
        searching="----\n"
                  "__Идет поиск файлов для загрузки...__\n"
                  "__Примерное время ожидания - 1 минута.__"
    )

    await query.edit_message_media(
        media=InputMediaPhoto(media=movie.poster_url),
    )
    await query.edit_message_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup([back_button])
    )

    if movie.countries == "Россия":
        inline_keyboard = []
    else:
        inline_keyboard = await generate_torrents_keyboard(
            movie
        )
    message_text_done = tg_text_templates.movie_info.format(
        movie_type=movie.movie_type,
        movie_year=movie.year,
        movie_name=movie.name,
        movie_countries=movie.countries,
        movie_rating=movie.rating,
        movie_genres=movie.genres,
        movie_description=movie.description,
        searching="⬇️__Смотреть в оригинале__⬇️"
        if inline_keyboard
        else "❌ __Файлов для загрузки не найдено.__ ❌"
    )

    await query.edit_message_text(
        text=message_text_done,
        reply_markup=InlineKeyboardMarkup(inline_keyboard + [back_button])
    )
    await query.answer(movie.name)


if __name__ == "__main__":
    app.run()

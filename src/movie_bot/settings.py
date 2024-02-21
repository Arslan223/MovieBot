from pydantic_settings import BaseSettings
from pydantic import Field


class TGSettings(BaseSettings):
    tg_api_id: int = Field(env="TG_API_ID")
    tg_api_hash: str = Field(env="TG_API_HASH")
    tg_bot_token: str = Field(env="TG_BOT_TOKEN")


class KPSettings(BaseSettings):
    kp_api_token: str = Field(env="KP_API_TOKEN")
    kp_base_url: str = Field("https://kinopoiskapiunofficial.tech/api")
    kp_max_movies: int = Field(5, env="KP_MAX_MOVIES")


class ARQSettings(BaseSettings):
    arq_api_url: str = Field("https://arq.hamker.dev/")
    arq_api_key: str = Field(env="ARQ_API_KEY")
    arq_max_torrents: int = Field(3, env="ARQ_MAX_TORRENTS")
    torr_conv_url: str = Field("https://magnet2torrent.com/upload/")


class TGTextTemplates(BaseSettings):
    start_message: str = (
        "Привет! Я помогу тебе найти и скачать в оригинале почти любой фильм или сериал на этом свете!\n"
        "Просто введи название фильма/сериала.\n"
        "\n"
        "Помимо этого, я умею отвечать на несколько команд:\n"
        "/history - просмотр истории поисковых запросов (интерактивное меню),\n"
        "/stats - просмотр статистики по отображенным фильмам (интерактивное меню).\n"
        "\n"
        "В будущем будет доступна возможность добавлять фильмы в избранное и делиться ими в чатах, "
        "с помощью inline режима (т.е. введя никнейм бота в любом чате).\n"
        "__Example:__ `@ltmoviebot бойцовский клуб`"
    )

    help_message: str = (
        "Я помогу тебе найти и скачать в оригинале почти любой фильм или сериал на этом свете!\n"
        "Просто введи название фильма/сериала.\n"
        "\n"
        "Помимо этого, я умею отвечать на несколько команд:\n"
        "/history - просмотр истории поисковых запросов (интерактивное меню),\n"
        "/stats - просмотр статистики по отображенным фильмам (интерактивное меню).\n"
        "\n"
        "В будущем будет доступна возможность добавлять фильмы в избранное и делиться ими в чатах, "
        "с помощью inline режима (т.е. введя никнейм бота в любом чате).\n"
        "__Example:__ `@ltmoviebot бойцовский клуб`"
    )

    search_results: str = (
        "**Результаты поиска**"
    )

    movie_info: str = (
        "🎞 **{movie_type}, {movie_year}**\n"
        "\n"
        "--{movie_name}--\n"
        "__{movie_countries}__\n"
        "**{movie_rating}**\n"
        "\n"
        "**Жанры:**\n__{movie_genres}__\n"
        "**Описание:**\n"
        "||__{movie_description}__||\n"
        "\n"
        "{searching}"
    )

    results_photo_url: str = "https://sun9-68.userapi.com/impf/yhUEN5_VIA6PPj-_SVQB7Q9_USgzK2HG_kgCZg/BrXql9RPCJQ.jpg?size=1024x1024&quality=96&sign=21fa7f19db03fe2142edf9ba4ebca5ca&type=album"

    search_history_photo_url: str = "https://sun9-5.userapi.com/impf/EY99_Rp7Ojf9Wz8Z5TAuYHlzyoAY0SHEA9NhYA/sIp0Sv0kmf8.jpg?size=1024x1024&quality=96&sign=66abd1947ef0c78ba689e08c61595465&type=album"

    stats_photo_url: str = "https://sun6-21.userapi.com/impf/7wPxLEHC4O6JzT0T0ISUyjTyZJiuv8x4xIhPSQ/Pfvdy2yRb74.jpg?size=1024x1024&quality=96&sign=fdf32a0ded48a303be4fe2b32b7c9292&type=album"

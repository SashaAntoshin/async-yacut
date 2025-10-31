from http import HTTPStatus

from flask import Blueprint, jsonify, request, url_for

from .error_handlers import InvalidAPIUsage
from .models import URLMap

EMPTY_REQUEST_BODY = "Отсутствует тело запроса"
URL_REQUIRED_FIELD = '"url" является обязательным полем!'

api_bp = Blueprint("api", __name__)


@api_bp.route("/id/", methods=["POST"])
def create_short_link():
    """Создание короткой ссылки"""

    if not request.data:
        raise InvalidAPIUsage(EMPTY_REQUEST_BODY)

    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage(EMPTY_REQUEST_BODY)

    if "url" not in data:
        raise InvalidAPIUsage(URL_REQUIRED_FIELD)

    original_url = data.get("url")
    short = data.get("custom_id")

    if not short:
        short = URLMap.get_unique_short_id()

    try:
        url_map = URLMap.create(original=original_url, short=short)
    except ValueError as e:
        raise InvalidAPIUsage(str(e))

    return (
        jsonify(
            {
                "url": url_map.original,
                "short_link": url_for(
                    "main.redirect_to_url", short=url_map.short, _external=True
                ),
            }
        ),
        HTTPStatus.CREATED,
    )


@api_bp.route("/id/<short>/", methods=["GET"])
def get_original_url(short):
    """Получение оригинальной ссылки по короткому ID"""
    url_map = URLMap.get(short)

    if not url_map:
        raise InvalidAPIUsage("Указанный id не найден", HTTPStatus.NOT_FOUND)

    return jsonify({"url": url_map.original})

from http import HTTPStatus

from flask import Blueprint, jsonify, request

from .error_handlers import InvalidAPIUsage
from .models import URLMap

EMPTY_REQUEST_BODY = "Отсутствует тело запроса"
URL_REQUIRED_FIELD = '"url" является обязательным полем!'
NOT_FOUND_ID = "Указанный id не найден"

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
    try:
        url_map = URLMap.create(
            original=data["url"], short=data.get("custom_id"), validate=True
        )
    except (ValueError, RuntimeError) as e:
        raise InvalidAPIUsage(str(e))

    return (
        jsonify(dict(url=data["url"], short_link=url_map.get_short_url())),
        HTTPStatus.CREATED,
    )


@api_bp.route("/id/<short>/", methods=["GET"])
def get_original_url(short):
    """Получение оригинальной ссылки по короткому ID"""
    url_map = URLMap.get(short)

    if not url_map:
        raise InvalidAPIUsage(NOT_FOUND_ID, HTTPStatus.NOT_FOUND)
    return jsonify({"url": url_map.original})

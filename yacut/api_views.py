from http import HTTPStatus

from flask import Blueprint, jsonify, request

from yacut import db

from .constants import (
    EMPTY_REQUEST_BODY,
    INVALID_CONTENT_TYPE,
    INVALID_JSON,
    MAX_SHORT_ID_LENGTH,
    SHORT_ID_PATTERN,
)
from .error_handlers import InvalidAPIUsage
from .models import URLMap

api_bp = Blueprint("api", __name__)


def create_url_map(original_url, short):
    """Создание и сохранение URLMap"""
    url_map = URLMap(original=original_url, short=short)
    db.session.add(url_map)
    db.session.commit()
    return url_map


@api_bp.route("/id/", methods=["POST"])
def create_short_link():
    """Создание короткой ссылки"""

    if not request.data:
        raise InvalidAPIUsage(EMPTY_REQUEST_BODY)

    if request.content_type != "application/json":
        raise InvalidAPIUsage(INVALID_CONTENT_TYPE)

    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(INVALID_JSON)

    if not data:
        raise InvalidAPIUsage(EMPTY_REQUEST_BODY)

    original_url = data.get("url")
    custom_id = data.get("custom_id")

    if not original_url:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    if not original_url.startswith(("http://", "https://")):
        raise InvalidAPIUsage("Некорректный URL")

    if custom_id:
        if len(custom_id) > MAX_SHORT_ID_LENGTH:
            raise InvalidAPIUsage(
                "Указано недопустимое имя для короткой ссылки"
            )

        if not SHORT_ID_PATTERN.match(custom_id):
            raise InvalidAPIUsage(
                "Указано недопустимое имя для короткой ссылки"
            )

        existing_url = URLMap.get_by_short(custom_id)
        if existing_url:
            raise InvalidAPIUsage(
                "Предложенный вариант короткой ссылки уже существует."
            )
        short = custom_id
    else:
        short = URLMap.get_unique_short_id()

    try:
        url_map = URLMap.create(original=original_url, short=short)
    except Exception:
        db.session.rollback()
        raise InvalidAPIUsage("При сохранении ссылки произошла ошибка!")

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@api_bp.route("/id/<short>/", methods=["GET"])
def get_original_url(short):
    """Получение оригинальной ссылки по короткому ID"""
    url_map = URLMap.get_by_short(short)

    if not url_map:
        raise InvalidAPIUsage("Указанный id не найден", HTTPStatus.NOT_FOUND)

    return jsonify({"url": url_map.original})

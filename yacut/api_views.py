from flask import jsonify, Blueprint, request
from yacut import db
from .models import URLMap
from .utils import get_unique_short_id
from .error_handlers import InvalidAPIUsage

ALLOWED_CHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
api_bp = Blueprint("api", __name__)


def validate_request_data():
    """Валидация данных запроса"""
    if not request.data:
        raise InvalidAPIUsage("Отсутствует тело запроса")

    if request.content_type != "application/json":
        raise InvalidAPIUsage("Неверный Content-Type")

    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage("Некорректный JSON")

    if not data:
        raise InvalidAPIUsage("Отсутствует тело запроса")

    return data


def validate_custom_id(custom_id):
    """Валидация custom_id"""
    if len(custom_id) > 16:
        raise InvalidAPIUsage("Указано недопустимое имя для короткой ссылки")

    if not all(char in ALLOWED_CHAR for char in custom_id):
        raise InvalidAPIUsage("Указано недопустимое имя для короткой ссылки")


def check_custom_id_availability(custom_id):
    """Проверка доступности custom_id"""
    existing_url = URLMap.query.filter_by(short=custom_id).first()
    if existing_url:
        raise InvalidAPIUsage(
            "Предложенный вариант короткой ссылки уже существует."
        )


def validate_url_data(data):
    """Валидация URL данных"""
    original_url = data.get("url")
    custom_id = data.get("custom_id")

    if not original_url:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    if not original_url.startswith(("http://", "https://")):
        raise InvalidAPIUsage("Некорректный URL")

    return original_url, custom_id


def create_url_map(original_url, short_id):
    """Создание и сохранение URLMap"""
    url_map = URLMap(original=original_url, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return url_map


@api_bp.route("/id/", methods=["POST"])
def create_short_link():
    """Создание короткой ссылки"""

    data = validate_request_data()

    original_url, custom_id = validate_url_data(data)

    if custom_id:
        validate_custom_id(custom_id)
        check_custom_id_availability(custom_id)
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    create_url_map(original_url, short_id)

    return (
        jsonify(
            {
                "short_link": f"http://localhost/{short_id}",  # noqa: E231
                "url": original_url,  # noqa: E231
            }  # noqa: E231
        ),
        201,
    )


@api_bp.route("/id/<short_id>/", methods=["GET"])
def get_original_url(short_id):
    """Получение оригинальной ссылки по короткому ID"""
    url_map = URLMap.query.filter_by(short=short_id).first()

    if not url_map:
        raise InvalidAPIUsage("Указанный id не найден", 404)

    return jsonify({"url": url_map.original})

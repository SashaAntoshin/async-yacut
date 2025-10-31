from datetime import datetime
import random

from . import db

from .constants import (
    ALLOWED_CHARS,
    GENERATED_ID_ATTEMPTS,
    MAX_SHORT_LENGTH,
    ORIGINAL_LENGTH,
    SHORT_LENGTH,
    SHORT_PATTERN,
    RESERVED_SHORTS,
)

INVALID_SHORT_NAME = "Указано недопустимое имя для короткой ссылки"
SHORT_ALREADY_EXISTS = "Предложенный вариант короткой ссылки уже существует."


class URLMap(db.Model):
    """Основная модель."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LENGTH), unique=True, nullable=False, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create(original, short):
        """Создание и сохранение новой записи URLMap"""
        if not original or not isinstance(original, str):
            raise ValueError("Url не может быт пустой строкой.")
        if not short:
            short = URLMap.get_unique_short_id()
        if not short or not isinstance(short, str):
            raise ValueError("Короткая ссылка не может быть пустой строкой")
        if len(short) > MAX_SHORT_LENGTH:
            raise ValueError(INVALID_SHORT_NAME)
        if not SHORT_PATTERN.match(short):
            raise ValueError(INVALID_SHORT_NAME)
        if short in RESERVED_SHORTS or URLMap.get(short):
            raise ValueError(SHORT_ALREADY_EXISTS)

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_unique_short_id():
        """Генерация уникального короткого ID"""

        for attempt in range(GENERATED_ID_ATTEMPTS):
            short = "".join(random.choices(ALLOWED_CHARS, k=SHORT_LENGTH))

            if short not in RESERVED_SHORTS and not URLMap.get(short):
                return short

        for length in range(SHORT_LENGTH + 1, MAX_SHORT_LENGTH + 1):
            short = "".join(random.choices(ALLOWED_CHARS, k=length))
            if short not in RESERVED_SHORTS and not URLMap.get(short):
                return short
        raise RuntimeError("Не удалось сгенерировать уникальный short ID")

    @staticmethod
    def get(short):
        """Найти запись по короткой ссылке."""
        return URLMap.query.filter_by(short=short).first()

from datetime import datetime
import random

from . import db
from flask import current_app

from .constants import (
    ALLOWED_CHARS,
    GENERATED_SHORT_ATTEMPTS,
    MAX_SHORT_LENGTH,
    ORIGINAL_LENGTH,
    SHORT_LENGTH,
    SHORT_PATTERN,
    RESERVED_SHORTS,
)

INVALID_SHORT_NAME = "Указано недопустимое имя для короткой ссылки"
SHORT_ALREADY_EXISTS = "Предложенный вариант короткой ссылки уже существует."
GENERATE_ERROR = "Не удалось сгенерировать уникальный short ID"


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LENGTH), unique=True, nullable=False, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create(original, short=None):
        """Создание и сохранение новой записи URLMap"""
        if not short:
            short = URLMap.get_unique_short_id()
        if len(short) > MAX_SHORT_LENGTH:
            raise ValueError(INVALID_SHORT_NAME)
        if not SHORT_PATTERN.match(short):
            raise ValueError(INVALID_SHORT_NAME)
        if short in RESERVED_SHORTS or URLMap.get(short):
            raise ValueError(SHORT_ALREADY_EXISTS)

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        return url_map

    @staticmethod
    def get_unique_short_id():
        """Генерация уникального короткого ID"""

        for attempt in range(GENERATED_SHORT_ATTEMPTS):
            short = "".join(random.choices(ALLOWED_CHARS, k=SHORT_LENGTH))

            if short not in RESERVED_SHORTS and not URLMap.get(short):
                return short
        raise RuntimeError(GENERATE_ERROR)

    @staticmethod
    def get(short):
        """Найти запись по короткой ссылке."""
        return URLMap.query.filter_by(short=short).first()

    def get_short(self):
        """Полная кортка ссылка"""
        base_url = current_app.config.get("BASE_URL", "http://localhost")
        return f"{base_url}/{self.short}"

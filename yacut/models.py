from datetime import datetime
import random
import re

from flask import url_for

from . import db
from .constants import (
    ALLOWED_CHARS,
    GENERATED_SHORT_ATTEMPTS,
    MAX_SHORT_LENGTH,
    ORIGINAL_LENGTH,
    SHORT_LENGTH,
    SHORT_PATTERN,
    RESERVED_SHORTS,
    REDIRECT_ENPOINT
)

INVALID_SHORT_NAME = "Указано недопустимое имя для короткой ссылки"
SHORT_ALREADY_EXISTS = "Предложенный вариант короткой ссылки уже существует."
GENERATE_ERROR = "Не удалось сгенерировать уникальный short ID"
URL_REQUIRED_FIELD = "Url не может быть пустой строкой"
URL_ERROR = "Слишком длинный URL"


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LENGTH), unique=True, nullable=False, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create(original, short=None, skip_validation=False):
        """Создание и сохранение новой записи URLMap"""
        if not skip_validation and len(original) > ORIGINAL_LENGTH:
            raise ValueError(URL_ERROR)
        if not short:
            short = URLMap.get_unique_short()
        if not skip_validation and short is not None:
            if isinstance(SHORT_PATTERN, str):
                if not re.fullmatch(SHORT_PATTERN, short):
                    raise ValueError(INVALID_SHORT_NAME)
            else:
                if not SHORT_PATTERN.fullmatch(short):
                    raise ValueError(INVALID_SHORT_NAME)
        if short in RESERVED_SHORTS or URLMap.get(short):
            raise ValueError(SHORT_ALREADY_EXISTS)

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_unique_short():
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

    def get_short_url(self):
        """Полная кортка ссылка"""
        return url_for(REDIRECT_ENPOINT,
                       short=self.short, _external=True)

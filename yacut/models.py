from datetime import datetime

from flask import url_for

from yacut import db

from .constants import (
    ALLOWED_CHARS,
    GENERATED_ID_ATTEMPTS,
    MAX_SHORT_ID_LENGTH,
    ORIGINAL_LENGTH,
    SHORT_LENGTH,
)


class URLMap(db.Model):
    """Основная модель."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_ID_LENGTH), unique=True, nullable=False, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, original, short):
        """Создание и сохранение новой записи URLMap"""
        url_map = cls(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @classmethod
    def get_unique_short_id(cls):
        """Генерация уникального короткого ID"""
        import random

        for attempt in range(GENERATED_ID_ATTEMPTS):
            short = "".join(random.choices(ALLOWED_CHARS, k=SHORT_LENGTH))

            if cls.is_short_available(short):
                return short

        for length in range(SHORT_LENGTH + 1, MAX_SHORT_ID_LENGTH + 1):
            short = "".join(random.choices(ALLOWED_CHARS, k=length))
            if cls.is_short_available(short):
                return short
        raise ValueError("Не удалось сгенерировать уникальный short ID")

    @classmethod
    def is_short_available(cls, short):
        """Проверить доступность короткой ссылки."""
        return cls.get_by_short(short) is None

    @classmethod
    def get_by_short(cls, short):
        """Найти запись по короткой ссылке."""
        return cls.query.filter_by(short=short).first()

    def to_dict(self):
        "Возвращает данные в виде словаря."
        return {
            "url": self.original,
            "short_link": url_for(
                "main.redirect_to_url", short=self.short, _external=True
            ),
        }

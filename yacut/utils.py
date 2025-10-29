import string
import random


SHORT_ID_LENGTH = 6

MAX_CUSTOM_ID_LENGTH = 16

ALLOWED_SYMBOLS = string.ascii_letters + string.digits

GENERATED_ID_ATTEMPTS = 10


def get_unique_short_id(length=SHORT_ID_LENGTH):
    """Получаем короткий ID для ссылки."""
    from .models import URLMap

    for attempt in range(GENERATED_ID_ATTEMPTS):
        short_id = "".join(random.choices(ALLOWED_SYMBOLS, k=length))

        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    return get_unique_short_id(length + 1)

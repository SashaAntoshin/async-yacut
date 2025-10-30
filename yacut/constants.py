import re
import string

ALLOWED_CHARS = string.ascii_letters + string.digits
MAX_SHORT_ID_LENGTH = 16
ORIGINAL_LENGTH = 2048
SHORT_LENGTH = 6
GENERATED_ID_ATTEMPTS = 100

# текстовые констаны

EMPTY_REQUEST_BODY = "Отсутствует тело запроса"
INVALID_CONTENT_TYPE = "Неверный Content-Type"
INVALID_JSON = "Некорректный JSON"
SHORT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
ID_ERROR_MESSAGE = "Допустимы только латинские буквы и цифры"
ORIGINAL_LINK = "Длинная ссылка"
CUSTOM_ID_LABEL = "Ваш вариант короткой ссылки"
SUBMIT_LABEL = "Создать"
REQUIRED_FIELD_MESSAGE = "Обязательное поле"
INVALID_URL_MESSAGE = "Некорректная ссылка"
LENGTH_ERROR_MESSAGE = "Не более 16 символов"

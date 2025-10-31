from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileSize
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.fields import URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from .constants import MAX_SHORT_LENGTH, SHORT_PATTERN


REQUIRED_FIELD_MESSAGE = "Обязательное поле"
LENGTH_ERROR_MESSAGE = f"Не более {MAX_SHORT_LENGTH} символов"
INVALID_URL_MESSAGE = "Некорректная ссылка"
SUBMIT_LABEL = "Создать"
ID_ERROR_MESSAGE = "Допустимы только латинские буквы и цифры"
ORIGINAL_LABEL = "Длинная ссылка"
SHORT = "Ваш вариант короткой ссылки"
FILES = "Файлы"
UPLOAD = "Загрузить"
MESSAGE = "Выберите файлы"


class URLForm(FlaskForm):
    """Основная форма."""

    original_link = URLField(
        ORIGINAL_LABEL,
        validators=[
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            URL(message=INVALID_URL_MESSAGE),
            Length(max=2048),
        ],
    )
    custom_id = StringField(
        SHORT,
        validators=[
            Optional(),
            Length(max=MAX_SHORT_LENGTH, message=LENGTH_ERROR_MESSAGE),
            Regexp(
                SHORT_PATTERN.pattern,
                message=ID_ERROR_MESSAGE,
            ),
        ],
    )
    submit = SubmitField(SUBMIT_LABEL)


class FileUploadForm(FlaskForm):
    """Форма загрузки файлов."""

    files = MultipleFileField(
        FILES,
        validators=[
            FileRequired(message=MESSAGE),
            FileSize(max_size=10 * 1024 * 1024),
            FileAllowed(["jpg", "jpeg", "png", "gif", "pdf", "txt"]),
        ],
    )
    submit = SubmitField(UPLOAD)

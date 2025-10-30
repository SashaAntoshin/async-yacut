from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.fields import URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from .constants import (
    ALLOWED_CHARS,
    ID_ERROR_MESSAGE,
    INVALID_URL_MESSAGE,
    LENGTH_ERROR_MESSAGE,
    MAX_SHORT_ID_LENGTH,
    REQUIRED_FIELD_MESSAGE,
    SUBMIT_LABEL,
)


class URLForm(FlaskForm):
    """Основная форма."""

    original_link = URLField(
        "Длинная ссылка",
        validators=[
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            URL(message=INVALID_URL_MESSAGE),
        ],
    )
    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Optional(),
            Length(max=MAX_SHORT_ID_LENGTH, message=LENGTH_ERROR_MESSAGE),
            Regexp(
                f"^[{ALLOWED_CHARS}]*$",
                message=ID_ERROR_MESSAGE,
            ),
        ],
    )
    submit = SubmitField(SUBMIT_LABEL)


class FileUploadForm(FlaskForm):
    """Форма загрузки файлов."""

    files = FileField(
        "Файлы", validators=[FileRequired(message="Выберите файлы")]
    )
    submit = SubmitField("Загрузить")

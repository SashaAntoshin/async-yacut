from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Length, Optional, Regexp
from .utils import MAX_CUSTOM_ID_LENGTH, ALLOWED_SYMBOLS


class URLForm(FlaskForm):
    """Основная форма."""

    original_link = StringField(
        "Длинная ссылка",
        validators=[
            DataRequired(message="Обязательное поле"),
            URL(message="Некорректная ссылка"),
        ],
    )
    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Optional(),
            Length(max=MAX_CUSTOM_ID_LENGTH, message="Не более 16 символов"),
            Regexp(
                f"^[{ALLOWED_SYMBOLS}]*$",
                message="Допустимы только латинские буквы и цифры",
            ),
        ],
    )
    submit = SubmitField("Создать")


class FileUploadForm(FlaskForm):
    """Форма загрузки файлов."""

    files = FileField(
        "Файлы", validators=[FileRequired(message="Выберите файлы")]
    )
    submit = SubmitField("Загрузить")

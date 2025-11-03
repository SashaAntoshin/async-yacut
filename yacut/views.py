from http import HTTPStatus

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
)

from .forms import FileUploadForm, URLForm
from .models import URLMap
from .yandex_disk import upload_files_async


SHORT_COMPLETE = "Ваша новая ссылка готова:"
UPLOAD_ERROR = "Ошибка при загрузке файлов: {}"
CREATE_SHORT_ERROR = "Ошибка создания ссылки для {}: {}"
main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Главная страница для создания коротких ссылок."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template("index.html", form=form)

    try:
        return render_template(
            "index.html",
            form=form,
            full_short_url=URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data,
                validate=True,
            ).get_short_url(),
        )
    except (ValueError, RuntimeError) as e:
        flash(str(e), "error")
        return render_template("index.html", form=form)


@main_bp.route("/files", methods=["GET", "POST"])
def files_upload():
    """Загрузка файлов на Яндекс Диск."""
    form = FileUploadForm()
    if not form.validate_on_submit():
        return render_template("files.html", form=form)

    files = form.files.data

    try:
        yadisk_results = upload_files_async(files)
        yadisk_urls = [url for _, url in yadisk_results]
    except (ValueError, RuntimeError) as e:
        flash(CREATE_SHORT_ERROR.format("файлов", e), "error")
        return render_template("files.html", form=form)
    try:
        file_links = [
            dict(
                name=file.filename,
                full_short_url=URLMap.create(
                    original=url, short=None
                ).get_short_url(),
            )
            for file, url in zip(files, yadisk_urls)
        ]
        return render_template("files.html", form=form, file_links=file_links)
    except (ValueError, RuntimeError) as e:
        flash(CREATE_SHORT_ERROR.format("ссылок", e), "error")
        return render_template("files.html", form=form)


@main_bp.route("/<short>")
def redirect_to_url(short):
    """Редирект по короткой ссылке."""
    url_map = URLMap.get(short)
    if not url_map:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)

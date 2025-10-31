from http import HTTPStatus

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)

from .forms import FileUploadForm, URLForm
from .models import URLMap
from .yandex_disk import upload_files_async

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Главная страница для создания коротких ссылок."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template("index.html", form=form)

    original_url = form.original_link.data
    short = form.custom_id.data

    try:
        url_map = URLMap.create(original=original_url, short=short)
    except ValueError as e:
        flash(str(e), "error")
        return render_template("index.html", form=form)

    full_short_url = url_for(
        "main.redirect_to_url", short=url_map.short, _external=True
    )

    flash("Ваша новая ссылка готова:", "success")
    return render_template(
        "index.html", form=form, full_short_url=full_short_url
    )


@main_bp.route("/files", methods=["GET", "POST"])
def files_upload():
    """Загрузка файлов на Яндекс Диск."""
    form = FileUploadForm()
    if not form.validate_on_submit():
        return render_template("files.html", form=form)

    files = form.files.data
    token = current_app.config.get("DISK_TOKEN")

    try:
        results = upload_files_async(files, token)

        file_links = []
        successful_files = []

        for file, result in zip(files, results):
            filename, download_url = result
            try:
                url_map = URLMap.create(original=download_url, short=None)
                successful_files.append((file, url_map))
            except ValueError as e:
                flash(
                    f"Ошибка создания короткой ссылки для "
                    f"{file.filename}: {e}",
                    "error",
                )
        file_links = [
            {
                "name": file.filename,
                "full_short_url": url_for(
                    "main.redirect_to_url", short=url_map.short, _external=True
                ),
            }
            for file, url_map in successful_files
        ]

        if file_links:
            flash("Файлы успешно загружены!", "success")
        return render_template("files.html", form=form, file_links=file_links)

    except ConnectionError as e:
        flash(f"Ошибка при загрузке файлов: {str(e)}", "error")
        return render_template("files.html", form=form, file_links=[])


@main_bp.route("/<short>")
def redirect_to_url(short):
    """Редирект по короткой ссылке."""
    url_map = URLMap.get(short)
    if not url_map:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)

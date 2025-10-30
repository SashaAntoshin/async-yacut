from http import HTTPStatus

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from . import db
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
    short = form.custom_id.data.strip() if form.custom_id.data else None

    if short and short in ["files"]:
        flash("Предложенный вариант короткой ссылки уже существует.", "error")
        return render_template("index.html", form=form)

    if short and URLMap.get_by_short(short):
        flash("Предложенный вариант короткой ссылки уже существует.", "error")
        return render_template("index.html", form=form)

    short = URLMap.get_unique_short_id() if not short else short

    URLMap.create(original=original_url, short=short)

    full_short_url = url_for(
        "main.redirect_to_url", short=short, _external=True
    )

    flash("Ваша новая ссылка готова:", "success")
    return render_template(
        "index.html", form=form, short_url=short, full_short_url=full_short_url
    )


@main_bp.route("/files", methods=["GET", "POST"])
def files_upload():
    """Загрузка файлов на Яндекс Диск."""
    form = FileUploadForm()
    if not form.validate_on_submit():
        return render_template("files.html", form=form, file_links=[])

    files = request.files.getlist("files")
    token = current_app.config.get("DISK_TOKEN")

    if not token:
        flash("Ошибка конфигурации: отсутствует токен Яндекс Диска", "error")
        return render_template("files.html", form=form, file_links=[])

    try:
        results = upload_files_async(files, token)
        file_links = save_uploaded_files(files, results)

        return render_template("files.html", form=form, file_links=file_links)
    except ConnectionError as e:
        flash(f"Ошибка при загрузке файлов: {str(e)}", "error")
        return render_template("files.html", form=form, file_links=[])


def save_uploaded_files(files, results):
    """Сохранение информации о загруженных файлах в базу."""
    file_links = []

    for file, result in zip(files, results):
        if isinstance(result, Exception):
            flash(f"Ошибка загрузки {file.filename}: {str(result)}", "error")
            continue

        filename, download_url = result
        short = URLMap.get_unique_short_id()
        url_map = URLMap(original=download_url, short=short)
        db.session.add(url_map)

        full_short_url = url_for(
            "main.redirect_to_url", short=short, _external=True
        )
        file_links.append(
            {
                "name": file.filename,
                "short_url": short,
                "full_short_url": full_short_url,
            }
        )

    db.session.commit()
    flash("Файлы успешно загружены!", "success")
    return file_links


@main_bp.route("/<short>")
def redirect_to_url(short):
    """Редирект по короткой ссылке."""
    url_map = URLMap.get_by_short(short)
    if not url_map:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)

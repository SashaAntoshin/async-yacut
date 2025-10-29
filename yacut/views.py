from flask import (
    render_template,
    redirect,
    flash,
    request,
    Blueprint,
    current_app,
)
from yacut import db
from .forms import URLForm, FileUploadForm
from .models import URLMap
from .utils import get_unique_short_id
import aiohttp
import asyncio


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Главная страница для создания коротких ссылок."""
    form = URLForm()
    if form.validate_on_submit():
        return handle_url_submission(form)
    return render_template("index.html", form=form)


def handle_url_submission(form):
    """Обработка отправки формы создания короткой ссылки."""
    original_url = form.original_link.data
    custom_id = form.custom_id.data.strip() if form.custom_id.data else None

    if is_reserved_or_taken(custom_id):
        flash("Предложенный вариант короткой ссылки уже существует.", "error")
        return render_template("index.html", form=form)

    short_id = get_or_generate_short_id(custom_id)
    save_url_map(original_url, short_id)

    flash("Ваша новая ссылка готова:", "success")
    return render_template("index.html", form=form, short_url=short_id)


def is_reserved_or_taken(custom_id):
    """Проверка зарезервированных путей и существующих short_id."""
    if custom_id and custom_id in ["files"]:
        return True

    if custom_id:
        existing_url = URLMap.query.filter_by(short=custom_id).first()
        return existing_url is not None

    return False


def get_or_generate_short_id(custom_id):
    """Получение или генерация short_id."""
    return custom_id if custom_id else get_unique_short_id()


def save_url_map(original_url, short_id):
    """Сохранение URLMap в базу данных."""
    url_map = URLMap(original=original_url, short=short_id)
    db.session.add(url_map)
    db.session.commit()


@main_bp.route("/files", methods=["GET", "POST"])
def files_upload():
    """Загрузка файлов на Яндекс Диск."""
    form = FileUploadForm()
    file_links = []

    if form.validate_on_submit():
        file_links = handle_file_upload(form)

    return render_template("files.html", form=form, file_links=file_links)


def handle_file_upload(form):
    """Обработка загрузки файлов."""
    files = request.files.getlist("files")
    token = current_app.config.get("DISK_TOKEN")

    if not token:
        flash("Ошибка конфигурации: отсутствует токен Яндекс Диска", "error")
        return []

    try:
        return process_file_upload(files, token)
    except Exception as e:
        flash(f"Ошибка при загрузке файлов: {str(e)}", "error")
        return []


def process_file_upload(files, token):
    """Основной процесс загрузки файлов."""
    results = upload_files_async(files, token)
    return save_uploaded_files(files, results)


def upload_files_async(files, token):
    """Асинхронная загрузка файлов на Яндекс Диск."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(upload_files(files, token))
    loop.close()
    return results


async def upload_files(files, token):
    """Асинхронная загрузка нескольких файлов."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_single_file(session, file, token) for file in files]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def upload_single_file(session, file, token):
    """Загрузка одного файла на Яндекс Диск."""
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": f"/yacut/{file.filename}", "overwrite": "true"}

    upload_url = await get_upload_url(session, headers, params)
    await upload_file_content(session, upload_url, headers, file)
    download_url = await get_download_url(session, headers, file.filename)

    return file.filename, download_url


async def get_upload_url(session, headers, params):
    """Получение URL для загрузки файла."""
    async with session.get(
        "https://cloud-api.yandex.net/v1/disk/resources/upload",
        headers=headers,
        params=params,
    ) as response:
        if response.status != 200:
            raise Exception(f"Ошибка получения URL: {response.status}")
        upload_data = await response.json()
        return upload_data["href"]


async def upload_file_content(session, upload_url, headers, file):
    """Загрузка содержимого файла."""
    file_content = file.read()
    async with session.put(
        upload_url, headers=headers, data=file_content
    ) as response:
        if response.status not in (201, 202):
            raise Exception(f"Ошибка загрузки: {response.status}")


async def get_download_url(session, headers, filename):
    """Получение ссылки для скачивания файла."""
    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    async with session.get(
        url,
        headers=headers,
        params={"path": f"/yacut/{filename}"},
    ) as response:
        if response.status != 200:
            msg = f"Ошибка получения download URL: {response.status}"
            raise Exception(msg)
        download_data = await response.json()
        return download_data["href"]


def save_uploaded_files(files, results):
    """Сохранение информации о загруженных файлах в базу."""
    file_links = []

    for file, result in zip(files, results):
        if isinstance(result, Exception):
            flash(f"Ошибка загрузки {file.filename}: {str(result)}", "error")
            continue

        filename, download_url = result
        short_id = get_unique_short_id()
        url_map = URLMap(original=download_url, short=short_id, is_file=True)
        db.session.add(url_map)
        file_links.append({"name": file.filename, "short_url": short_id})

    db.session.commit()
    flash("Файлы успешно загружены!", "success")
    return file_links


@main_bp.route("/<short_id>")
def redirect_to_url(short_id):
    """Редирект по короткой ссылке."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)

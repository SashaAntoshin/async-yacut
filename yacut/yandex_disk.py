import asyncio
import os
from http import HTTPStatus

import aiohttp
from flask import current_app

from .error_handlers import YandexDiskError

URL_ERROR = "Ошибка получения URL: {}"
UPLOAD_ERROR = "Ошибка загрузки: {}"
DOWNLOAD_ERROR = "Ошибка получения download URL: {}"

HEADERS = {"Authorization": f"OAuth {os.getenv('DISK_TOKEN')}"}


async def upload_files(files):
    """Асинхронная загрузка нескольких файлов."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_single_file(session, file) for file in files]
        return await asyncio.gather(*tasks)


def upload_files_async(files):
    """Асинхронная загрузка файлов на Яндекс Диск."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(upload_files(files))
    loop.close()
    return results


async def upload_single_file(session, file):
    """Загрузка одного файла на Яндекс Диск."""
    await upload_file_content(
        session,
        await get_upload_url(
            session, {"path": f"/yacut/{file.filename}", "overwrite": "true"}
        ),
        file,
    )
    download_url = await get_download_url(session, file.filename)
    return file.filename, download_url


async def get_upload_url(session, params):
    """Получение URL для загрузки файла."""
    base_url = current_app.config["YANDEX_API_BASE"]
    api_version = current_app.config["API_VERSION"]
    upload_url = f"{base_url}/{api_version}/disk/resources/upload"

    async with session.get(
        upload_url, headers=HEADERS, params=params
    ) as response:
        if response.status != HTTPStatus.OK:
            raise YandexDiskError(UPLOAD_ERROR.format(response.status))
        return (await response.json())["href"]


async def upload_file_content(session, upload_url, file):
    """Загрузка содержимого файла."""
    file_content = file.read()
    async with session.put(
        upload_url, headers=HEADERS, data=file_content
    ) as response:
        if response.status not in (HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
            raise YandexDiskError(UPLOAD_ERROR.format(response.status))


async def get_download_url(session, filename):
    """Получение ссылки для скачивания файла."""
    base_url = current_app.config["YANDEX_API_BASE"]
    api_version = current_app.config["API_VERSION"]
    download_url = f"{base_url}/{api_version}/disk/resources/download"

    async with session.get(
        download_url,
        headers=HEADERS,
        params={"path": f"/yacut/{filename}"},
    ) as response:
        if response.status != HTTPStatus.OK:
            raise YandexDiskError(DOWNLOAD_ERROR.format(response.status))
        return (await response.json())["href"]

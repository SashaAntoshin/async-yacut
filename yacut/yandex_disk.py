import asyncio
import os
from http import HTTPStatus

import aiohttp


DISK_TOKEN = os.getenv("DISK_TOKEN")

YANDEX_BASE = os.getenv("YANDEX_API_BASE", "https://cloud-api.yandex.net")
API_VERSION = os.getenv("API_VERSION", "v1")


UPLOAD_URL = f"{YANDEX_BASE}/{API_VERSION}/disk/resources/upload"
DOWNLOAD_URL = f"{YANDEX_BASE}/{API_VERSION}/disk/resources/download"
URL_ERROR = "Ошибка получения URL: {}"
UPLOAD_ERROR = "Ошибка загрузки: {}"
DOWNLOAD_ERROR = "Ошибка получения download URL: {}"

HEADERS = {"Authorization": f"OAuth {DISK_TOKEN}"}


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
    params = {"path": f"/yacut/{file.filename}", "overwrite": "true"}
    upload_url = await get_upload_url(session, params)
    await upload_file_content(session, upload_url, file)

    return file.filename, await get_download_url(
        session, file.filename
    )


async def get_upload_url(session, params):
    """Получение URL для загрузки файла."""
    async with session.get(
        UPLOAD_URL,
        headers=HEADERS,
        params=params,
    ) as response:
        if response.status != HTTPStatus.OK:
            raise RuntimeError(UPLOAD_ERROR.format(response.status))
        return (await response.json())["href"]


async def upload_file_content(session, upload_url, file):
    """Загрузка содержимого файла."""
    file_content = file.read()
    async with session.put(
        upload_url, headers=HEADERS, data=file_content
    ) as response:
        if response.status not in (HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
            raise RuntimeError(UPLOAD_ERROR.format(response.status))


async def get_download_url(session, filename):
    """Получение ссылки для скачивания файла."""
    url = DOWNLOAD_URL
    async with session.get(
        url,
        headers=HEADERS,
        params={"path": f"/yacut/{filename}"},
    ) as response:
        if response.status != HTTPStatus.OK:
            raise RuntimeError(DOWNLOAD_ERROR.format(response.status))
        return (await response.json())["href"]

import asyncio
import os
import aiohttp

from http import HTTPStatus


AUTH_HEADER = "OAuth {}"
UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
DOWNLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/download"
URL_ERROR = "Ошибка получения URL: {}"
UPLOAD_ERROR = "Ошибка загрузки: {}"
DOWNLOAD_ERROR = "Ошибка получения download URL: {}"

DISK_TOKEN = os.getenv("DISK_TOKEN")


def make_headers():
    if not DISK_TOKEN:
        raise EnvironmentError("DISK_TOKEN не найден")
    return {"Authorization": AUTH_HEADER.format(DISK_TOKEN)}


async def upload_files(files):
    """Асинхронная загрузка нескольких файлов."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_single_file(session, file) for file in files]
        return await asyncio.gather(*tasks, return_exceptions=True)


def upload_files_async(files):
    """Асинхронная загрузка файлов на Яндекс Диск."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(upload_files(files))
    loop.close()
    return results


async def upload_single_file(session, file):
    """Загрузка одного файла на Яндекс Диск."""
    headers = make_headers()
    params = {"path": f"/yacut/{file.filename}", "overwrite": "true"}

    upload_url = await get_upload_url(session, headers, params)
    await upload_file_content(session, upload_url, headers, file)

    return file.filename, await get_download_url(
        session, headers, file.filename
    )


async def get_upload_url(session, headers, params):
    """Получение URL для загрузки файла."""
    async with session.get(
        UPLOAD_URL,
        headers=headers,
        params=params,
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ConnectionError(URL_ERROR.format(response.status))
        return (await response.json())["href"]


async def upload_file_content(session, upload_url, headers, file):
    """Загрузка содержимого файла."""
    file_content = file.read()
    async with session.put(
        upload_url, headers=headers, data=file_content
    ) as response:
        if response.status not in (HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
            raise ConnectionError(UPLOAD_ERROR.format(response.status))


async def get_download_url(session, headers, filename):
    """Получение ссылки для скачивания файла."""
    url = DOWNLOAD_URL
    async with session.get(
        url,
        headers=headers,
        params={"path": f"/yacut/{filename}"},
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ConnectionError(DOWNLOAD_ERROR.format(response.status))
        return (await response.json())["href"]

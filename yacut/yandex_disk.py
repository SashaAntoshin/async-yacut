import asyncio
import os
import aiohttp

from http import HTTPStatus


DISK_TOKEN = os.getenv("DISK_TOKEN")

AUTH_HEADER = f"OAuth {os.getenv('DISK_TOKEN')}"
UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
DOWNLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/download"
URL_ERROR = "Ошибка получения URL: {}"
UPLOAD_ERROR = "Ошибка загрузки: {}"
DOWNLOAD_ERROR = "Ошибка получения download URL: {}"

HEADERS = {"Authorization": AUTH_HEADER}


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
            raise RuntimeError(URL_ERROR.format(response.status))
        return (await response.json())["href"]


async def upload_file_content(session, upload_url, file):
    """Загрузка содержимого файла."""
    file_content = file.read()
    async with session.put(
        upload_url, headers=HEADERS, data=file_content
    ) as response:
        if response.status not in (HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
            raise ValueError(UPLOAD_ERROR.format(response.status))


async def get_download_url(session, filename):
    """Получение ссылки для скачивания файла."""
    url = DOWNLOAD_URL
    async with session.get(
        url,
        headers=HEADERS,
        params={"path": f"/yacut/{filename}"},
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ValueError(DOWNLOAD_ERROR.format(response.status))
        return (await response.json())["href"]

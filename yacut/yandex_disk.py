import asyncio

import aiohttp


async def upload_files(files, token):
    """Асинхронная загрузка нескольких файлов."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_single_file(session, file, token) for file in files]
        return await asyncio.gather(*tasks, return_exceptions=True)


def upload_files_async(files, token):
    """Асинхронная загрузка файлов на Яндекс Диск."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(upload_files(files, token))
    loop.close()
    return results


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
            raise ConnectionError(f"Ошибка получения URL: {response.status}")
        upload_data = await response.json()
        return upload_data["href"]


async def upload_file_content(session, upload_url, headers, file):
    """Загрузка содержимого файла."""
    file_content = file.read()
    async with session.put(
        upload_url, headers=headers, data=file_content
    ) as response:
        if response.status not in (201, 202):
            raise ConnectionError(f"Ошибка загрузки: {response.status}")


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
            raise ConnectionError(msg)
        download_data = await response.json()
        return download_data["href"]

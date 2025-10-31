## Автор проекта:

- **Автор:** Антошин Александр
- **Контакты:** [Telegram @globe_s](https://t.me/globe_s)

## Техно - стек:

- **Backend**: Python 3.8+, Flask
- **База данных**: SQLite/PostgreSQL с SQLAlchemy ORM
- **Фронтенд**: HTML, Bootstrap, Jinja2
- **API**: RESTful JSON API
- **Асинхронность**: aiohttp для работы с внешними API
- **Загрузка файлов**: Интеграция с Яндекс.Диском
- **Валидация**: WTForms, регулярные выражения

### Как запустить проект Yacut:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/SashaAntoshin/async-yacut.git
```

```
cd yacut
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать в директории проекта файл .env с четыремя переменными окружения:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=your_secret_key
DB=sqlite:///db.sqlite3
```

Создать базу данных и применить миграции:

```
flask db upgrade
```

Запустить проект:

```
flask run
```

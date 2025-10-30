from http import HTTPStatus

from flask import jsonify, render_template, request

from . import db


class InvalidAPIUsage(Exception):
    """Класс обработки ошибок."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message

        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {"message": self.message}


def init_error_handlers(app):
    @app.errorhandler(InvalidAPIUsage)
    def handle_invalid_api_usage(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def page_not_found(error):
        """Страница не найдена."""
        if request.path.startswith("/api/"):
            return (
                jsonify({"message": "Указаный id не найден"}),
                HTTPStatus.NOT_FOUND,
            )
        return (
            render_template(
                "error.html",
                error_code=HTTPStatus.NOT_FOUND,
                error_message="Страница не найдена",
            ),
            HTTPStatus.NOT_FOUND,
        )

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def intrnal_error(error):
        """Ошибка сервера."""
        if request.path.startswith("/api/"):
            return jsonify({"message": "Ошибка сервера"})
        return (
            render_template(
                "error.html",
                error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_message="Внутренняя ошибка сервера",
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @app.errorhandler(HTTPStatus.BAD_REQUEST)
    def bad_request(error):
        """Не корректный запрос."""
        if request.path.startswith("/api/"):
            return jsonify({"message": "Отсутствует тело запроса"})
        return (
            render_template(
                "error.html",
                error_code=HTTPStatus.BAD_REQUEST,
                error_message="Некорректный запрос",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(Exception)
    def handle_database_error(error):
        """Обработка ошибок базы данных."""
        db.session.rollback()
        if request.path.startswith("/api/"):
            return (
                jsonify({"message": "Ошибка сервера"}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return (
            render_template(
                "error.html",
                error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_message="Внутренняя ошибка сервера",
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

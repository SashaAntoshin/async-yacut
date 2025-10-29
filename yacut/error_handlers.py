from flask import render_template, jsonify, request


class InvalidAPIUsage(Exception):
    """Класс обработки ошибок."""

    status_code = 400

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

    @app.errorhandler(404)
    def page_not_found(error):
        """Страница не найдена."""
        if request.path.startswith("/api/"):
            return jsonify({"message": "Указаный id не найден"}), 404
        return (
            render_template(
                "error.html",
                error_code=404,
                error_message="Страница не найдена",
            ),
            404,
        )

    @app.errorhandler(500)
    def intrnal_error(error):
        """Ошибка сервера."""
        if request.path.startswith("/api/"):
            return jsonify({"message": "Ошибка сервера"})
        return (
            render_template(
                "error.html",
                error_code=500,
                error_message="Внутренняя ошибка сервера",
            ),
            500,
        )

    @app.errorhandler(400)
    def bad_request(error):
        """Не корректный запрос."""
        if request.path.startswith("/api/"):
            return jsonify({"message": "Отсутствует тело запроса"})
        return (
            render_template(
                "error.html",
                error_code=400,
                error_message="Некорректный запрос",
            ),
            400,
        )

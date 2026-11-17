from flask import jsonify


class LibraryError(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status


def error(message, status):
    return LibraryError(message, status)


def bad_request(message):
    return error(message, 400)


def not_found(message):
    return error(message, 404)


def conflict(message):
    return error(message, 409)


def error_response(message, status):
    return jsonify({"error": message}), status


def handle_library_error(e):
    return error_response(e.message, e.status)

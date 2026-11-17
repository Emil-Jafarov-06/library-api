import os

from flask import Flask

from routes import book_routes, member_routes, loan_routes, report_routes
from routes.swagger import swagger_bp
from core.db import init_db
from core.errors import LibraryError, handle_library_error

app = Flask(__name__)

for blueprint in (swagger_bp, book_routes.bp, member_routes.bp, loan_routes.bp, report_routes.bp):
    app.register_blueprint(blueprint)

app.register_error_handler(LibraryError, handle_library_error)


if not os.path.exists("library.db"):
    init_db()

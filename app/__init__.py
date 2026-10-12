"""Flask Application Factory module for Student Record & Academic Management Platform."""
from flask import Flask, render_template


def create_app():
    """Application factory for configuring and instantiating the Flask application."""
    app = Flask(__name__)

    # Register API blueprint under /api prefix
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Interactive Dashboard Route
    @app.route("/", methods=["GET"])
    def index():
        """Render the primary interactive web dashboard."""
        return render_template("index.html")

    return app

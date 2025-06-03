from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    # Optional: Load config into Flask app config if needed
    # app.config.from_object(Config)

    # Import and register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    print(f"Flask app created. Debug: {Config.DEBUG}, Port: {Config.PORT}")
    return app
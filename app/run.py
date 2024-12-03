from app import create_app
from app.config import Config

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

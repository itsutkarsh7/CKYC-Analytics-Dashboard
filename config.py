import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = "CKYC_SECRET_KEY"

    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "ckyc_local.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    EXPORT_FOLDER = os.path.join(
        BASE_DIR,
        "exports"
    )

    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

from sqlmodel import SQLModel

# Import all models here so Alembic can discover them via target_metadata
from app.db import models as _models  # noqa: F401

metadata = SQLModel.metadata

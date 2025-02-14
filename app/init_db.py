from app import engine, Base
from app.models.user import User

Base.metadata.create_all(bind=engine)
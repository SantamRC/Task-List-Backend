import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL").replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

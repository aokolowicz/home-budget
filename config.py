import os

class Config:
    # https://blog.pythonanywhere.com/121/
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}'.format(
        username=os.environ.get("DB_USERNAME", None),
        password=os.environ.get("DB_PASSWORD", None),
        hostname=os.environ.get("DB_HOSTNAME", None),
        databasename=os.environ.get("DB_NAME", None),
    )
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False

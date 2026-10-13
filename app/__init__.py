import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

es_host = os.environ.get('ES_HOST', 'http://localhost:9200')
es = Elasticsearch(es_host)

with app.app_context():
    db.create_all()

from app import routes, models  # noqa: E402,F401
from app import cli  # noqa: E402,F401 — регистрирует flask load-data
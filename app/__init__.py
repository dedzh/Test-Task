import os
import asyncio

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from elasticsearch import Elasticsearch

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

es_host = os.environ.get('ES_HOST', 'http://localhost:9200')
es = Elasticsearch(es_host)

from app import routes, models, cli
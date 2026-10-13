import asyncio
from flask import jsonify, request

from app import app
from app.models import Docs
from app.tasks import delete, search


def _run(coro):
    return asyncio.run(coro)


@app.get('/search/')
def get_posts():
    text = request.args.get('text')
    return jsonify(_run(search(Docs, text)))


@app.delete('/delete/')
def delete_post():
    post_id = request.args.get('id')
    return _run(delete(Docs, post_id))
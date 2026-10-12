from flask import jsonify, request

from app import app, loop
from app.models import Docs
from app.tasks import delete, search


@app.get('/search/')
def get_posts():
    text = request.args.get('text')
    result = loop.run_until_complete(search(Docs, text))
    return jsonify(result)


@app.delete('/delete/')
def delete_post():
    post_id = request.args.get('id')
    result = loop.run_until_complete(delete(Docs, post_id))
    return result


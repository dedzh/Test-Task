from app import db, es
from app.elastic import add_to_index, delete_by_id, query_index_by_id, query_index_by_text


async def search(Model, text):
    if not es.indices.exists(index='docs'):
        for post in Model.query.all():
            add_to_index('docs', post)

    if text is None or not str(text).strip():
        return []

    try:
        ids = query_index_by_text('docs', text)
        if not ids:
            return []
        result = Model.query.filter(Model.id.in_(ids)).order_by(Model.created_date.desc()).all()
        return [post.as_dict() for post in result]
    except Exception as exc:
        return str(exc)


async def delete(Model, id):
    if not es.indices.exists(index='docs'):
        for post in Model.query.all():
            add_to_index('docs', post)

    try:
        post_id = int(id)
    except (TypeError, ValueError):
        return "Not found post with such id"

    db_item = Model.query.filter_by(id=post_id).first()
    elastic_item = query_index_by_id('docs', post_id)

    if db_item is not None:
        db.session.delete(db_item)
        db.session.commit()
        db_deleted = True
    else:
        db_deleted = False

    if elastic_item is not None:
        elastic_deleted = delete_by_id('docs', post_id)
    else:
        elastic_deleted = False

    if db_deleted or elastic_deleted:
        return str(True)
    return "Not found post with such id"
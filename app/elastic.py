import elasticsearch

from app import es


def delete_by_id(index, id):
    try:
        es.delete(index=index, id=str(id))
        return True
    except elasticsearch.NotFoundError:
        return False


def query_index_by_text(index, text):
    if text is None or not str(text).strip():
        return []
    search = es.search(
        index=index,
        size=20,
        query={'multi_match': {'query': text, 'fields': ['text', 'id']}})
    hits = search.get('hits', {}).get('hits', [])
    return [int(hit['_id']) for hit in hits]


def query_index_by_id(index, id):
    try:
        return es.get(index=index, id=str(id))
    except elasticsearch.NotFoundError:
        return None


def add_to_index(index, model):
    payload = {'id': model.id}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    es.index(index=index, id=str(model.id), document=payload)

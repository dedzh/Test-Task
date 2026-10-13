# Test Task — поисковик по документам

Простой поисковый сервис: принимает текстовый запрос, ищет по тексту документов в Elasticsearch, возвращает первые 20 совпадений с полными данными из БД, отсортированные по дате создания. Умеет удалять документы из БД и индекса.

## Стек

- **Python 3.10**, **Flask 3.0**
- **SQLite** + **SQLAlchemy 2.0** (хранение документов)
- **Elasticsearch 8.2** (поисковый индекс)
- **Docker** + **docker-compose**

## Запуск

Требуется **Docker Desktop**.

```bash
docker compose up --build -d
```

Первый запуск занимает ~1 минуту: Elasticsearch стартует, затем приложение загружает `posts.csv` в SQLite и индексирует его в ES.

**Проверить статус:**

```bash
docker compose ps
```
Оба контейнера должны быть *Up*, у `intern-elastic` — статус *(healthy)*.

**Остановить:**

```bash
docker compose down
```
Данные Elasticsearch сохраняются в volume `es_data` между перезапусками.

## API

Сервис поднимается на `http://localhost:5000`.

### Поиск

`GET /search/?text=<запрос>`

Возвращает JSON-массив (до 20 документов), отсортированный по `created_date` по убыванию:

```json
[
  {
    "id": 547,
    "text": "...",
    "created_date": "2019-07-25 12:42:13",
    "rubrics": ["VK-1603736028819866", "VK-11879320040"]
  }
]
```

**Пример:**

```bash
curl "http://localhost:5000/search/?text=святой"
```

### Удаление

`DELETE /delete/?id=<id>`

Возвращает `True` при успехе или `Not found post with such id`, если документа нет.

**Пример:**

```bash
curl -X DELETE "http://localhost:5000/delete/?id=5"
```

## Документация

OpenAPI-спецификация лежит в `docs.json`. Открыть в Swagger Editor:  
[https://editor.swagger.io](https://editor.swagger.io)

## Тесты

Функциональные тесты в `app/tests.py`. Требуется запущенный Elasticsearch (поднимается через `docker compose up`) и переменная окружения `ES_HOST`.

```bash
# Windows cmd
set ES_HOST=http://localhost:9200
python -m pytest app/tests.py -v

# Linux/macOS
export ES_HOST=http://localhost:9200
pytest app/tests.py -v
```

## Структура проекта

```text
.
├── app/
│   ├── __init__.py     # инициализация Flask, SQLAlchemy, ES
│   ├── models.py       # модель Docs
│   ├── elastic.py      # функции работы с ES
│   ├── routes.py       # HTTP-эндпоинты
│   ├── tasks.py        # логика поиска и удаления
│   ├── cli.py          # flask load-data
│   └── tests.py        # тесты
├── boot.sh             # ожидание ES, загрузка данных, запуск gunicorn
├── server.py           # точка входа
├── config.py           # конфигурация
├── docker-compose.yml
├── Dockerfile
├── docs.json           # OpenAPI
└── posts.csv           # исходные данные
```

## Как работает загрузка данных

При старте контейнера `boot.sh`:
1. Ждёт готовности Elasticsearch.
2. Вызывает `flask load-data` — читает `posts.csv`, создаёт таблицу `docs` в SQLite, индексирует документы в ES.
3. Запускает `gunicorn`.

*Команда идемпотентна: если данные уже загружены, повторный запуск ничего не дублирует.*

import csv
import os

import click

from app import app, db, es
from app.models import Docs
from app.elastic import add_to_index, ensure_index


@app.cli.command("load-data")
@click.option("--csv-path", default="posts.csv", help="Path to CSV file")
def load_data(csv_path):
    """Загружает posts.csv в SQLite и индексирует в Elasticsearch."""
    if not os.path.exists(csv_path):
        click.echo(f"CSV not found: {csv_path}")
        return

    # ВАЖНО: создаём таблицы, если их нет
    db.create_all()

    if Docs.query.count() > 0:
        click.echo(f"DB already has {Docs.query.count()} docs, skipping load")
    else:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                doc = Docs(
                    id=count,
                    text=row["text"],
                    raw_created_date=row["created_date"],
                    rubrics=row["rubrics"],
                )
                db.session.add(doc)
                count += 1
            db.session.commit()
            click.echo(f"Loaded {count} docs into DB")

    ensure_index("docs")

    already_indexed = es.count(index="docs")["count"]
    if already_indexed > 0:
        click.echo(f"ES already has {already_indexed} docs, skipping index")
        return

    for doc in Docs.query.all():
        add_to_index("docs", doc)
    es.indices.refresh(index="docs")
    click.echo(f"Indexed {Docs.query.count()} docs into ES")
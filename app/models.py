import ast
from datetime import datetime

from app import db

DATETIME_PATTERN = r"%Y-%m-%d %H:%M:%S"


class Docs(db.Model):
    __searchable__ = ['text']
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text())
    created_date = db.Column(db.DateTime)
    rubrics = db.Column(db.String())

    def __init__(self, id: int, text: str, raw_created_date: str, rubrics: str):
        self.id = id
        self.text = text
        self.created_date = self._parse_datetime(raw_created_date)
        self.rubrics = rubrics

    @staticmethod
    def _parse_datetime(raw_created_date):
        if isinstance(raw_created_date, datetime):
            return raw_created_date
        return datetime.strptime(raw_created_date, DATETIME_PATTERN)

    @staticmethod
    def _parse_rubrics(value):
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, tuple):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parsed = value
            if isinstance(parsed, (list, tuple, set)):
                return [str(item).strip() for item in parsed if str(item).strip()]
            if isinstance(parsed, str):
                return [parsed.strip()] if parsed.strip() else []
            return [str(parsed).strip()] if str(parsed).strip() else []
        return [str(value).strip()] if str(value).strip() else []

    def as_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "created_date": self.created_date.strftime(DATETIME_PATTERN),
            "rubrics": self._parse_rubrics(self.rubrics),
        }


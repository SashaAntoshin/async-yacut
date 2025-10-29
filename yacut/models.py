from datetime import datetime
from yacut import db


class URLMap(db.Model):
    """Основная модель."""
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_file = db.Column(db.Boolean, default=False)

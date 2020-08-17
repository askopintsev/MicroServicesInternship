from . import db


class Mail(db.Model):
    __tablename__ = "mails"

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(), nullable=False)

from app import db


class UploadHistory(db.Model):

    __tablename__ = "upload_history"

    id = db.Column(db.Integer, primary_key=True)

    report_name = db.Column(db.String(100))

    uploaded_on = db.Column(db.DateTime)

    total_rows = db.Column(db.Integer)

    status = db.Column(db.String(30))
from app import db
from datetime import datetime

class EDCData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time_period = db.Column(db.String(20), nullable=False)
    positive_flexibility = db.Column(db.Float)
    negative_flexibility = db.Column(db.Float)
    shared_electricity = db.Column(db.Float)
    
    def __repr__(self):
        return f'<EDCData {self.date} {self.time_period}>' 
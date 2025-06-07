from app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class EDCData(db.Model):
    __tablename__ = 'okte_data'
    
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.String, nullable=False)  # TEXT in database
    zuctovacia_perioda = db.Column(db.String, nullable=False)  # TEXT in database
    aktivovana_agregovana_flexibilita_kladna = db.Column(db.Float)  # REAL in database
    aktivovana_agregovana_flexibilita_zaporna = db.Column(db.Float)  # REAL in database
    zdielana_elektrina = db.Column(db.Float)  # REAL in database
    
    @hybrid_property
    def date(self):
        return datetime.strptime(self.datum, '%Y-%m-%d').date()
    
    def __repr__(self):
        return f'<EDCData {self.datum} {self.zuctovacia_perioda}>' 
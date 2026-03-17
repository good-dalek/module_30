from .app import db
from sqlalchemy import ForeignKey


class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))

    def __repr__(self):
        return f'Клиент {self.name} {self.surname}'

    def to_json(self):
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns}


class Parking(db.Model):
    __tablename__ = 'parking'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=False)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.CheckConstraint('opened IN (0, 1)', name='check_opened_boolean'),
    )


class ClientParking(db.Model):
    __tablename__ = 'client_parking'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('client.id'))
    parking_id = db.Column(db.Integer, ForeignKey('parking.id'))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)

    client = db.relationship('Client', backref='parkings')
    parking = db.relationship('Parking', backref='clients')

    __table_args__ = (
        db.UniqueConstraint('client_id', 'parking_id',
                            name='unique_client_parking'),
    )

    def to_json(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'parking_id': self.parking_id,
            'time_in': self.time_in.strftime('%Y-%m-%d %H:%M:%S'),
            'time_out': self.time_out.strftime('%Y-%m-%d %H:%M:%S') if self.time_out else None,
            'parking_address': self.parking.address if self.parking else None
        }

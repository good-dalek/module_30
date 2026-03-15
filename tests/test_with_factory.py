from .factories import ClientFactory, ParkingFactory
from ..main.models import Client, Parking


def test_create_client(app, db):
	client_factory = ClientFactory()
	db.session.commit()

	assert client_factory.id is not None
	assert len(db.session.query(Client).all()) == 2


def test_create_parking(app, db):
	parking_factory = ParkingFactory()
	db.session.commit()
	assert parking_factory.id is not None
	assert len(db.session.query(Parking).all()) == 2


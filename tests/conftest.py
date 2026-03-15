import pytest
from flask import template_rendered

from ..main.app import create_app, db as _db
from ..main.models import Client, Parking, ClientParking


@pytest.fixture
def app():
	_app = create_app()
	_app.config['TESTING'] = True
	_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

	with _app.app_context():
		_db.create_all()
		db_client = Client(id=1,
		                   name='Name',
		                   surname='Surname',
		                   credit_card='1234qwe')
		db_parking = Parking(id=1,
		                     address='address',
		                     opened=True,
		                     count_places=20,
		                     count_available_places=15)

		_db.session.add(db_client)
		_db.session.add(db_parking)
		_db.session.commit()

		yield _app
		_db.session.close()
		_db.drop_all()


@pytest.fixture
def client(app):
	client = app.test_client()
	yield client


@pytest.fixture
def db(app):
	with app.app_context():
		yield _db

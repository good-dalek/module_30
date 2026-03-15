import factory
import factory.fuzzy as fuzzy

from ..main.app import db
from ..main.models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
	class Meta:
		model = Client
		sqlalchemy_session = db.session

	name = factory.Faker('first_name')
	surname = factory.Faker('last_name')
	credit_card = factory.Faker('credit_card_number')
	car_number = fuzzy.FuzzyText(length=6, chars='123тру')


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
	class Meta:
		model = Parking
		sqlalchemy_session = db.session

	address = factory.Faker('address')
	opened = factory.Faker('pybool')
	count_places = fuzzy.FuzzyInteger(10, 50)
	count_available_places = factory.LazyAttribute(
		lambda x: fuzzy.FuzzyInteger(0, x.count_places).fuzz())

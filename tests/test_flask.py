import datetime

import pytest
from main.models import Parking, ClientParking, Client


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200


# тест создания клиента
def test_create_client(client):
    client_data = {'name': 'Алексей',
                   'surname': 'Дементьев',
                   'credit_card': '88005553555',
                   'car_number': 'В666АД'}

    resp = client.post('/clients', json=client_data)

    assert resp.status_code == 201


# тест создания парковки
def test_create_parking(client):
    parking_data = {'address': 'ул, Ленина 1',
                    'opened': True,
                    'count_places': 30,
                    'count_available_places': 20}

    resp = client.post('/parkings', json=parking_data)
    assert resp.status_code == 201


# тест заезда на парковку
@pytest.mark.parking
def test_entering_parking(client, db):
    free_places_before = db.session.query(Parking.count_available_places).scalar()  # кол-во мест до парковки
    data = {'client_id': '1',
            'parking_id': '1',
            'time_in': datetime.datetime.now()}

    resp = client.post('/client_parkings', json=data)
    opened_parking = (db.session.query(Parking.opened)
                      .filter(Parking.id == data['parking_id']).scalar())  # открытая парковка
    places_after_reduction = db.session.query(Parking.count_available_places).scalar()  # кол-во мет после парковки

    assert places_after_reduction < free_places_before
    assert opened_parking is True
    assert resp.status_code == 201


# тест выезда с парковки
@pytest.mark.parking
def test_leaving_the_parking(client, db):
    data = {'client_id': '1',
            'parking_id': '1',
            'time_in': datetime.datetime.now()}
    post_method = client.post('/client_parkings', json=data)
    places_after_reduction = db.session.query(Parking.count_available_places).scalar()  # кол-во мет после парковки
    time_in = (db.session.query(ClientParking.time_in)
               .filter_by(parking_id=data['parking_id']).scalar())  # время заезда

    del_method = client.delete('/client_parkings', json=data)
    free_places_before = db.session.query(Parking.count_available_places).scalar()  # кол-во мест до парковки
    time_out = (db.session.query(ClientParking.time_out)
                .filter_by(parking_id=data['parking_id']).scalar())  # время выезда с парковки
    card = db.session.query(Client.credit_card).scalar()

    assert del_method.status_code == 200
    assert places_after_reduction < free_places_before
    assert time_out > time_in
    assert card is not None

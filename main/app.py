import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app_parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .models import Client, ClientParking, Parking

    with app.app_context():
        db.create_all()

    @app.route("/clients", methods=["GET"])
    def all_clients():
        clients = db.session.query(Client).all()
        clients_list = [c.to_json() for c in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_id(client_id):
        client = db.session.query(Client).get(client_id)
        if client is None:
            return jsonify({"error": "There is no client with this ID."})
        return jsonify(client.to_json()), 200

    @app.route("/clients", methods=["POST"])
    def create_new_client():
        data = request.get_json()

        new_client = Client(name=data.get("name"), surname=data.get("surname"))
        db.session.add(new_client)
        db.session.commit()

        return "Клиент добавлен", 201

    @app.route("/parkings", methods=["POST"])
    def create_parking_zone():
        data = request.get_json()
        new_parking_zone = Parking(
            address=data.get("address"),
            opened=data.get("opened"),
            count_places=data.get("count_places"),
            count_available_places=data.get("count_available_places"),
        )
        print(data.get("opened"))
        db.session.add(new_parking_zone)
        db.session.commit()
        return "Парковочная зона добавлена", 201

    @app.route("/client_parkings", methods=["POST"])
    def parking_entrance():
        data = request.get_json()
        parking_id = data.get("parking_id")
        opened_parking = (
            db.session.query(Parking.opened).where(Parking.id == parking_id)
        ).scalar()
        parking = db.session.query(Parking).get(parking_id)

        if opened_parking is False:
            return jsonify({"error": "Парковка закрыта"})

        if parking.count_available_places <= 0:
            return jsonify({"error": "Свободных мест нет"})

        parking_record = ClientParking(
            client_id=data.get("client_id"),
            parking_id=data.get("parking_id"),
            time_in=datetime.datetime.now(),
        )
        print(type(parking_record))
        parking.count_available_places -= 1

        db.session.add(parking_record)
        db.session.commit()

        return (
            f"Дата и время заезда на парковку: "
            f"{parking_record.to_json()['time_in']}\n "
            f"Парковка №: {parking_record.parking_id}"
        ), 201

    @app.route("/client_parkings", methods=["DELETE"])
    def leaving_the_parking():
        data = request.get_json()
        parking_id = data.get("parking_id")
        client_id = data.get("client_id")
        client_parking_id = (
            db.session.query(ClientParking.id).filter(
                ClientParking.client_id == client_id,
                ClientParking.parking_id == parking_id,
            )
        ).scalar()

        parking = db.session.query(Parking).get(parking_id)
        credit_card = (
            db.session.query(Client.credit_card)
            .filter(Client.id == data.get("client_id"))
            .scalar()
        )

        if not credit_card:
            return jsonify({"error": "Для оплаты парковки привяжите карту"}), 400

        (
            db.session.query(ClientParking)
            .filter(ClientParking.id == client_parking_id)
            .update({ClientParking.time_out: datetime.datetime.now()})
        )

        parking.count_available_places += 1

        db.session.commit()

        time_out = (
            db.session.query(ClientParking)
            .filter(ClientParking.id == client_parking_id)
            .scalar()
        )
        return (
            f"Дата и время выезда с парковки: "
            f"{time_out.to_json()['time_out']}", 200,
        )

    return app

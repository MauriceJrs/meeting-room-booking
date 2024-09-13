from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/meeting_rooms_db'
db = SQLAlchemy(app)

class Room(db.Model):
    """
    Модель, представляющая конференц-зал.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Slot(db.Model):
    """
    Модель, представляющая временной интервал для конференц-зала.
    """
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

class Booking(db.Model):
    """
    Модель, представляющая бронь временного интервала конференц-зала.
    """
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    emails = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)

@app.route('/rooms/available', methods=['GET'])
def get_available_rooms():
    """
    Получить список доступных залов в заданном временном интервале.
    """
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if not start_time or not end_time:
        return jsonify({'error': 'Укажите start_time и end_time'}), 400

    try:
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({'error': 'Неверный формат даты. Используйте формат ISO.'}), 400

    # Найти интервал времени, который пересекается с заданным временным интервалом
    overlapping_slots = Slot.query.filter(
        and_(
            Slot.start_time < end_time,
            Slot.end_time > start_time
        )
    ).all()

    # Получить ID залов, которые имеют пересекающиеся интервалы
    room_ids_with_overlaps = {slot.room_id for slot in overlapping_slots}

    # Найти все залы, которые не имеют пересекающихся интервалов
    available_rooms = Room.query.filter(
        Room.id.notin_(room_ids_with_overlaps)
    ).all()

    return jsonify([
        {'id': room.id, 'name': room.name, 'capacity': room.capacity}
        for room in available_rooms
    ])

if __name__ == '__main__':
    app.run(debug=True)

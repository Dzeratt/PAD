from flask import Flask, request, jsonify
import psycopg2


cm = Flask(__name__)

def dbConnect():
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="tgbot",
        user="tgbotadmin",
        password="321")

    return conn

def dbClose(cursor, connection):
    cursor.close()
    connection.close()

@cm.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    name = data.get('name')
    rate = data.get('rate')

    if not name or not rate:
        return jsonify({'error': 'Название и курс должны быть заполнены.'}), 400

    try:
        amount = float(rate)
    except ValueError:
        return jsonify({'error': 'Курс должен быть числом.'}), 400

    if amount <= 0:
        return jsonify({'error': 'Курс должен быть положительным числом.'}), 400

    name = name.upper().strip()

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT currency_name FROM currencies WHERE currency_name = %s", (name,))
    if cur.fetchone():
        dbClose(cur, conn)
        return jsonify({'error': 'Данная валюта уже существует.'}), 400

    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (name, rate))
    conn.commit()

    dbClose(cur, conn)

    return jsonify({'message': f'Валюта: {name} успешно добавлена.'}), 200

@cm.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    name = data.get('name')
    new_rate = data.get('rate')

    if not name or not new_rate:
        return jsonify({'error': 'Название и курс должны быть заполнены.'}), 400

    try:
        amount = float(new_rate)
    except ValueError:
        return jsonify({'error': 'Курс должен быть числом.'}), 400

    if amount <= 0:
        return jsonify({'error': 'Курс должен быть положительным числом.'}), 400

    name = name.upper().strip()

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT currency_name FROM currencies WHERE currency_name = %s", (name,))
    if not cur.fetchone():
        dbClose(cur, conn)
        return jsonify({'error': 'Валюта не найдена.'}), 404

    cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (new_rate, name))
    conn.commit()

    dbClose(cur, conn)

    return jsonify({'message': 'Валюта успешно обновлена.'}), 200

@cm.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Название должно быть заполнено.'}), 400

    name = name.upper().strip()

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT currency_name FROM currencies WHERE currency_name = %s", (name,))
    if not cur.fetchone():
        dbClose(cur, conn)
        return jsonify({'error': 'Валюта не найдена.'}), 404

    cur.execute("DELETE FROM currencies WHERE currency_name = %s", (name,))
    conn.commit()

    dbClose(cur, conn)

    return jsonify({'message': 'Валюта успешно удалена.'}), 200

if __name__ == '__main__':
    cm.run(port=5001, debug=True)

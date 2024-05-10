from flask import Flask, request, jsonify
import psycopg2


dm = Flask(__name__)

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

@dm.route('/convert', methods=['GET'])
def convert_currency():
    currency_name = request.args.get('currency_name')
    amount = request.args.get('amount')

    if not currency_name or not amount:
        return jsonify({'error': 'Название и курс должны быть заполнены.'}), 400
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Курс должен быть числом.'}), 400

    if amount <= 0:
        return jsonify({'error': 'Курс должен быть положительным числом.'}), 400

    currency_name = currency_name.upper().strip()

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
    row = cur.fetchone()
    if not row:
        dbClose(cur, conn)
        return jsonify({'error': 'Валюта не найдена.'}), 404

    rate = row[0]
    converted_amount = float(amount) * float(rate)

    dbClose(cur, conn)

    return jsonify({'converted_amount': converted_amount}), 200

@dm.route('/currencies', methods=['GET'])
def get_currencies():
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT currency_name, rate FROM currencies")
    rows = cur.fetchall()

    currency_list = [{'currency_name': row[0], 'rate': row[1]} for row in rows]

    dbClose(cur, conn)

    return jsonify({'currencies': currency_list}), 200

if __name__ == '__main__':
    dm.run(port=5002, debug=True)

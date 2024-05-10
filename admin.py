from flask import Flask, request, jsonify
import psycopg2


ad = Flask(__name__)

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

@ad.route('/check_admin', methods=['POST'])
def check_admin():
    data = request.json
    id = data.get('id')

    if not id:
        return jsonify({'error': 'Id are required'}), 400

    #try:
    #    id = str(id)
    #except ValueError:
    #    return jsonify({'error': 'Amount must be a valid string'}), 400

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM admins WHERE chat_id = '%s'", (id,))
    if cur.fetchone():
        return jsonify({'message': f'ID: {id} является администратором'}), 200
    else:
        return jsonify({'error': f'ID: {id} не является администратором'}), 400





if __name__ == '__main__':
    ad.run(port=5003, debug=True)

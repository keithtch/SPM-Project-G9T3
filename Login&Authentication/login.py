from flask import Flask
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)
def get_db_connection():
    return pymysql.connect(
        host='spm-project-db.cn2miou8y197.us-east-1.rds.amazonaws.com',
        user='admin',
        password='awspassword',
        database='projectdb'
    )

@app.route('/data')
def get_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Employee")
            result = cursor.fetchall()
            return {'data': result}
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)

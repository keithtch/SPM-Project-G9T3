from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
import os

app = Flask(__name__)
CORS(app)

load_dotenv('../.env')

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('RDS_HOST'),
        user=os.environ.get('RDS_USER'),
        password=os.environ.get('RDS_PASSWORD'),
        database= os.environ.get('RDS_DATABASE')
    )

@app.route('/application')
def apply():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Application")
            result = cursor.fetchall()
            return {'data': result}
    finally:
        connection.close()
        
@app.route('/updateDates',methods=['POST'])
def updateDates():
    data = request.get_json()
    dates = data.get('dates')
    print(dates)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for entry in dates:
                cursor.execute("""INSERT INTO Application (Staff_ID, Date_Applied, Reporting_Manager, Status_Of_Application)
    VALUES (%s,%s,%s,%s)""",(entry[0],entry[1],entry[2],entry[3]))
            connection.commit()
            if dates:
                print(dates)
                return jsonify({"status": "success", "received_dates": dates}), 200
            else:
                return jsonify({"status": "error", "message": "No dates received"}), 400
    finally:
        connection.close()
    

    

if __name__ == '__main__':
    app.run(debug=True, port=5001)

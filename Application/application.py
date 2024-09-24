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
                cursor.execute("""INSERT INTO Application (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason)
    VALUES (%s,%s,%s,%s,%s,%s)""",(entry[0],entry[1],entry[2],entry[3],entry[4],entry[5]))
            connection.commit()
            if dates:
                print(dates)
                return jsonify({"status": "success", "received_dates": dates}), 200
            else:
                return jsonify({"status": "error", "message": "No dates received"}), 400
    finally:
        connection.close()
    
@app.route('/getApps',methods=['POST'])
def getApps():
    data = request.get_json()
    ids = data.get('ids')
    print(ids)
    idQuery = ', '.join(['%s'] * len(ids))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM Application WHERE Staff_ID IN ({idQuery})",ids)
            results = cursor.fetchall()
            if results:
                print(results)
                return jsonify({"status": "success", "results": results}), 200
            else:
                return jsonify({"status": "error", "message": "No apps received"}), 400
    finally:
        connection.close()
    

if __name__ == '__main__':
    app.run(debug=True, port=5001)

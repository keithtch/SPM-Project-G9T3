from flask import Flask, request, jsonify
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
        
@app.route('/getDates',methods=['POST'])
def getDates():
    data = request.get_json()
    dates = data.get('dates')
    
    if dates:
        print(dates)
        return jsonify({"status": "success", "received_dates": dates}), 200
    else:
        return jsonify({"status": "error", "message": "No dates received"}), 400
    

if __name__ == '__main__':
    app.run(debug=True, port=5001)

from flask import request, Flask
from dotenv import load_dotenv
from flask_cors import CORS
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

@app.route('/employee')
def get_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Employee")
            result = cursor.fetchall()
            return {'data': result}
    finally:
        connection.close()

@app.route('/getEmployee/<int:id>', methods=['POST'])
def get_employeeData(id):
    id = str(id)
    print(id)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Employee WHERE Staff_ID=%s",(id))
            result = cursor.fetchall()
            return {'employee':result}
    finally:
        connection.close()

@app.route('/findTeam/<int:id>', methods=['POST'])
def findTeam(id):
    id = str(id)
    print(id)
    queue = []
    staff = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Role FROM Employee WHERE Staff_ID = %s", (id))
            role = cursor.fetchone()[0]
            if role == 2:
                cursor.execute("SELECT * FROM Employee WHERE Reporting_Manager = (SELECT Reporting_Manager FROM Employee WHERE Staff_ID = %s)",(id))
            # elif role == 3:
            #     cursor.execute("SELECT * FROM Employee WHERE Reporting_Manager = %s", (id))
            else:
                cursor.execute("SELECT * FROM Employee")
                allStaff = cursor.fetchall()
                queue.append(id)
                while len(queue)>0:
                    tempID = queue.pop()
                    # print(queue)
                    for employee in allStaff:
                        # print(employee[0],employee[7])
                        if (str(employee[7]) == str(tempID) and (employee not in staff) and employee[0] != 130002):
                            queue.append(employee[0])
                            staff.append(employee)
                print(staff)

            return {'employees':staff}
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)

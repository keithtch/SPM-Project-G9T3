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

@app.route('/getFirstName', methods=['POST'])
def get_firstname():
    data = request.get_json()
    ids = data.get('ids')
    idQuery = ', '.join(['%s'] * len(ids))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM Employee WHERE Staff_ID IN ({idQuery})",ids)
            result = cursor.fetchall()
            resultDict = {}
            for employee in result:
                resultDict[employee[0]] = employee[1]
            return {'names':resultDict}
    finally:
        connection.close()

@app.route('/findTeam/<int:id>', methods=['POST'])
def findTeam(id):
    id = str(id)
    print(id)
    queue = []
    staff = {}
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Role FROM Employee WHERE Staff_ID = %s", (id))
            role = cursor.fetchone()[0]
            cursor.execute("SELECT Staff_ID,Staff_FName FROM Employee")
            nameResult = cursor.fetchall()
            teamNames = {key:value for key,value in nameResult}
            print(teamNames)
            if role == 2:
                cursor.execute("SELECT * FROM Employee WHERE Reporting_Manager = (SELECT Reporting_Manager FROM Employee WHERE Staff_ID = %s)",(id))
                staffResult = cursor.fetchall()
                staff = {teamNames[staffResult[0][7]]: [list(row) for row in staffResult]}
                print(staff)
            # elif role == 3:
            #     cursor.execute("SELECT * FROM Employee WHERE Reporting_Manager = %s", (id))
            elif role == 1 or role == 3:
                cursor.execute("SELECT * FROM Employee")
                allStaff = cursor.fetchall()
                allStaff = [list(row) for row in allStaff]
                queue.append(id)
                while len(queue)>0:
                    tempID = int(queue.pop())
                    for employee in allStaff:
                        if (int(employee[7]) == tempID and (employee not in staff.values()) and (employee[0] != employee[7])):
                            if teamNames[tempID] not in staff:
                                staff[teamNames[tempID]] = []
                            if employee[8] == 1 or employee[8] == 3:
                                queue.append(employee[0])
                            staff[teamNames[tempID]].append(employee)

            return {'employees':staff}
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)

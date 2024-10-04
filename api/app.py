from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
import os

app = Flask(__name__)
CORS(app)

# load_dotenv('../.env')

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
    date = data.get('date')
    status = data.get('status')
    print(ids,date)
    idQuery = ', '.join(['%s'] * len(ids))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM Application WHERE Staff_ID IN ({idQuery}) AND Date_Applied = %s AND Status_Of_Application = %s",(*ids,date,status))
            results = cursor.fetchall()
            print(results)
            if results:
                print(results)
                return jsonify({"status": "success", "results": results}), 200
            elif results == ():
                return jsonify({"status": "success", "message": "No apps received"}), 200
            else:
                return jsonify({"status": "error", "message": "SQL failure"}), 400

    finally:
        connection.close()
        
@app.route('/getPendingApplications', methods=['POST'])
def getPendingApplications():
    data = request.get_json()
    reporting_manager_id = data.get('staffID')  # staffID from the front-end

    connection = get_db_connection() 
    try:
        with connection.cursor() as cursor:
            # SQL Query: Join Employee and Application tables to get subordinates' pending applications
            query = """
                SELECT a.Staff_ID, a.Date_Applied, a.Time_Of_Day, a.Status_Of_Application, a.Reason
                FROM Employee e
                JOIN Application a ON e.Staff_ID = a.Staff_ID
                WHERE e.Reporting_Manager = %s  -- Using reporting_manager_id
                AND a.Status_Of_Application = 'Pending'
            """
            cursor.execute(query, (reporting_manager_id,))  # Pass the reporting manager's ID
            results = cursor.fetchall()

            if results:
                return jsonify({"status": "success", "pendingApplications": results}), 200
            elif len(results) == 0:
                return jsonify({"status": "success", "pendingApplications": results}), 200
            else:
                return jsonify({"status": "error", "message": "No pending applications found"}), 404
    finally:
        connection.close()



if __name__ == '__main__':
    app.run(debug=True, port=5001)

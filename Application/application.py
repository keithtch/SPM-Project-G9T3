from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
import os

app = Flask(__name__)
CORS(app)

load_dotenv('../.env')

# Getting the database connection
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('RDS_HOST'),
        user=os.environ.get('RDS_USER'),
        password=os.environ.get('RDS_PASSWORD'),
        database= os.environ.get('RDS_DATABASE')
    )

# When we run the application.py , auto connects to the database and returns the data from the Application table
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
        
        
# retrieve the pending applications of the subordinates of the reporting manager   
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
        
# Adding another route for getApproved and getRejected applications each

# getApprovedApplications
# 1. Same as getPendingApplications, but the status is 'Approved'
# Retrieveing all the pening applications 
@app.route('/getApprovedApplications', methods=['POST'])
def getApprovedApplications():
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
                AND a.Status_Of_Application = 'Approved'
            """
            cursor.execute(query, (reporting_manager_id,))  # Pass the reporting manager's ID
            results = cursor.fetchall()

            if results:
                return jsonify({"status": "success", "approvedApplications": results}), 200
            elif len(results) == 0:
                return jsonify({"status": "success", "approvedApplications": results}), 200
            else:
                return jsonify({"status": "error", "message": "No approved applications found"}), 404
    finally:
        connection.close()
        
    

# getRejectedApplication
# 1. Prompt a front end textbox to state reason 
# 2. Once submitted, push to database 
# 3. Under the Team Rejected Application tab, display the datbase rejected rows 
@app.route('/getRejectedApplications', methods=['POST'])
def getRejectedApplications():
    data = request.get_json()
    reporting_manager_id = data.get('staffID')
    
    connection = get_db_connection() 
    try:
        with connection.cursor() as cursor:
            # SQL Query: Join Employee and Application tables to get subordinates' pending applications
            query = """
                SELECT a.Staff_ID, a.Date_Applied, a.Time_Of_Day, a.Status_Of_Application, a.Reason
                FROM Employee e
                JOIN Application a ON e.Staff_ID = a.Staff_ID
                WHERE e.Reporting_Manager = %s  -- Using reporting_manager_id
                AND a.Status_Of_Application = 'Rejected'
            """
            cursor.execute(query, (reporting_manager_id,))  # Pass the reporting manager's ID
            results = cursor.fetchall()

            if results:
                return jsonify({"status": "success", "rejectedApplications": results}), 200
            elif len(results) == 0:
                return jsonify({"status": "success", "rejectedApplications": results}), 200
            else:
                return jsonify({"status": "error", "message": "No rejected applications found"}), 404
    finally:
        connection.close()


# Once the manager approves the application, the status of the application will be updated to 'Approved'      
@app.route('/approveApplication', methods=['POST'])
def approveApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                UPDATE Application
                SET Status_Of_Application = 'Approved'
                WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
            """
            cursor.execute(query, (staff_id, date_applied, time_of_day))
            connection.commit()
            return jsonify({"status": "success", "message": "Application approved"}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Failed to approve application"}), 500
    finally:
        connection.close()       

            
   
        

if __name__ == '__main__':
    app.run(debug=True, port=5001)

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)


load_dotenv('../.env')

def dummy_function():
    pass
    


# Getting the database connection
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('RDS_HOST'),
        user=os.environ.get('RDS_USER'),
        password=os.environ.get('RDS_PASSWORD'),
        database= os.environ.get('RDS_DATABASE')
    )
def send_email(subject,body,email):
    try:
        # Set up the email sender credentials
        email_sender = os.environ.get('EMAIL_SENDER')
        email_password = os.environ.get('EMAIL_PASSWORD')

        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email
        msg['Subject'] = subject

        # Attach the email body to the message
        msg.attach(MIMEText(body, 'plain'))

        # Set up the secure SSL context and SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email, msg.as_string())

        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")

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
    dept = {}
    deptDone = False
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Role, Dept FROM Employee WHERE Staff_ID = %s", (id))
            result = cursor.fetchall()
            role,deptName = result[0]
            print(role)

            cursor.execute("SELECT Staff_ID,Staff_FName FROM Employee")
            nameResult = cursor.fetchall()
            teamNames = {key:value for key,value in nameResult}
            print(teamNames)
            if role == 2 and deptName != 'HR':
                cursor.execute("SELECT * FROM Employee WHERE Reporting_Manager = (SELECT Reporting_Manager FROM Employee WHERE Staff_ID = %s)",(id))
                staffResult = cursor.fetchall()
                staff = {teamNames[staffResult[0][7]]: [list(row) for row in staffResult]}
                print(staff)
            # elif role == 3:
            #     cursor.execute("SELECT * FROM Employee WHERE Reporting_Manager = %s", (id))
            else:
                if role == 1 or deptName == 'HR':
                    id = 130002
                cursor.execute("SELECT * FROM Employee")
                allStaff = cursor.fetchall()
                allStaff = [list(row) for row in allStaff]
                queue.append(id)
                while len(queue)>0:
                    tempID = int(queue.pop())
                    for employee in allStaff:
                        


                        if (int(employee[7]) == tempID and (employee not in staff.values()) and (employee[0] != employee[7])):

                            if employee[0] != 130002:
                                if employee[3] not in dept.keys():
                                    dept[employee[3]] = []
                                if employee not in dept[employee[3]]:
                                    dept[employee[3]].append(employee)
                            if teamNames[tempID] not in staff:
                                staff[teamNames[tempID]] = []
                            if employee[8] == 1 or employee[8] == 3:
                                queue.append(employee[0])
                            staff[teamNames[tempID]].append(employee)
                print('\n\ntest!!',staff.values())
            return {'employees':staff, 'dept':dept}
    finally:
        connection.close()

@app.route('/findDept', methods=['POST'])
def findDept():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Employee")
    finally:
        connection.close()

# When we run the application.py , auto connects to the database and returns the data from the Application table
@app.route('/application')
def apply():
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Application")
            result = cursor.fetchall()
            return {'data': result}
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if connection:
            connection.close()
    
        
def retrieve_highest_recurring_ID():
    connection = get_db_connection()
    try: 
        with connection.cursor() as cursor:
            retrieval = "Select MAX(Recurring_ID) from Application where Recurring_ID is not NULL"
            cursor.execute(retrieval)
            result = cursor.fetchone()
            print(result[0])
            return result[0] if result else 0
    finally:
        connection.close()
            


@app.route('/updateDates',methods=['POST'])
def updateDates():
    data = request.get_json( )
    dates = data.get('dates')
    highest_recurring_id= int(retrieve_highest_recurring_ID())
    current_recurring_id = highest_recurring_id + 1
    print(dates)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for entry in dates:
                if entry[8] == 'recurring':
                    application_query= """INSERT INTO Application (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Start_Date, End_Date,Recurring_ID, Recurring_Day)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cursor.execute(application_query,(entry[0],entry[1],entry[2],entry[3],entry[4],entry[5],entry[6],entry[7],current_recurring_id, entry[9]))
                    connection.commit()
                    print('application success')

                    log_query="""
                        INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Start_Date, End_Date,Recurring_ID, Recurring_Day) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    cursor.execute(log_query,(entry[0],entry[1],entry[2],entry[3],entry[4],entry[5],entry[6],entry[7],current_recurring_id,entry[9]))
                    connection.commit()
                    print('application success logged')
                else:
                    if entry[2] == 'AM':
                        check_query = """SELECT * FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND (Status_Of_Application = 'Approved' OR Status_Of_Application = 'Pending') AND (Time_Of_Day = 'Full Day' OR Time_Of_Day = 'AM')"""
                    elif entry[2] == 'PM':
                        check_query = """SELECT * FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND (Status_Of_Application = 'Approved' OR Status_Of_Application = 'Pending') AND (Time_Of_Day = 'Full Day' OR Time_Of_Day = 'PM')"""
                    else:
                        check_query = """SELECT * FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND (Status_Of_Application = 'Approved' OR Status_Of_Application = 'Pending') AND (Time_Of_Day = 'AM' OR Time_Of_Day = 'PM')"""


                    cursor.execute(check_query,(entry[0],entry[1]))
                    result = cursor.fetchall()
                    print('tihs',result, 'END')
                    
                    if result:
                        return jsonify({"status": "error", "message": "Application already exists"}), 400
                    application_query= """INSERT INTO Application (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Start_Date, End_Date, Recurring_Day)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cursor.execute(application_query,(entry[0],entry[1],entry[2],entry[3],entry[4],entry[5],entry[1],entry[1],entry[9]))
                    connection.commit()
                    print('application success')

                    log_query="""
                        INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Start_Date, End_Date, Recurring_Day) VALUES (%s,%s,%s,%s,%s,%s, %s, %s, %s)
                    """
                    cursor.execute(log_query,(entry[0],entry[1],entry[2],entry[3],entry[4],entry[5], entry[1], entry[1],entry[8]))
                    connection.commit()
                    print('application success logged')

             
            if dates:
                # print(dates)
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
        
@app.route('/getTeamApplications', methods=['POST'])
def getTeamApplications():
    data = request.get_json()
    reporting_manager_id = data.get('staffID')  # staffID from the front-end
    connection = get_db_connection() 
    try:
        with connection.cursor() as cursor:
            # SQL Query: Join Employee and Application tables to get subordinates' applications
            query = """
                SELECT a.Staff_ID, a.Date_Applied, a.Time_Of_Day, a.Status_Of_Application, a.Reason, a.Start_Date, a.End_Date, a.Recurring_ID, a.recurring_day, a.manager_reason, a.Staff_Withdrawal_Reason
                FROM Employee e
                JOIN Application a ON e.Staff_ID = a.Staff_ID
                WHERE e.Reporting_Manager = %s  -- Using reporting_manager_id
            """
            cursor.execute(query, (reporting_manager_id,))  # Pass the reporting manager's ID
            results = cursor.fetchall()

            if results:
                return jsonify({"status": "success", "Applications": results}), 200
            elif len(results) == 0:
                return jsonify({"status": "success", "Applications": results}), 200
            else:
                return jsonify({"status": "error", "message": "No applications found"}), 404
    finally:
        connection.close()

# Withdrawing the pending application and logging it
# this will delete the application from the application db and log it in the log db

@app.route('/withdrawPendingApplication', methods=['POST'])
def withdrawApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    reason = data.get('Reason') 
    status= data.get('Status')
    # Input validation
    if not isinstance(staff_id, str):
        return jsonify({"status": "error", "message": "Invalid Staff_ID"}), 400

    managerid = find_manager(staff_id)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Step 1: Delete the pending application from the Application table
            delete_query = """
                DELETE FROM Application
                WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
                AND Status_Of_Application = %s
            """
            cursor.execute(delete_query, (staff_id, date_applied, time_of_day,status))
            connection.commit()
            print('i did this part')

            # Step 2: Log the withdrawal in the Log table
            log_query = """
                INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason)
                VALUES (%s, %s, %s, %s, %s , %s)
            """
            cursor.execute(log_query, (staff_id, date_applied, time_of_day, managerid,'Withdrawn', reason))
            connection.commit()
            print('i did this part')


            return jsonify({"status": "success", "message": "Application withdrawn and logged"}), 200
    except Exception as e:
        print(f"Error withdrawing application: {e}")
        return jsonify({"status": "error", "message": "Failed to withdraw application"}), 500
    finally:
        connection.close()

def get_recurring_ID(a,b,c):
    connection = get_db_connection()
    try: 
        with connection.cursor() as cursor:
            retrieval = "Select Recurring_ID from Application WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s"
            cursor.execute(retrieval,(a,b,c))
            result = cursor.fetchone()
            print(result)
            print(result[0])
            return result[0]
    finally:
        connection.close() 

# Once the manager approves the application, the status of the application will be updated to 'Approved'      
# AMQP send message to exchange to publish message upon manager's approval
@app.route('/approveApplication', methods=['POST'])
def approveApplication():
    
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    dayToNum = {'Monday': 0, 'Tuesday': 1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}

    # Validate input data
    if not staff_id or not date_applied or not time_of_day:
        return jsonify({"status": "error", "message": "Missing required data"}), 400

    if not isinstance(staff_id, int):
        return jsonify({"status": "error", "message": "Invalid Staff_ID"}), 400

    start = end = day = None #Initialise variables
    if len(date_applied) > 15:
        start, end = date_applied.split(' to ')
        end, day = end.split(' ')
        day = dayToNum[day[1:-1]]
        print(start,end,day)
        date_applied = start

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            select_query = """
                SELECT * FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
                """
            print(staff_id,date_applied,time_of_day)
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()
            print(application)
            if not application:
                return jsonify({"status": "error", "message": "Application not found"}), 404 #Return error if application not found
            
            recurring_id = application[10]
            print(recurring_id)
            if recurring_id is not None and start and end and day is not None: #Variable check for start,end and day.
                delete_query = """
                    DELETE FROM Application
                    WHERE Recurring_ID = %s
                """
                cursor.execute(delete_query, (recurring_id))
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")

                dates = []
                current = start_date + timedelta((day-start_date.weekday() + 7) % 7)

                while current <= end_date:
                    print(current)
                    dates.append(current.strftime("%Y-%m-%d"))
                    current += timedelta(days=7)
                
                print(dates)
                for date in dates:
                    query = """
                        INSERT INTO Application (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason, Start_Date, End_Date)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    cursor.execute(query, (application[0],date,application[2],application[3],'Approved',application[5],'No Issue',date,date))
                    
                    log_query="""
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason, Start_Date, End_Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
                    """
                    cursor.execute(log_query, (application[0], date, application[2], application[3], 'Approved', application[5],'No Issue',date,date))
                connection.commit()
            else:
                query = """
                    UPDATE Application
                    SET Status_Of_Application = 'Approved' , Manager_Reason = 'No Issue'
                    WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
                """
                cursor.execute(query, (staff_id, date_applied, time_of_day))
                connection.commit()
                

                log_query="""
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason, Start_Date, End_Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
                    """
                cursor.execute(log_query, (staff_id, date_applied, time_of_day, application[3], 'Approved', application[5], 'No Issue' ,application[8],application[9]))
                connection.commit()
                
                
            
           
            # Retrieve the employee's email address
            cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (staff_id,))
            
            
            result = cursor.fetchone()
            if result:
                email = result[0]
            else:
                email = None  # Handle the case where the email is not found
            print(email)
             # Prepare the email content
            subject = "Your WFH Application has been Approved"
            body = f"""Dear Employee,

            Your WFH application for {date_applied} ({time_of_day}) has been approved.

            Best regards,
            Management
            """
            # Send the email
            if email:
                send_email(subject,body,email)
                
            else:
                print("Employee email not found; cannot send email.")            
            
            
            
            return jsonify({"status": "success", "message": "Application approved"}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Failed to approve application"}), 500
    finally:
        connection.close()   
        
# Once the manager rejects the application, the status of the application will be updated to 'Rejected'
@app.route('/rejectApplication', methods=['POST'])
def rejectApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    rejection_reason = data.get('Rejection_Reason')

    dayToNum = {'Monday': 0, 'Tuesday': 1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}   
    start = end = day = None #Initialise variables
    if len(date_applied) > 15:
        start, end = date_applied.split(' to ')
        end, day = end.split(' ')
        day = dayToNum[day[1:-1]]
        print(start,end,day)
        date_applied = start

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            select_query = """
                SELECT * FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
                """
            print(staff_id,date_applied,time_of_day)
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()
            if not application:
                return jsonify({"status": "error", "message": "Application not found"}), 404 #Return error if application not found
            recurring_id = application[10]
            if recurring_id is not None:
                query = """
                    UPDATE Application
                    SET Status_Of_Application = 'Rejected', Manager_Reason = %s
                    WHERE Recurring_ID = %s
                """
                cursor.execute(query, (rejection_reason,recurring_id))
                connection.commit()
                
                log_query="""
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason, Start_Date, End_Date, Recurring_ID,Recurring_Day) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
                    """
                cursor.execute(log_query, (staff_id, date_applied, time_of_day, application[3], 'Rejected', application[5], rejection_reason, application[8],application[9], application[10],application[11]))
                connection.commit()
            else:
                query = """
                    UPDATE Application
                    SET Status_Of_Application = 'Rejected', Manager_Reason = %s
                    WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
                """
                cursor.execute(query, (rejection_reason, staff_id, date_applied, time_of_day))
                connection.commit()
                
                log_query="""
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason, Start_Date, End_Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                cursor.execute(log_query, (staff_id, date_applied, time_of_day, application[3], 'Rejected', application[5], rejection_reason, application[8],application[9]))
                connection.commit()
            
             # Retrieve the employee's email address
            cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (staff_id,))
            result = cursor.fetchone()
            if result:
                email = result[0]
            else:
                email = None  # Handle the case where the email is not found
            print(email)
             # Prepare the email content
            subject = "Your WFH Application has been Rejected"
            body = f"""Dear Employee,

            Your WFH application for {date_applied} ({time_of_day}) has been rejected.
            
            Reason : {rejection_reason}.

            Best regards,
            Management
            """
            # Send the email
            if email:
                send_email(subject,body,email)

            else:
                print("Employee email not found; cannot send email.")   
            
            
            
            return jsonify({"status": "success", "message": "Application rejected"}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Failed to reject application"}), 500
    finally:
        connection.close()
        
        
def find_manager(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Employee")
            result = cursor.fetchall()
            staffind = findid(id,result)
            managerid = result[staffind][7]
            print(managerid)
            return managerid
    finally:
        connection.close()
        
def findid(id, arr):
    try:
        id = int(id)
    except ValueError:
        return -1  # Return -1 or any other value to indicate invalid id

    for i in range(len(arr)):
        if int(arr[i][0]) == id:
            print(i)
            return i
    return 0

@app.route('/pendingwithdrawApprovedApplication', methods=['POST'])
def pendingwithdrawApprovedApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    withdraw_reason = data.get('Withdraw_Reason')
    manager_id = find_manager(staff_id)
    print(manager_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Retrieve application details before deleting
            select_query = """
                SELECT Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason
                FROM Application
                WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Approved'
            """
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()

            if application:
                # Update the status of the application to Pending_Withdrawal
                update_query = """
                    UPDATE Application SET Status_Of_Application = 'Pending_Withdrawal', Staff_Withdrawal_Reason = %s
                    WHERE Staff_ID = %s and Date_Applied = %s and Time_Of_Day = %s and Status_Of_Application = 'Approved';

                """

                cursor.execute(update_query, (withdraw_reason,staff_id, date_applied, time_of_day))
                

                # Insert into Staff_Application_Logs
                log_query = """
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager,
                    Status_Of_Application, Reason, Manager_Reason, Staff_Withdrawal_Reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(log_query, (
                    application[0],  # Staff_ID
                    application[1],  # Date_Applied
                    application[2],  # Time_Of_Day
                    application[3],  # Reporting_Manager
                    'Pending_Withdrawal',     # Status_Of_Application
                    application[5],  # Reason
                    application[6],  # Manager_Reason
                    withdraw_reason,  # Withdrawal_Reason
                    
                ))

                connection.commit()
                # Insert code for email notification
                 # Retrieve the manager's email address
                cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (manager_id,))
                manager_result = cursor.fetchone()
                if manager_result:
                    manager_email = manager_result[0]
                    print(manager_email)
                else:
                    manager_email = None  # Handle the case where the email is not found

                # Prepare the email content
                subject = "Employee Withdrawal of Approved WFH Application"
                body = f"""Dear Manager,

                Employee {staff_id} has applied for withdrawal for their approved WFH application for {date_applied} ({time_of_day}).

                Withdrawal Reason: {withdraw_reason}

                Best regards,
                HR System
                """

                # Send the email to the manager
                if manager_email:
                    send_email(subject,body,manager_email)
                else:
                    print("Manager email not found; cannot send email.")

                
                
                
                return jsonify({"status": "success", "message": "Pending Application withdrawal submitted"}), 200
            else:
                return jsonify({"status": "error", "message": "Application not found or not approved"}), 404
    except Exception as e:
        print(f"Error withdrawing approved application: {e}")
        return jsonify({"status": "error", "message": "Failed to withdraw application"}), 500
    finally:
        connection.close()
        
        
@app.route('/RejectPendingWithdrawApprovedApplication', methods=['POST'])
def RejectedPendingWithdrawApprovedApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    manager_withdraw_reason = data.get('Withdrawal_Reason')
    manager_id = find_manager(staff_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Retrieve application details before deleting
            select_query = """
                SELECT Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason, Staff_Withdrawal_Reason FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Pending_Withdrawal'
            """
            print(staff_id,date_applied,time_of_day)
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()

            if application:
                # Update the status of the application to Pending_Withdrawal
                update_query = """
                    UPDATE Application SET Status_Of_Application = 'Approved', Manager_Reason = %s
                    WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Pending_Withdrawal'
                """
                print(staff_id,date_applied,time_of_day)
                cursor.execute(update_query, (manager_withdraw_reason,staff_id, date_applied, time_of_day))
                # Insert into Staff_Application_Logs
                log_query = """
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager,
                    Status_Of_Application, Reason, Manager_Reason,Staff_Withdrawal_Reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(log_query, (
                    application[0],  # Staff_ID
                    application[1],  # Date_Applied
                    application[2],  # Time_Of_Day
                    application[3],  # Reporting_Manager
                    'Approved',     # Status_Of_Application
                    application[5],  # Reason
                    manager_withdraw_reason,
                    application[7],  # Manager_Reason
                     # manager approve withdraw reason
                ))
                connection.commit()
                # Insert code for email notification
                 # Retrieve the manager's email address
                cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (staff_id,))
                staff_result = cursor.fetchone()
                if staff_result:
                    staff_email = staff_result[0]
                else:
                    staff_email = None  # Handle the case where the email is not found

                # Prepare the email content
                subject = "Rejection of withdrawal of approved WFH"
                body = f"""Dear Manager,

                Manager {manager_id} has rejected your withdrawal for your approved WFH application for {date_applied} ({time_of_day}).

                Rejecting Withdrawal Reason: {manager_withdraw_reason}

                Best regards,
                HR System
                """

                # Send the email to the manager
                if staff_email:
                    send_email(subject,body,staff_email)
                else:
                    print("Manager email not found; cannot send email.")

                
                
                
                return jsonify({"status": "success", "message": "Rejected withdrawal for application and logged"}), 200
            else:
                return jsonify({"status": "error", "message": "Application not found or not approved"}), 404
    except Exception as e:
        print(f"Error withdrawing approved application: {e}")
        return jsonify({"status": "error", "message": "Failed to withdraw application"}), 500
    finally:
        connection.close()

@app.route('/ApprovePendingWithdrawApprovedApplication', methods=['POST'])
def ApprovePendingWithdrawApprovedApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    manager_id = find_manager(staff_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Retrieve application details before deleting
            select_query = """
                SELECT Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Pending_Withdrawal'
            """
            print(staff_id,date_applied,time_of_day)
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()

            if application:
                # Update the status of the application to Pending_Withdrawal
                #print("Application:",application)
                delete_query = """
                    DELETE FROM Application
                    WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Pending_Withdrawal'
                """
                print(staff_id,date_applied,time_of_day)
                cursor.execute(delete_query, (staff_id, date_applied, time_of_day))

                # Insert into Staff_Application_Logs
                log_query = """
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager,
                    Status_Of_Application, Reason, Manager_Reason,Staff_Withdrawal_Reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(log_query, (
                    application[0],  # Staff_ID
                    application[1],  # Date_Applied
                    application[2],  # Time_Of_Day
                    application[3],  # Reporting_Manager
                    'Withdrawn',     # Status_Of_Application
                    application[5],  # Reason
                    application[6],  # Manager_Reason
                    '' # manager approve withdraw reason
                ))

                connection.commit()
                # Insert code for email notification
                 # Retrieve the manager's email address
                cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (staff_id,))
                staff_result = cursor.fetchone()
                if staff_result:
                    staff_email = staff_result[0]
                else:
                    staff_email = None  # Handle the case where the email is not found

                # Prepare the email content
                subject = "Approval of withdrawal of approved WFH"
                body = f"""Dear Manager,

                Manager {manager_id} has approved your withdrawal for your approved WFH application for {date_applied} ({time_of_day}).

                Best regards,
                HR System
                """

                # Send the email to the manager
                if staff_email:
                    send_email(subject,body,staff_email)
                else:
                    print("Manager email not found; cannot send email.")

                
                
                
                return jsonify({"status": "success", "message": "Rejected withdrawal for application and logged"}), 200
            else:
                return jsonify({"status": "error", "message": "Application not found or not approved"}), 404
    except Exception as e:
        print(f"Error withdrawing approved application: {e}")
        return jsonify({"status": "error", "message": "Failed to withdraw application"}), 500
    finally:
        connection.close()

@app.route('/withdrawApprovedApplication', methods=['POST'])
def withdrawApprovedApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    withdraw_reason = data.get('Withdraw_Reason')
    manager_id = find_manager(staff_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Retrieve application details before deleting
            select_query = """
                SELECT Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason
                FROM Application
                WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Approved'
            """
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()

            if application:
                # Delete the application from the Application table
                delete_query = """
                    DELETE FROM Application
                    WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Approved'
                """
                cursor.execute(delete_query, (staff_id, date_applied, time_of_day))

                # Insert into Staff_Application_Logs
                log_query = """
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager,
                    Status_Of_Application, Reason, Manager_Reason, Staff_Withdrawal_Reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(log_query, (
                    application[0],  # Staff_ID
                    application[1],  # Date_Applied
                    application[2],  # Time_Of_Day
                    application[3],  # Reporting_Manager
                    'Withdrawn',     # Status_Of_Application
                    application[5],  # Reason
                    application[6],  # Manager_Reason
                    withdraw_reason  # Withdrawal_Reason
                ))

                connection.commit()
                # Insert code for email notification
                 # Retrieve the manager's email address
                cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (manager_id,))
                manager_result = cursor.fetchone()
                if manager_result:
                    manager_email = manager_result[0]
                else:
                    manager_email = None  # Handle the case where the email is not found

                # Prepare the email content
                subject = "Employee Withdrawal of Approved WFH Application"
                body = f"""Dear Manager,

                Employee {staff_id} has withdrawn their approved WFH application for {date_applied} ({time_of_day}).

                Withdrawal Reason: {withdraw_reason}

                Best regards,
                HR System
                """

                # Send the email to the manager
                if manager_email:
                    send_email(subject,body,manager_email)
                else:
                    print("Manager email not found; cannot send email.")

                
                
                
                return jsonify({"status": "success", "message": "Approved application withdrawn and logged"}), 200
            else:
                return jsonify({"status": "error", "message": "Application not found or not approved"}), 404
    except Exception as e:
        print(f"Error withdrawing approved application: {e}")
        return jsonify({"status": "error", "message": "Failed to withdraw application"}), 500
    finally:
        connection.close()
            
@app.route('/changeApplication', methods=['POST'])
def changeApplication():
    data = request.get_json()
    staff_id = data.get('Staff_ID')
    date_applied = data.get('Date_Applied')
    time_of_day = data.get('Time_Of_Day')
    changeDate = data.get('changeDate')
    manager_id = find_manager(staff_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Retrieve application details before deleting
            select_query = """
                SELECT Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager, Status_Of_Application, Reason, Manager_Reason FROM Application WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Approved'
            """
            print(staff_id,date_applied,time_of_day)
            cursor.execute(select_query, (staff_id, date_applied, time_of_day))
            application = cursor.fetchone()

            if application:
                # Update the status of the application to Pending_Withdrawal
                update_query = """
                    UPDATE Application SET Status_Of_Application = 'Pending', Date_Applied = %s 
                    WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s AND Status_Of_Application = 'Approved'
                """
                print(staff_id,date_applied,time_of_day)
                cursor.execute(update_query, (changeDate, staff_id, date_applied, time_of_day))

                # Insert into Staff_Application_Logs
                log_query = """
                    INSERT INTO Staff_Application_Logs (Staff_ID, Date_Applied, Time_Of_Day, Reporting_Manager,
                    Status_Of_Application, Reason, Manager_Reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(log_query, (
                    application[0],  # Staff_ID
                    changeDate,  # Date_Applied
                    application[2],  # Time_Of_Day
                    application[3],  # Reporting_Manager
                    'Pending',     # Status_Of_Application
                    application[5],  # Reason
                    application[6],  # Manager_Reason
                ))

                connection.commit()
                # Insert code for email notification
                 # Retrieve the manager's email address
                cursor.execute("SELECT Email FROM Employee WHERE Staff_ID = %s", (staff_id,))
                staff_result = cursor.fetchone()
                if staff_result:
                    staff_email = staff_result[0]
                else:
                    staff_email = None  # Handle the case where the email is not found

                # Prepare the email content
                subject = "Change of approved WFH"
                body = f"""Dear Manager,

                Manager {manager_id} has rejected your withdrawal for your approved WFH application for {date_applied} ({time_of_day}).

                Rejecting Withdrawal Reason: 

                Best regards,
                HR System
                """

                # Send the email to the manager
                if staff_email:
                    send_email(subject,body,staff_email)
                else:
                    print("Manager email not found; cannot send email.")

                
                
                
                return jsonify({"status": "success", "message": "Rejected withdrawal for application and logged"}), 200
            else:
                return jsonify({"status": "error", "message": "Application not found or not approved"}), 404
    except Exception as e:
        print(f"Error withdrawing approved application: {e}")
        return jsonify({"status": "error", "message": "Failed to withdraw application"}), 500
    finally:
        connection.close()

@app.route('/getLogs')
def getLogs():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Staff_Application_Logs")
            result = cursor.fetchall()
            if result:
                return jsonify({"status": "success", "data": result}), 200
            else:
                return jsonify({"status": "success", "data": [], "message": "No logs found"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()
   
        

if __name__ == '__main__':
    app.run(debug=True, port=5001)

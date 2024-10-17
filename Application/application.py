from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        
@app.route('/getTeamApplications', methods=['POST'])
def getTeamApplications():
    data = request.get_json()
    reporting_manager_id = data.get('staffID')  # staffID from the front-end
    connection = get_db_connection() 
    try:
        with connection.cursor() as cursor:
            # SQL Query: Join Employee and Application tables to get subordinates' applications
            query = """
                SELECT a.Staff_ID, a.Date_Applied, a.Time_Of_Day, a.Status_Of_Application, a.Reason
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
    managerid = find_manager(staff_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Step 1: Delete the pending application from the Application table
            delete_query = """
                DELETE FROM Application
                WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
                AND Status_Of_Application = 'Pending'
            """
            cursor.execute(delete_query, (staff_id, date_applied, time_of_day))
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



# Once the manager approves the application, the status of the application will be updated to 'Approved'      
# AMQP send message to exchange to publish message upon manager's approval
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
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                UPDATE Application
                SET Status_Of_Application = 'Rejected', Manager_Reason = %s
                WHERE Staff_ID = %s AND Date_Applied = %s AND Time_Of_Day = %s
            """
            cursor.execute(query, (rejection_reason, staff_id, date_applied, time_of_day))
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
            return managerid
    finally:
        connection.close()
        
def findid(id,arr):
    for i in range(len(arr)):
        if id==arr[i][0]:
            return i
    
    return 0



            
   
        

if __name__ == '__main__':
    app.run(debug=True, port=5001)

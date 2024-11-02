import pytest
from flask import Flask
from application import app, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_apply(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    response = client.get('/application')
    assert response.status_code == 200
    assert response.json == {'data': [{'id': 1, 'name': 'Test'}]}

def test_updateDates(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)
    mocker.patch('application.retrieve_highest_recurring_ID', return_value=1)

    data = {
        'dates': [
            [1, '2023-01-01', 'Morning', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday']
        ]
    }
    response = client.post('/updateDates', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_getApps(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'ids': [1],
        'date': '2023-01-01',
        'status': 'Pending'
    }
    response = client.post('/getApps', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_getTeamApplications(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'staffID': 1
    }
    response = client.post('/getTeamApplications', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_withdrawApplication(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)
    mocker.patch('application.find_manager', return_value=1)

    data = {
        'Staff_ID': '1',
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'Morning',
        'Reason': 'Reason',
        'Status': 'Pending'
    }
    response = client.post('/withdrawPendingApplication', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'


def test_approveApplication(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    # Adjust the return value to match the expected structure
    mock_cursor.fetchone = mocker.Mock(side_effect=[
        [1, '2023-01-01', 'AM', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday', 1],  # Application data
        ['test@example.com']  # Employee email
    ])
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    # Mock the get_recurring_ID function
    mocker.patch('application.get_recurring_ID', return_value=1)

    # Mock the email sending part
    mock_smtp = mocker.patch('smtplib.SMTP_SSL', autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail = mocker.Mock()

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01 to 2023-01-07 (Monday)',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
    mock_smtp_instance.sendmail.assert_called()

def test_approveApplication_with_recurring_id(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(side_effect=[
        [1, '2023-01-01', 'AM', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday', 1],  # Application data
        ['test@example.com']  # Employee email
    ])
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    # Mock the get_recurring_ID function
    mocker.patch('application.get_recurring_ID', return_value=1)

    # Mock the email sending part
    mock_smtp = mocker.patch('smtplib.SMTP_SSL', autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail = mocker.Mock()

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01 to 2023-01-07 (Monday)',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
    mock_smtp_instance.sendmail.assert_called()

def test_approveApplication_without_recurring_id(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(side_effect=[
        [1, '2023-01-01', 'AM', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday', None],  # Application data
        ['test@example.com']  # Employee email
    ])
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    # Mock the email sending part
    mock_smtp = mocker.patch('smtplib.SMTP_SSL', autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail = mocker.Mock()

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
    mock_smtp_instance.sendmail.assert_called()

def test_approveApplication_with_invalid_data(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(return_value=None)
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': 'invalid',  # Invalid data type
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 400  # Bad Request
    assert response.json['message'] == 'Invalid Staff_ID'

def test_approveApplication_with_missing_data(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(return_value=None)
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01'
        # Missing 'Time_Of_Day'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 400  # Bad Request
    assert response.json['message'] == 'Missing required data'

def test_approveApplication_with_database_error(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock(side_effect=Exception('Database error'))
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert 'Failed' in response.json['message']

def test_approveApplication_with_email_error(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(side_effect=[
        [1, '2023-01-01', 'AM', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday', 1],  # Application data
        ['test@example.com']  # Employee email
    ])
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    # Mock the get_recurring_ID function
    mocker.patch('application.get_recurring_ID', return_value=1)

    # Mock the email sending part and simulate an error
    mock_smtp = mocker.patch('smtplib.SMTP_SSL', autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail = mocker.Mock(side_effect=Exception('Email error'))

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
    mock_smtp_instance.sendmail.assert_called()

def test_approveApplication_with_no_email(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(side_effect=[
        [1, '2023-01-01', 'AM', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday', 1],  # Application data
        None  # No email found
    ])
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    # Mock the get_recurring_ID function
    mocker.patch('application.get_recurring_ID', return_value=1)

    # Mock the email sending part
    mock_smtp = mocker.patch('smtplib.SMTP_SSL', autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail = mocker.Mock()

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM'
    }
    response = client.post('/approveApplication', json=data)

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
    mock_smtp_instance.sendmail.assert_not_called()  # Ensure no email is sent


def test_rejectApplication(client, mocker):
    # Mock the database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.execute = mocker.Mock()
    mock_cursor.fetchone = mocker.Mock(side_effect=[
        [1, '2023-01-01', 'AM', 'Manager', 'Pending', 'Reason', '2023-01-01', '2023-01-01', 'recurring', 'Monday', 1],  # Application data
        ['test@example.com']  # Employee email
    ])
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    # Mock the email sending part
    mock_smtp = mocker.patch('smtplib.SMTP_SSL', autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail = mocker.Mock()

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM',
        'Rejection_Reason': 'Reason'
    }
    response = client.post('/rejectApplication', json=data)

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
    mock_smtp_instance.sendmail.assert_called()

def test_getLogs(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    response = client.get('/getLogs')
    assert response.status_code == 200
    assert response.json == {'status': 'success', 'data': [{'id': 1, 'name': 'Test'}]}

# Edge Cases

def test_empty_database(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    response = client.get('/application')
    assert response.status_code == 200
    assert response.json == {'data': []}

def test_invalid_data(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall = mocker.Mock(return_value=[[1, 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data']])
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': [],  # Invalid data type
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM',
        'Reason': 'Reason',
        'Status': 'Pending'
    }
    response = client.post('/withdrawPendingApplication', json=data)

    assert response.status_code == 400  # Expecting a 400 Bad Request status code
    assert response.json['status'] == 'error'
    assert 'Invalid Staff_ID' in response.json['message']

def test_boundary_values(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall = mocker.Mock(return_value=[[1, 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data']])
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': '1',
        'Date_Applied': '9999-12-31',  # Boundary date value
        'Time_Of_Day': 'AM',
        'Reason': 'Reason',
        'Status': 'Pending'
    }
    response = client.post('/withdrawPendingApplication', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_concurrent_requests(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_cursor.fetchall = mocker.Mock(return_value=[[1, 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data', 'mocked_data']])
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': '1',
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'AM',
        'Reason': 'Reason',
        'Status': 'Pending'
    }

    # Simulate concurrent requests
    response1 = client.post('/withdrawPendingApplication', json=data)
    response2 = client.post('/withdrawPendingApplication', json=data)
    assert response1.status_code == 200
    assert response1.json['status'] == 'success'
    assert response2.status_code == 200
    assert response2.json['status'] == 'success'

def test_database_connection_issue(client, mocker):
    mocker.patch('application.get_db_connection', side_effect=Exception('Database connection failed'))

    response = client.get('/application')
    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert 'Database connection failed' in response.json['message']

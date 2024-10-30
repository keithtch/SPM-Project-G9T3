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
    mocker.patch('application.retrieve_recurring_ID', return_value=1)

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
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'Morning',
        'Reason': 'Reason',
        'Status': 'Pending'
    }
    response = client.post('/withdrawPendingApplication', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_approveApplication(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'Morning'
    }
    response = client.post('/approveApplication', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_rejectApplication(client, mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.__enter__ = mocker.Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.Mock(return_value=False)
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('application.get_db_connection', return_value=mock_connection)

    data = {
        'Staff_ID': 1,
        'Date_Applied': '2023-01-01',
        'Time_Of_Day': 'Morning',
        'Rejection_Reason': 'Reason'
    }
    response = client.post('/rejectApplication', json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

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
    assert response.json == {'data': [{'id': 1, 'name': 'Test'}]}
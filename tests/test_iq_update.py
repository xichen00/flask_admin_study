from flask import g, session


def test_basic_link(client):
    assert client.get('/').status_code == 404

    rv = client.get('/iq7/v1/updates')
    assert rv.status_code == 200
    assert b'Version 7.0 0161' in rv.data
    assert b'Version 7.0 0170' in rv.data

    rv = client.get('/iq7/v1/updates?greaterThan=0161')
    assert rv.status_code == 200
    assert b'Version 7.0 0161' not in rv.data
    assert b'Version 7.0 0170' in rv.data

    rv = client.get('/iq7/v1/updates?hasUpdatesFor=0161')
    assert rv.status_code == 200
    assert b'true' in rv.data

    rv = client.get('/iq7/v1/updates?hasUpdatesFor=0170')
    assert rv.status_code == 200
    assert b'false' in rv.data

    rv = client.get('/iq7/v1/updates/0161')
    assert rv.status_code == 200
    assert b'RP-5381' in rv.data

    rv = client.get('/iq7/v1/updates/0161?language=de')
    assert rv.status_code == 200
    assert b'General:' not in rv.data
    assert b'Allgemein:' in rv.data

    rv = client.get('/iq7/v1/updates/0161?language=en')
    assert rv.status_code == 200
    assert b'General:' in rv.data
    assert b'Allgemein:' in rv.data


def fail_test_login(client, auth):
    # test that viewing the page renders without template errors
    #assert client.get('/admin/').status_code == 200
    assert client.get('/admin/login/').status_code == 200
    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/admin/'

#    # login request set the user_id in the session
#    # check that the user is loaded from the session
#    with client:
#        client.get('/')
#        assert session['user_id'] == 1
#        assert g.user['email'] == 'admin'

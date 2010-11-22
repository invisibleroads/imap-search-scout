'Tests for people controller'
# Import system modules
import re
import urlparse
import simplejson
# Import custom modules
from scout import model
from scout.model import meta
from scout.config import parameter
from scout.lib import store, helpers as h
from scout.tests import *


# Define shortcuts
username = 'username'
password = 'password'
nickname = u'nickname'
email = 'email@example.com'


class TestPeopleController(TestController):

    def setUp(self):
        'Clear tables'
        # Logout
        self.app.get(url('person_logout_plain'))
        # Delete all people
        meta.Session.rollback()
        meta.Session.query(model.Person).delete()
        meta.Session.query(model.PersonCandidate).delete()
        meta.Session.commit()

    def test_index(self):
        'Assert that the index page shows how many accounts are on file'
        # Initialize
        url_test = url('person_index')
        # Make sure that we begin with 0 people
        self.assert_('0 people' in self.app.get(url_test))
        # Add person
        meta.Session.add(model.Person(username, model.hashString(password), nickname, email))
        meta.Session.commit()
        # Make sure that we now have 1 person
        self.assert_('1 people' in self.app.get(url_test))

    def test_registration(self):
        'Make sure that registration works'
        # Make sure the registration page appears properly
        self.assert_('Registration' in self.app.get(url('person_register')))
        # Register
        self.app.post(url('person_register_'), dict(username=username, password=password, nickname=nickname, email=email))
        # Register with the same username but with different case
        self.app.post(url('person_register_'), dict(username=username.upper(), password=password, nickname=nickname + 'x', email=email + 'x'))
        # Register with the same nickname but with different case
        self.app.post(url('person_register_'), dict(username=username + 'x', password=password, nickname=nickname.upper(), email=email + 'x'))
        # Register with the same email but with different case
        self.app.post(url('person_register_'), dict(username=username + 'x', password=password, nickname=nickname + 'x', email=email.upper()))
        # Confirm registration
        self.app.get(url('person_confirm', ticket=meta.Session.query(model.PersonCandidate.ticket).filter_by(email=email).first()[0]))
        # Make sure the person exists
        self.assertEqual(meta.Session.query(model.Person).filter_by(email=email).count(), 1)
        # Make sure that conflicting registrations have been deleted
        self.assertEqual(meta.Session.query(model.PersonCandidate).filter_by(password_hash=model.hashString(password)).count(), 0)

    def test_reset(self):
        """
        Make sure that resetting the password works
        Trying to reset an email that does not exist should return an error
        Make sure that resetting the password does not immediately change the password
        Make sure that reset confirmation works
        """
        # Reset an unfamiliar email
        self.assertEqual(simplejson.dumps({'isOk': 0}), self.app.post(url('person_reset'), dict(email=email)).body)
        # Add person
        meta.Session.add(model.Person(username, model.hashString(password), nickname, email))
        meta.Session.commit()
        # Reset password
        self.assertEqual(simplejson.dumps({'isOk': 1}), self.app.post(url('person_reset'), dict(email=email)).body)
        # Make sure the candidate exists
        self.assertEqual(meta.Session.query(model.PersonCandidate).filter_by(email=email).count(), 1)
        # Activate candidate
        self.app.get(url('person_confirm', ticket=meta.Session.query(model.PersonCandidate.ticket).filter_by(email=email).first()[0]))
        # Make sure the password has changed
        self.assertEqual(meta.Session.query(model.Person).filter_by(password_hash=model.hashString(password)).count(), 0)

    def test_update(self):
        """
        Make sure that updating credentials works
        Make sure the update page only appears when the user is logged in
        Make sure the update form is filled with the user's credentials
        Make sure that update_ only works when the user is logged in
        Make sure that update confirmation works
        """
        # Assert that we are redirected to the login page if the person is not logged in
        response = self.app.get(url('person_update'))
        self.assertEqual(urlparse.urlparse(response.response.location).path, url('person_login', targetURL=h.encodeURL(url('person_update'))))
        # Assert that we get rejected if we try to post without logging in
        self.assertEqual(simplejson.dumps({'message': 'Login required', 'isOk': 0}), self.app.post(url('person_update_')).body)
        # Add person
        meta.Session.add(model.Person(username, model.hashString(password), nickname, email))
        meta.Session.commit()
        # Log in
        self.app.post(url('person_login_'), dict(username=username, password=password))
        # Assert that the update form is filled with the user's credentials
        responseBody = self.app.get(url('person_update')).body
        self.assert_(username in responseBody)
        self.assert_(nickname in responseBody)
        self.assert_(email in responseBody)
        # Update credentials
        username_ = store.makeRandomString(parameter.USERNAME_LENGTH_MAXIMUM)
        password_ = store.makeRandomAlphaNumericString(parameter.PASSWORD_LENGTH_AVERAGE)
        nickname_ = unicode(store.makeRandomString(parameter.NICKNAME_LENGTH_MAXIMUM))
        email_ = re.sub(r'.*@', store.makeRandomString(16) + '@', email)
        self.assertEqual(simplejson.dumps({'isOk': 1}), self.app.post(url('person_update_'), dict(username=username_, password=password_, nickname=nickname_, email=email_)).body)
        # Make sure the credentials have not changed yet
        self.assertEqual(meta.Session.query(model.Person).filter_by(username=username_, password_hash=model.hashString(password_), nickname=nickname_, email=email_).count(), 0)
        # Activate candidate
        self.app.get(url('person_confirm', ticket=meta.Session.query(model.PersonCandidate.ticket).filter_by(email=email_).first()[0]))
        # Make sure the credentials have changed
        self.assertEqual(meta.Session.query(model.Person).filter_by(username=username_, password_hash=model.hashString(password_), nickname=nickname_, email=email_).count(), 1)

    def test_login(self):
        """
        Make sure that logging in works
        Ensure that the login page shows
        Ensure that bad credentials result in an error message
        Ensure that good credentials result in a proper redirect
        """
        # Initialize
        url_test = url('person_update')
        # Assert that the login page shows and stores url
        self.assert_('Login' in self.app.get(url('person_login', targetURL=h.encodeURL(url_test))))
        # Add person
        meta.Session.add(model.Person(username, model.hashString(password), nickname, email))
        meta.Session.commit()
        # Log in using bad credentials
        self.assertEqual(simplejson.dumps({'rejection_count': 1, 'isOk': 0}), self.app.post(url('person_login_'), dict(username=username, password=password + 'x')).body)
        # Log in using good credentials
        self.assertEqual(simplejson.dumps({'isOk': 1}), self.app.post(url('person_login_'), dict(username=username, password=password)).body)

    def test_logout(self):
        """
        Make sure that logging out works
        If the person is logged in, make sure the person gets logged out
        and is redirected properly.  If the person is already logged out, 
        return the user to the page before the user tried to log out.
        """
        # Initialize
        url_test = url('person_index')
        # Add person
        meta.Session.add(model.Person(username, model.hashString(password), nickname, email))
        meta.Session.commit()
        # Logging out should redirect back
        self.assert_(url_test in self.app.get(url('person_logout', targetURL=h.encodeURL(url_test))))
        # Log in
        self.assert_('Login' in self.app.get(url('person_login', targetURL=h.encodeURL(url_test))))
        self.assertEqual(simplejson.dumps({'isOk': 1}), self.app.post(url('person_login_'), dict(username=username, password=password)).body)
        # Logging out should redirect back
        self.assert_(url_test in self.app.get(url('person_logout', targetURL=h.encodeURL(url_test))))

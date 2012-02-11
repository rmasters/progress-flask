import os
import progress
import unittest
import tempfile
from datetime import datetime

class ProgressTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, progress.app.config['DATABASE'] = tempfile.mkstemp()
        progress.app.config['TESTING'] = True
        self.app = progress.app.test_client()
        progress.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(progress.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No deadlines' in rv.data

    def test_login_logout(self):
        rv = self.login(progress.app.config['USERNAME'],
                        progress.app.config['PASSWORD'])
        assert 'You were logged in' in rv.data

        rv = self.logout()
        assert 'You were logged out' in rv.data

        rv = self.login(progress.app.config['USERNAME'] + 'x',
                        progress.app.config['PASSWORD'])
        assert 'Invalid username' in rv.data
        
        rv = self.login(progress.app.config['USERNAME'],
                        progress.app.config['PASSWORD'] + 'x')
        assert 'Invalid password' in rv.data

    def test_deadlines(self):
        self.login(progress.app.config['USERNAME'],
                   progress.app.config['PASSWORD'])

        rv = self.app.post('/add', data=dict(
            name='Test',
            deadline=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ), follow_redirects=True)
        assert 'No deadlines' not in rv.data
        assert 'Test' in rv.data

if __name__ == '__main__':
    unittest.main()

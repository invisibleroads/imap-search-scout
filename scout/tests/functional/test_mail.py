from scout.tests import *

class TestMailController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='mail', action='index'))
        # Test response...

from scout.tests import *


class TestMessagesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='messages', action='index'))
        # Test response...

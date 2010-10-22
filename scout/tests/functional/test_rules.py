from scout.tests import *


class TestRulesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='rules', action='index'))
        # Test response...

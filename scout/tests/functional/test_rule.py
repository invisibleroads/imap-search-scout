from scout.tests import *

class TestRuleController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='rule', action='index'))
        # Test response...

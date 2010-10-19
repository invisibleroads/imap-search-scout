# Import system modules
import unittest
# Import custom modules
from scout.lib import mail_store_imap, mail_process
from scout import tests
from scout.config import parameter


class TestMailProcess(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        'Load IMAP mailbox credentials for testing'
        # Call super constructor
        unittest.TestCase.__init__(self, *args, **kwargs)
        # Connect
        self.mailbox = mail_store_imap.Store(*tests.credentials)

    def setUp(self):
        # Load one message
        message = self.mailbox.read(excludes=parameter.EXCLUDED_TAGS).next()

    def tearDown(self):
        pass

    def testDeletingMessage(self):
        """
        Flag a message for deletion and make sure that the message is deleted.
        """
        pass

    def testUpdatingPrivacyViaTags(self):
        """
        If a message is set for automatic visibility, ensure that tags can influence the message's privacy.
        """
        pass

    def testUpdatingPrivacyViaRules(self):
        """
        If a message is set for automatic visibility, ensure that rules can influence the message's privacy.
        """
        pass

    def testUpdatingPrivacyManually(self):
        """
        If a message is set for manual visibility, ensure that the message can be shown or hidden.
        """
        pass

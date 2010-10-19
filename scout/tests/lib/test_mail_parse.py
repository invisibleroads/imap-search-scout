# Import system modules
from unittest import TestCase
import datetime
# Import custom modules
from scout.lib import mail_format, mail_parse


class TestMailStoreIMAP(TestCase):

    def testParseHeader(self):
        # Define
        def assertHeader(subject, fromWhom, toWhom, ccWhom, bccWhom):
            # Get
            when = datetime.datetime(2009, 9, 18, 13, 32, 0)
            header = mail_format.formatHeader(subject, when, fromWhom, toWhom, ccWhom, bccWhom)
            message = mail_parse.parseHeader(header)
            # Assert
            self.assertEqual(message['subject'], subject)
            self.assertEqual(message['when'], when)
            self.assertEqual(message['fromWhom'], fromWhom)
            self.assertEqual(message['toWhom'], toWhom)
            self.assertEqual(message['ccWhom'], ccWhom)
            self.assertEqual(message['bccWhom'], bccWhom)
        # Try different combinations
        assertHeader('subject\nsubject', 'from\nfrom', '', '', '')
        assertHeader('subject\nsubject', 'from\nfrom', 'to\nto', '', '')
        assertHeader('subject\nsubject', 'from\nfrom', '', 'cc\ncc', '')
        assertHeader('subject\nsubject', 'from\nfrom', '', '', 'bcc\nbcc')
        assertHeader('subject\nsubject', 'from\nfrom', 'to\nto', 'cc\ncc', '')
        assertHeader('subject\nsubject', 'from\nfrom', '', 'cc\ncc', 'bcc\nbcc')
        assertHeader('subject\nsubject', 'from\nfrom', 'to\nto', '', 'bcc\nbcc')
        assertHeader('subject\nsubject', 'from\nfrom', 'to\nto', 'cc\ncc', 'bcc\nbcc')

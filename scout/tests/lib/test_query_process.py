# Import system modules
import unittest
# Import custom modules
from scout.lib import query_process


class TestQueryProcess(unittest.TestCase):

    def testExtractRelevantText(self):
        'Ensure that extraction works properly'
        # Initialize
        textMachine = query_process.TextMachine(extractLength=10)
        # Define
        def extract(queryString, content, extract):
            self.assertEqual(textMachine.process(queryString, content), extract)
        # Test
        extract('foot', 'Put one foot in front of the other', 'one foot in f')
        extract('man', 'A man and a woman produced other men and women', 'A man and')
        extract('thinks', 'We are thinking about what we think', 'are thinking abou ... t we think')
        extract('fishes sea', 'Let us go fish in the sea', 's go fish in the sea')

    def testHighlightRelevantText(self):
        # Initialize
        textMachine = query_process.TextMachine(extractLength=0, highlightTemplate='*%s*')
        # Define
        def highlight(queryString, content, extract):
            self.assertEqual(textMachine.process(queryString, content), extract)
        # Test
        highlight('foot', 'Put one foot in front of the other', '*foot*')
        highlight('man', 'A man and a woman produced other men and women', '*man*')
        highlight('thinks', 'We are thinking about what we think', '*thinking* ... *think*')
        highlight('fishes sea', 'Let us go fish in the sea', '*fish* ... *sea*')

    def testProcessRelevantText(self):
        # Initialize
        textMachine = query_process.TextMachine(extractLength=10, highlightTemplate='*%s*')
        # Define
        def process(queryString, content, extract):
            self.assertEqual(textMachine.process(queryString, content), extract)
        # Test
        process('thinks', 'We are thinking about what we think', 'are *thinking* abou ... t we *think*')
        process('foot', 'Put one foot in front of the other', 'one *foot* in f')
        process('man', 'A man and a woman produced other men and women', 'A *man* and')
        process('fishes sea', 'Let us go fish in the sea', 's go *fish* in the *sea*')

# Import system modules
import xapian
import re


pattern_url = re.compile(r'((?:ftp|http|https|gopher|mailto|news|nntp|telnet|wais|file|prospero|aim|webcal):(?:(?:[A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(?:#(?:[a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?(?:[A-Za-z0-9$_+!*();/?:~-]))')


def getQueryParser():
    queryParser = xapian.QueryParser()
    queryParser.set_stemmer(xapian.Stem('english'))
    queryParser.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
    return queryParser


class TextMachine(object):
    
    def __init__(self, highlightTemplate=None, extractLength=None, escape=None, joinText=' ... '):
        self.highlightTemplate = highlightTemplate
        self.extractLength = extractLength
        self.escape = escape
        self.joinText = joinText 

    def process(self, queryString, content):
        # Parse query
        queryParser = getQueryParser()
        query = queryParser.parse_query(queryString)
        # Parse content after replacing non alphanumeric characters with spaces
        queryParser.parse_query(re.sub('\W', ' ', content).lower())
        # Create search pattern
        documentTerms = sum([list(queryParser.unstemlist(x)) for x in set(query)], [])
        if not documentTerms:
            documentTerms = set(query)
        pattern = re.compile(r'\b(%s)\b' % '|'.join(re.escape(x) for x in documentTerms), re.IGNORECASE)
        # If the user does not want to extract text,
        if self.extractLength == None:
            extract = content
        # If the user wants to extract text and there is a queryString,
        elif queryString:
            # Initialize
            extractIntervals = []
            extractLengthHalved = self.extractLength / 2
            # For each matchInterval,
            for match in pattern.finditer(content):
                # Prepare
                mStart = max(0, match.start() - extractLengthHalved)
                mEnd = min(len(content), match.end() + extractLengthHalved)
                # Absorb it
                absorbInterval((mStart, mEnd), extractIntervals)
            # Load extracts
            extract = self.joinText.join(content[eStart:eEnd].strip() for eStart, eEnd in extractIntervals)
        # If the user wants to extract text and there is no queryString,
        else:
            contentLengthHalved = len(content) / 2
            extractLengthHalved = self.extractLength / 2
            extract = content[contentLengthHalved - extractLengthHalved: contentLengthHalved + extractLengthHalved]
        # If the user wants to escape the text,
        if self.escape:
            extract = self.escape(extract)
        # If the user wants to highlight relevant terms and there is a queryString,
        if self.highlightTemplate and queryString:
            extract = pattern.sub(self.highlightTemplate % r'\1', extract)
        # If we are displaying the entire text,
        if self.extractLength == None:
            extract = extract.replace('\n', '<br>')
        # Format hyperlinks
        extract = pattern_url.sub(r'<a href="\1" class=linkOFF>\1</a>', extract)
        # Return
        return extract


def absorbInterval((mStart, mEnd), extractIntervals):
    # For each extractInterval,
    for eIndex, (eStart, eEnd) in enumerate(extractIntervals):
        # If the matchInterval is contained in an existing extractInterval,
        if eStart <= mStart and eEnd >= mEnd:
            # Ignore it because we have it already
            return
        # If the matchInterval overlaps the left side of extractInterval,
        elif mEnd > eStart and mEnd < eEnd:
            # Extend the extractInterval in that direction
            extractIntervals[eIndex] = (mStart, eEnd)
            return
        # If the matchInterval overlaps the right side of extractInterval,
        elif mStart > eStart and mStart < eEnd:
            # Extend the extractInterval in that direction
            extractIntervals[eIndex] = (eStart, mEnd)
            return
    # The matchInterval does not overlap any existing extractInterval
    extractIntervals.append((mStart, mEnd))

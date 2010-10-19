# Import system modules
import datetime
import re
import html2text
import lxml.html
import lxml.html.clean
import lxml.html.html5parser
import lxml.html.soupparser
import warnings
# Import custom modules
import mail_format


# Set patterns for parseHeader
pattern_when = re.compile(r'^Date:(.*)', re.MULTILINE)
patterns_from = [
    re.compile(r'^From:(.*)(?:^Date)', re.MULTILINE|re.DOTALL),
]
patterns_subject = [
    re.compile(r'^Subject:(.*)(?:^To)', re.MULTILINE|re.DOTALL),
    re.compile(r'^Subject:(.*)(?:^CC)', re.MULTILINE|re.DOTALL),
    re.compile(r'^Subject:(.*)(?:^BCC)', re.MULTILINE|re.DOTALL),
    re.compile(r'^Subject:(.*)', re.MULTILINE|re.DOTALL),
]
patterns_to = [
    re.compile(r'^To:(.*)(?:^CC)', re.MULTILINE|re.DOTALL),
    re.compile(r'^To:(.*)(?:^BCC)', re.MULTILINE|re.DOTALL),
    re.compile(r'^To:(.*)', re.MULTILINE|re.DOTALL),
]
patterns_cc = [
    re.compile(r'^CC:(.*)(?:^BCC)', re.MULTILINE|re.DOTALL),
    re.compile(r'^CC:(.*)', re.MULTILINE|re.DOTALL),
]
patterns_bcc = [
    re.compile(r'^BCC:(.*)', re.MULTILINE|re.DOTALL),
]


def parseHeader(header):
    'Parse header as created by mail_format.formatHeader()'
    # Load
    valueByName = {}
    extractString = lambda pattern: pattern.search(header).group(1).strip()
    patternPacks = (
        (patterns_subject, 'subject'),
        (patterns_from, 'fromWhom'),
        (patterns_to, 'toWhom'),
        (patterns_cc, 'ccWhom'),
        (patterns_bcc, 'bccWhom'),
    )
    # Get
    valueByName['when'] = datetime.datetime.strptime(extractString(pattern_when), '%A, %B %d, %Y %I:%M:%S %p')
    for patterns, name in patternPacks:
        for pattern in patterns:
            match = pattern.search(header)
            if match:
                value = match.group(1).strip()
                break
        if not match:
            value = ''
        valueByName[name] = mail_format.unicodeSafely(value)
    # Return
    return valueByName


def stripHTML_html2text(html):
    return html2text.html2text(mail_format.unicodeSafely(html))


def stripHTML_lxml(html):
    html = lxml.html.fromstring(html)
    html = lxml.html.clean.Cleaner(style=True).clean_html(html)
    return renderWithSpaces(html)


def stripHTML_html5lib(html):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        html = lxml.html.html5parser.fromstring(html)
    html = lxml.html.clean.Cleaner(style=True).clean_html(html)
    return renderWithSpaces(html)


def stripHTML_BeautifulSoup(html):
    html = lxml.html.soupparser.fromstring(html)
    html = lxml.html.clean.Cleaner(style=True).clean_html(html)
    return renderWithSpaces(html)


def renderWithSpaces(lxmlDocument):
    for el in lxmlDocument.iter():
        if el.tag == 'br':
            if el.tail and not el.tail.startswith('\n'):
                el.tail = '\n' + el.tail
            else:
                el.tail = '\n'
            el.drop_tag()
        if el.text:
            el.text = ''.join((' ', el.text))
        if el.tail:
            el.tail += ' '
    return lxmlDocument.text_content()


def stripHTML(html):
    # Initialize
    conversionMethodName = None
    methodPacks = [
        ('lxml', stripHTML_lxml),
        ('html5lib', stripHTML_html5lib),
        ('BeautifulSoup', stripHTML_BeautifulSoup),
        ('html2text', stripHTML_html2text),
    ]
    # For each methodPack,
    for methodName, method in methodPacks:
        try:
            html = method(html)
        except:
            pass
        else:
            conversionMethodName = methodName
            break
    # Return
    return mail_format.unicodeSafely(re.sub(r'\s+', ' ', html)), conversionMethodName

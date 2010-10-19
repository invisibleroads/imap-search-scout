Changes in release 0.8
======================
Version 0.8 of TCO Scout was deployed on Thursday, December 10, 2009.


Email search
--------------------------
623. Fix the problem of some messages not being indexed by improving the html to text conversion algorithm using lxml, html5lib, BeautifulSoup, html2text

571. Show results in reverse chronological order when there is a single search term

782. Get rid of query that returns all results because it uses too much memory

778. Display relevant text extracts in search results

821. Add attachment file names to document content so that the file names can be search keywords

89. Add highlighting of keywords in search results

668. Let the user screen for emails containing attachments

670. Let the user screen for emails containing a certain attachment type such as pdf

669. Let the user screen for emails by tag, i.e. in a specific folder


Email browse
--------------------------
247. Show most recent messages on the browse page

822. Let the user browse emails in the database to which he or she has access

90. Let the user browse emails by tag; each email is associated with a set of tags that correspond to the hiearchical tree of folders that contain the message in the user's IMAP account

779. Add better pagination controls, enabling the user to click on arrows to move through pages as well as type the offset directly

811. Let the user view the email header by clicking on the header link


Email management
------------------------------
516. Implement the ability to revive a message with attachments from the database to an IMAP account so that the user can reply to or forward the email using their email client

824. Fix revive so that it revives the message in the logged-in user's mailbox rather than the message owner's mailbox.

506. Add delete feature in web interface so that the user can delete a message permanently


Email archival
----------------------------
239. Archive the inbox more frequently than other folders

91. Fix rule combing so that a message is marked private even if a message contained inside the text of a message contains a matching from, to, cc, bcc, subject, tag; this happens in replied or forwarded mails

216. Make sure Scout doesn't mark emails as read when archiving

279. Write a unit test to make sure that if we save a message, then its read or unread flag is unchanged


Security
--------
244. Add HTTPS security

826. Redirect from HTTP to HTTPS so that transfers are encrypted

505. Add make private feature in web interface so that the user can force messages to be private


Documentation
------------
722. Describe the use of xapian's NEAR and ADJ to search for keywords that are within a specific radius of each other

829. Publish itemized changeset for release 0.8

504. Record tutorial on how to get Sent Items stored via Scout in Outlook, by creating a separate folder visible from the Lotus Notes IMAP interface and then creating a rule in Outlook

310. Make the help text be more applied and specific


Migration
---------
827. Migrate all existing data to the new database


Webhosting
----------
828. Upgrade to Shared 2 plan on WebFaction

Changes in release 0.8.2
========================
Version 0.8.2 of TCO Scout was deployed on Friday, March 12, 2010.


Email browse
--------------------------
- Revised user interface to have preview be on the bottom or on the side
- Added layout button on the lower right for horizontal or vertical layout
- Patched message formatting to enable URL links to be live


Email management
------------------------------
- Restored full text when user clicks on Reply and Forward using AJAX to reduce bandwidth
- Added tooltips to Reply, Forward, Revive, Delete, AttachmentCount
- Fixed bug where messages would not revive properly if the folder exists but is capitalized differently


Email archival
----------------------------
- Patched message numbering system to overcode linux ext3 inode limit using bins
- Patched content archival so that all content is unicoded
- Patched tag archival so that all tags are lowercased
- Fixed issue with duplicate tags because spaces were not being stripped properly


Account management
--------------------------------
- Moved account registration to the People page.


Security
--------
- Replaced filename with fileID in attachment download URL
- Updated authentication code to include recaptcha after multiple failed login attempts


Dependencies
------------
- Upgraded Xapian
- Upgraded lxml
- Upgraded html5lib

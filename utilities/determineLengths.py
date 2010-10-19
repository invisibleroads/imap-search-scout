# Import system modules
import win32com.client
import pywintypes


if __name__ == '__main__':
    # Connect
    application = win32com.client.Dispatch('Outlook.Application')
    namespace = application.GetNamespace('MAPI')
    folders = namespace.Folders
    try:
        folders[0]
    except pywintypes.com_error:
        pass
    else:
        print 'Please run makepy on Microsoft Office 11 Object Library'
        print 'Please run makepy on Microsoft Outlook 11 Object Library'
        sys.exit(-1)
    # Initialize
    nextFolders = [folders[i] for i in xrange(1, len(folders) + 1)]
    subjectLengths = []
    tagLengths = []
    fromLengths = []
    # While there are folders,
    while nextFolders:
        # Initialize
        folder = nextFolders.pop()
        items = folder.Items
        # Append
        tagLengths.append(len(folder.Name))
        # For each item,
        for itemIndex in xrange(1, len(items) + 1):
            item = items[itemIndex]
            subjectLengths.append(len(item.Subject))
            try:
                fromLengths.append(len(item.SenderEmailAddress))
            except AttributeError:
                pass
        # Recurse
        nextFolders.extend([folder.Folders[i] for i in xrange(1, len(folder.Folders) + 1)])
    # Print
    print 'Subject (maximum): %s' % max(subjectLengths)
    print 'Subject (mean): %s' % (sum(subjectLengths) / float(len(subjectLengths)))
    print 'Tag (maximum): %s' % max(tagLengths)
    print 'Tag (mean): %s' % (sum(tagLengths) / float(len(tagLengths)))
    print 'From (maximum): %s' % max(fromLengths)
    print 'From (mean): %s' % (sum(fromLengths) / float(len(fromLengths)))

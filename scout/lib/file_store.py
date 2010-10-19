# Import system modules
import os
# Import custom modules
import store


def binPath(basePath, fileID):
    # Convert to an integer
    fileID = int(fileID)
    # Get the bin number
    binID = fileID / 31993 # Maximum number of subfolders in ext3 is 31998 but allow for 5 extra files
    # Return path
    return os.path.join(store.makeFolderSafely(os.path.join(basePath, str(binID))), str(fileID))


class PathStore(object):

    # Constructor

    def __init__(self, storagePath):
        store.makeFolderSafely(storagePath)
        self.documentBasePath = store.makeFolderSafely(os.path.join(storagePath, 'documents'))
        self.indexBasePath = store.makeFolderSafely(os.path.join(storagePath, 'indices'))
        self.exampleBasePath = store.makeFolderSafely(os.path.join(storagePath, 'examples'))

    # Get

    def getDocumentBasePath(self):
        return self.documentBasePath

    def getIndexBasePath(self):
        return self.indexBasePath

    def getExampleBasePath(self):
        return self.exampleBasePath

    # Fill

    def fillDocumentPath(self, fileID):
        return binPath(self.documentBasePath, fileID)

    def fillExamplePath(self, fileID):
        return binPath(self.exampleBasePath, fileID)

    # Make

    def makeDocumentPath(self, documentID):
        # Set
        documentPath = self.fillDocumentPath(documentID)
        # Remove documentPath if it exists
        store.removeSafely(documentPath)
        # Return documentPath
        return documentPath

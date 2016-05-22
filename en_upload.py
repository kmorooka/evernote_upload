#coding: UTF_8
#--------------------------------------------------------------
# Name: en_upload
# Function: upload all files in specified directory name.
#           Python 2.7 EverNote file attach upload program.
# Usage: >Python en_upload.py /Users/kenjim/dev/evernote/test/ [CR]
#        Need the "/" esparator at the end of directory name.
#--------------------------------------------------------------
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
from evernote.edam.error import ttypes as Errors #This line is doubtful if working is correct or not.
import os, sys, hashlib, mimetypes, binascii

#--------------------------------------------------------------
# set private Evernote Token
#--------------------------------------------------------------
# For Dev env.
# dev_token = “<Insert developer token for sandbox.>”
# For production env.
dev_token = “<Inser developer token for production environment.>”

#--------------------------------------------------------------
# Switch sandbox(True) or real env(False) by flag.
#--------------------------------------------------------------
# client = EvernoteClient(token = dev_token, sandbox = True)
client = EvernoteClient(token = dev_token, sandbox = False)

### debug
# userStore = client.get_user_store()
# user = userStore.getUser()
# print user.username

#--------------------------------------------------------------
# main 
#--------------------------------------------------------------
def main():
    print "=== en_upload: Start."
    param = sys.argv
    dirname = param[1]
    files = os.listdir(dirname)
    for fn in files:
        flist = []
        flist.append(dirname + fn)
        sendNote(fn, flist)
    print "=== en_upload: End.."
#--------------------------------------------------------------
def sendNote(title,filepaths=[]):
    resources = []
    print "=== en_upload: Sending... %s" % title
    for filepath in filepaths:
        resources.append(getResource(filepath))
    makeNote(dev_token, client.get_note_store(), title, "", resources)

#--------------------------------------------------------------
# getResource: get attach file & set evernote attribute
#     return: resource
#--------------------------------------------------------------
def getResource(filepath):
    filename = os.path.basename(filepath)
    data = Types.Data()
    data.body = open(filepath, 'r').read()
    data.size = len(data.body)
    data.bodyHash = hashlib.md5(data.body).hexdigest()
    resource = Types.Resource()
    resource.mime = mimetypes.guess_type(filename)[0]
    resource.data = data
    attr = Types.ResourceAttributes()
    attr.fileName = filename
    resource.attributes = attr
    # print('attachment: ' + filename)
    return resource

#--------------------------------------------------------------
# makeNote: set evernote attribute & upload 
#     return: note
#     Line35 is modified from official sample code
#--------------------------------------------------------------
def makeNote(authToken, noteStore, noteTitle, noteBody, resources=[], parentNotebook=None):
        """
        Create a Note instance with title and body
        Send Note object to user's account
        """
        ourNote = Types.Note()
        ourNote.title = noteTitle

        ## Build body of note
        nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
        nBody += "<en-note>%s" % noteBody
        if resources:
                ### Add Resource objects to note body
                nBody += "<br />" * 2
                ourNote.resources = resources
                for resource in resources:
                        # morooka hexhash = binascii.hexlify(resource.data.bodyHash)
                        hexhash = resource.data.bodyHash
                        nBody += "<en-media type=\"%s\" hash=\"%s\" /><br />" % \
                                (resource.mime, hexhash)
        nBody += "</en-note>"

        ourNote.content = nBody
        # print nBody

        ## parentNotebook is optional; if omitted, default notebook is used
        if parentNotebook and hasattr(parentNotebook, 'guid'):
                ourNote.notebookGuid = parentNotebook.guid

        ## Attempt to create note in Evernote account
        try:
                # print('Sending...')
                note = noteStore.createNote(authToken, ourNote)
                # print('Sent.')
        except Errors.EDAMUserException, edue:
                ## Something was wrong with the note data
                ## See EDAMErrorCode enumeration for error code explanation
                ## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
                print "EDAMUserException:", edue
                return None
        except Errors.EDAMNotFoundException, endfe:
                ## Parent Notebook GUID doesn't correspond to an actual notebook
                print "EDAMNotFoundException: Invalid parent notebook GUID"
                return None
        ## Return created note object
        return note
#--------------------------------------------------------------
# Run as script
#--------------------------------------------------------------
if __name__ == '__main__':
    main()

#--------------------------------------------------------------
# End of File
#--------------------------------------------------------------

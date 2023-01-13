import boto3, pyinotify
import os #access directories on laptop
from pathlib import Path

client = boto3.client('s3')
path = '/home/jim/Desktop/tobeuploaded/' #path of the directory to be synced

#uploading to s3
def sync_whole_dir():
    for file in os.listdir(path): 
        upload_file_bucket = 'filesyncc'
        upload_file_key = get_sorted_path(file)
        client.upload_file(path+file,upload_file_bucket,upload_file_key)

def sync_file(file):
    upload_file_bucket = 'filesyncc'
    upload_file_key = get_sorted_path(file)
    client.upload_file(path+file,upload_file_bucket,upload_file_key)

def get_sorted_path(file):
    if '.py' in file:
            upload_file_key = 'python/' + str(file)

    elif '.txt' in file:
        upload_file_key = 'text/' + str(file)

    elif '.pdf' in file:
        upload_file_key = 'pdf/' + str(file)

    elif '.doc' in file or '.docx' in file:
        upload_file_key = 'word_doc/' + str(file)
    
    else:
        upload_file_key = 'other/' + str(file)
    
    return upload_file_key


sync_whole_dir()
print("Syncing the whole directory", path, "to s3.")


# watch the folder for changes using pyinotify
# The watch manager stores the watches and provides operations on watches
wm = pyinotify.WatchManager()

mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events

class EventHandler(pyinotify.ProcessEvent): #The EventHandler class inherits from a processing base class called ProcessEvent; it handles notifications and takes actions through specific processing methods. For an EVENT_TYPE, a process_EVENT_TYPE function will execute. 
    def process_IN_CREATE(self, event):
        print("Creating", event.pathname, "and syncing to s3")
        sync_file(Path(str(event.pathname)).name)

    def process_IN_DELETE(self, event):
        print("Removing", event.pathname)

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(path, mask, rec=True)

notifier.loop()





"""
next steps:
make it auto-detect new files added
should it delete deleted local files?

sync edited files

make it recognize folders and loop through them

"""

import boto3
import os #access directories on laptop
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path


client = boto3.client('s3')
path = '/home/jim/ws/tobeuploaded/' #path of the directory to be synced
bucket_name = 'filesyncc'

#uploading to s3
def sync_whole_dir():
    for file in os.listdir(path): 
        upload_file_key = get_sorted_path(file)
        client.upload_file(path+file,bucket_name,upload_file_key)

def sync_file(file):
    upload_file_key = get_sorted_path(file)
    client.upload_file(path+file,bucket_name,upload_file_key)

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


#monitoring files

class ChangeHandler(FileSystemEventHandler): #event handler that takes action when an event is received
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            print("Hey,", Path(str(event.src_path)).name, "has been", event.event_type, "in",event.src_path, "!\nUploading to ", bucket_name)
            sync_file(Path(str(event.src_path)).name)

        elif event.event_type == 'modified':
            print("Hey,", Path(str(event.src_path)).name, "has been", event.event_type, "!\nSyncing changes to ",bucket_name)
            sync_file(Path(str(event.src_path)).name)

        elif event.event_type == 'deleted':
            print("Hey,", event.src_path, "has been", event.event_type, "!\nDeleting from ",bucket_name)
        
        else:
            return None
    
class OnMyWatch:
    # Set the directory on watch
    watchDirectory = path
  
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        event_handler = ChangeHandler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        print("Started monitoring")
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")
  
        self.observer.join()


if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
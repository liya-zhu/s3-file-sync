import boto3
import os #access directories on laptop
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path
from botocore.exceptions import ClientError



client = boto3.client('s3')
path = "" # path of the directory to be synced
bucket_name = "" #s3 bucket name
phone_num = "" # receiver's number
sns = boto3.resource('sns')

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
        messenger = SnsWrapper(sns)
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            message = "Hey,"+ Path(str(event.src_path)).name +"has been"+ event.event_type+ "in" + event.src_path + "!\nUploading to "+ bucket_name
            messenger.publish_text_message(phone_num,message)
            
            sync_file(Path(str(event.src_path)).name)

        elif event.event_type == 'modified':
            message = "Hey,"+ Path(str(event.src_path)).name + "has been"+ event.event_type + "!\nSyncing changes to " + bucket_name
            messenger.publish_text_message(phone_num,message)
            sync_file(Path(str(event.src_path)).name)

        elif event.event_type == 'deleted':
            message = "Hey,"+ event.src_path + "has been" + event.event_type + "!\nDeleting from "+ bucket_name
            messenger.publish_text_message(phone_num,message)
        
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

#A topic is a message channel. When you publish a message to a topic, it fans out the message to all subscribed endpoints.
class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""
    def __init__(self, sns_resource):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        self.sns_resource = sns_resource

    def publish_text_message(self, phone_number, message):
        """
        Publishes a text message directly to a phone number without need for a
        subscription.

        :param phone_number: The phone number that receives the message. This must be
                             in E.164 format. For example, a United States phone
                             number might be +12065550101.
        :param message: The message to send.
        :return: The ID of the message.
        """
        try:
            response = self.sns_resource.meta.client.publish(
                PhoneNumber=phone_number, Message=message)
            message_id = response['MessageId']
            print("Published message to %s.", phone_number)
        except ClientError:
            print("Couldn't publish message to %s.", phone_number)
            raise
        else:
            return message_id



if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
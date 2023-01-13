from secret import access_key, secret_access_key

import boto3
import os #access directories on laptop

client = boto3.client('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_access_key)

for file in os.listdir(): #all files in same working dir

    upload_file_bucket = 'filesyncc'

    if '.py' in file:
        upload_file_key = 'python/' + str(file)
        client.upload_file(file,upload_file_bucket,upload_file_key)

    elif '.txt' in file:
        upload_file_key = 'text/' + str(file)
        client.upload_file(file,upload_file_bucket,upload_file_key)

    elif '.pdf' in file:
        upload_file_key = 'pdf/' + str(file)
        client.upload_file(file,upload_file_bucket,upload_file_key)

    elif '.doc' in file or '.docx' in file:
        upload_file_key = 'word_doc/' + str(file)
        client.upload_file(file,upload_file_bucket,upload_file_key)
    
    else:
        upload_file_key = 'other/' + str(file)
        client.upload_file(file,upload_file_bucket,upload_file_key)

import json
import boto3
import uuid
from dotenv import load_dotenv
import json

from src.logging_util import logger

load_dotenv()

def getMetrics(input):
    f = open("metrics.txt", "w")
    f.write( 'dict = ' + repr(input) + '\n' )
    f.close()
    file_name = 'feedback/'+"metrics.txt"
    bucket_name = 'ml-recommendation-capstone'
    s3 = boto3.client('s3')
    try:
        # Upload the JSON file to the S3 bucket
        file_name = f"metrics_{str(uuid.uuid4())}.txt"
        s3.upload_file("metrics.txt", Bucket=bucket_name, Key=file_name)
        return {
            'statusCode': 200,
            'body': f'File {file_name} successfully uploaded to {bucket_name}'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
            }

def getRatings(input):
    json_data = json.dumps(input, indent=4)
    file_name = 'feedback/'+str(uuid.uuid4()) + ".json"
    bucket_name = 'ml-recommendation-capstone'
    s3 = boto3.client('s3')
    try:
        # Upload the JSON file to the S3 bucket
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=json_data)
        return {
            'statusCode': 200,
            'body': f'File {file_name} successfully uploaded to {bucket_name}'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
            }
    
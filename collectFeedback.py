import json
import boto3
import uuid
import os
from dotenv import load_dotenv
import logging

session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="")

def getMetrics(input):
    print(input)
    # ctr = input[0]
    # mrr = input[1:]
    f = open("metrics.txt", "w")
    # f.write("Conversion Rate:")
    f.write( 'dict = ' + repr(input) + '\n' )
    # json.dump(input, indent=4)
    # f.write("Mean Reciprocal Rank:")
    # f.write(mrr)
    f.close()
    
    
    # return 'Working'
    # json_data = json.dumps(input, indent=4)
    file_name = 'feedback/'+"metrics.txt"
    bucket_name = 'ml-recommendation-capstone'
    s3 = session.client('s3')
    
    try:
        # Upload the JSON file to the S3 bucket
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
    # return 'Working2'

def getRatings(input):
    
    
    # return 'Working'
    json_data = json.dumps(input, indent=4)
    file_name = 'feedback/'+str(uuid.uuid4()) + ".json"
    bucket_name = 'ml-recommendation-capstone'
    s3 = session.client('s3')
    
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
    

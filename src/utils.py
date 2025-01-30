from pathlib import Path
import yaml
from box import ConfigBox
from box.exceptions import BoxValueError
import os
import boto3
from dotenv import load_dotenv

from src.logging_util import logger

load_dotenv()

# Initialize a session using credentials from environment variables
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    # aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: ConfigBox type
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e

def create_folder_from_config(config_path: Path):
    """Creates a folder from the path specified in the config file

    Args:
        config_path (Path): Path to the config file
    """
    config = read_yaml(config_path)
    folder_path = config.get("model_trainer").get("root_dir")

    if folder_path:
        os.makedirs(folder_path, exist_ok=True)
        logger.info(f"Folder created at: {folder_path}")
        return folder_path
    else:
        logger.error("No folder path specified in the config file")

def download_file_from_s3(bucket_name:str, file_name:str, download_path:str, job_id:str=None, folder_name:str=None,):
    """
    Downloads a file from an S3 bucket inside a folder named after the job ID,
    which contains another folder named after the folder name.

    Args:
        bucket_name (str): The name of the S3 bucket.
        job_id (str): The job ID used as the parent folder name.
        folder_name (str): The folder name inside the job ID folder.
        file_name (str): The name of the file to be downloaded.
        download_path (str): The local path where the file will be saved.

    Returns:
        str: The local path to the downloaded file.
    """
    # Initialize the S3 client
    s3_client = boto3.client('s3')

    # Construct the S3 object key
    if job_id:
        object_key = f"{job_id}/{folder_name}/{file_name}"
    else:
        object_key = f"{file_name}"

    try:
        # object_key = 
        # Download the file from S3
        logger.info(f"starting to download: {object_key}")
        s3_client.download_file(bucket_name, object_key, f"{download_path}")
        logger.info(f"File {file_name} downloaded from s3://{bucket_name}/{object_key} to {download_path}")

        # Return the local path to the downloaded file
        return download_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        raise

def download_s3_folder(bucket_name: str, s3_folder: str, local_dir: str):
    """Downloads all files from a folder in an S3 bucket to a local directory

    Args:
        bucket_name (str): Name of the S3 bucket
        s3_folder (str): Folder path in the S3 bucket
        local_dir (str): Local directory to download files to
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_folder)
    

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                s3_key = obj['Key']
                local_file_path = os.path.join(local_dir, os.path.relpath(s3_key, s3_folder))
                local_file_dir = os.path.dirname(local_file_path)

                if not os.path.exists(local_file_dir):
                    os.makedirs(local_file_dir)

                s3.download_file(bucket_name, s3_key, local_file_path)
                logger.info(f"Downloaded {s3_key} to {local_file_path}")
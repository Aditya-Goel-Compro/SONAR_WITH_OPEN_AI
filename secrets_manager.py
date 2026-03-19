import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_NAME = os.getenv("SECRET_NAME")


def get_secret():
   
    session = boto3.Session(
        profile_name="AWS-Training-Account-Cred",
        region_name="ap-south-1"
    )

    print("Secret name:", SECRET_NAME)

    client = session.client("secretsmanager")

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    secret = response["SecretString"]

    return json.loads(secret)
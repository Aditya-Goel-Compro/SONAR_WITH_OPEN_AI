import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv("AWS_REGION")
SECRET_NAME = os.getenv("SECRET_NAME")


def get_secret():

    print("Using AWS profile:", AWS_PROFILE)
    print("AWS region:", AWS_REGION)
    print("Secret name:", SECRET_NAME)

    session = boto3.Session(
        profile_name="AWS-Training-Account-Cred",
        region_name="ap-south-1"
    )

    print("Using AWS profile:", AWS_PROFILE)
    print("AWS region:", AWS_REGION)
    print("Secret name:", SECRET_NAME)


    client = session.client("secretsmanager")

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    secret = response["SecretString"]

    return json.loads(secret)
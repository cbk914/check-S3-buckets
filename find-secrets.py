import boto3
import os
import re
import argparse
import psutil
from tqdm import tqdm

# Create an S3 client
s3 = boto3.client('s3')

# List of regular expressions to match against
secrets = [
r'(?i)access_?key',
r'(?i)access_?token',
r'(?i)api_?key',
r'(?i)client_?id',
r'(?i)client_?secret',
r'(?i)credentials',
r'(?i)certificate',
r'(?i)dsa',
r'(?i)email',
r'(?i)encryption',
r'(?i)2fa',
r'(?i)mfa',
r'(?i)hashed_?password',
r'(?i)jwt',
r'(?i)md5',
r'(?i)nonce',
r'(?i)otp',
r'(?i)pgp',
r'(?i)password',
r'(?i)private_?key',
r'(?i)rsa',
r'(?i)salt',
r'(?i)secret',
r'(?i)secret_?key',
r'(?i)security',
r'(?i)sha1',
r'(?i)sha256',
r'(?i)ssh',
r'(?i)ssl',
r'(?i)token',
r'(?i)username',
r'(?i)user_?name'
]
# Create an argument parser
parser = argparse.ArgumentParser()

# Add -r option to allow for manual input of regular expressions
parser.add_argument('-r', '--regex', help='Regular expression to include in search')

# Parse the arguments
args = parser.parse_args()

if args.regex:
    secrets.append(args.regex)

# Get a list of all S3 buckets
response = s3.list_buckets()
buckets = [bucket['Name'] for bucket in response['Buckets']]

# Get the total size of all objects in all buckets
total_size = 0
for bucket in buckets:
    paginator = s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket):
        for obj in result.get('Contents', []):
            total_size += obj['Size']

# Function to check if there is enough disk space for the objects
def check_disk_space(bucket_name):
    # Get the total size of all objects in the bucket
    result = s3.list_objects_v2(Bucket=bucket_name)
    total_size = sum(int(item['Size']) for item in result.get("Contents", []))
    # Get the amount of free space on the local disk
    free_space = psutil.disk_usage("/").free
    # Check if there is enough free space
    if total_size > free_space:
        print(f"There is not enough free space on the local disk to download the objects from {bucket_name}. The total size of the objects is {total_size / (1024 ** 3):.2f} GB and the amount of free space is {free_space / (1024 ** 3):.2f} GB.")
        proceed = input("Do you want to proceed? (y/n)")
        if proceed.lower() != "y":
            return False
    return True

# Create a secrets.txt file for storing found secrets
with open('secrets.txt', 'w') as secrets_file:
    # Iterate through each bucket
    for bucket in tqdm(buckets):
        # Use the boto3 paginator to handle pagination for the list_objects_v2 method
        paginator = s3.get_paginator('list_objects_v2')
        for result in paginator.paginate(Bucket=bucket):
            for obj in result.get('Contents', []):
            # Download the object from S3
            s3.download_file(bucket, obj['Key'], obj['Key'])
            # Open the downloaded object
            with open(obj['Key'], 'r') as f:
                content = f.read()
                # Search for secrets in the object's content
                for secret in secrets:
                    if re.search(secret, content):
                        print(f'Found {secret} in {obj["Key"]}')
                        with open("secrets.txt", "a") as f:
                        f.write(f'Found {secret} in {obj["Key"]}\n')
            # Remove the downloaded object after searching its content
            os.remove(obj['Key'])

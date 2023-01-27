import argparse
import boto3
import re
import requests

def check_bucket_objects(bucket_name, region_code, key_name, proxy=None):
    bucket_name = re.sub('[^0-9a-zA-Z-]', '', bucket_name)
    region_code = re.sub('[^0-9a-zA-Z-]', '', region_code)
    key_name = re.sub('[^0-9a-zA-Z-._]', '', key_name)
    s3 = boto3.client('s3', region_name=region_code)
    try:
        s3.head_object(Bucket=bucket_name, Key=key_name)
        url = f'https://{bucket_name}.s3.{region_code}.amazonaws.com/{key_name}'
        if proxy is not None:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            response = requests.get(url, proxies=proxies)
        else:
            response = requests.get(url)
        print(f'{key_name} exists in bucket {bucket_name} and the url is {url}')
    except s3.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f'{key_name} does not exist in bucket {bucket_name}')
        else:
            raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check S3 bucket objects')
    parser.add_argument('-f', '--file', dest='file_name', required=True, help='File with key names list')
    parser.add_argument('-r', '--region', dest='region_code', required=True, help='Region code')
    parser.add_argument('-b', '--bucket', dest='bucket_name', required=True, help='Bucket name')
    parser.add_argument('-p', '--proxy', dest='proxy', required=False, help='Proxy server')
    args = parser.parse_args()
    # Sanitize input
    args.file_name = re.sub(r'[^0-9a-zA-Z-]', '', args.file_name)
    args.region_code = re.sub(r'[^0-9a-zA-Z-]', '', args.region_code)
    args.bucket_name = re.sub(r'[^0-9a-zA-Z-]', '', args.bucket_name)
    if args.proxy:
        args.proxy = re.sub(r'[^0-9a-zA-Z-]', '', args.proxy)
    with open(args.file_name, 'r') as f:
        key_names = f.read().splitlines()
        for key_name in key_names:
            if not all(x.isalnum() or x.isspace() or x in string.punctuation for x in key_name):
                print(f'{key_name} contains invalid characters. Skipping.')
                continue
            if args.proxy:
                if not all(x.isalnum() or x.isspace() or x in string.punctuation for x in args.proxy):
                    print(f'{args.proxy} contains invalid characters. Skipping.')
                    continue
                check_bucket_objects(args.bucket_name, args.region_code, key_name, args.proxy)
            else:
                check_bucket_objects(args.bucket_name, args.region_code, key_name)

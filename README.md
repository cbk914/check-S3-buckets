# check-S3-buckets

# Installation

* Install boto3, argparse, and requests by running the following command:

  pip install boto3 argparse requests

* Create a file containing the list of key names you want to check, with one key name per line. Let's call this file keys.txt for the purpose of these instructions.
* Set up your AWS credentials, this can be done by creating a new IAM user with programmatic access and s3 read access and configure the credentials in your local machine by following the instructions in this link https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
* Set up your proxy server, For example if you are using Burp Suite, you need to configure it to listen on the right interface, and configure the proxy settings in your script accordingly.
* Run the script by providing the appropriate values for the command-line arguments.

  python check-s3-buckets.py -f keys.txt -r us-west-2 -b my-bucket -p http://proxy_ip:proxy_port

* You can replace us-west-2 with the appropriate region code for your S3 bucket, and my-bucket with the actual name of your S3 bucket. Also replace the proxy_ip and proxy_port with the actual values of your proxy server.

* The script will check each key name in the keys.txt file, send the request for each object through the specified proxy and print the url of the object if it exists and print the error if the object doesn't exist.

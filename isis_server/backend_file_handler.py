import json
import requests
import boto3

# general idea for communication between front and back ends
    # 1. n8n sends url to backend
    # 2. backend downloads file at url
    # 3. backend pushes file to s3
    # 4. backend responds to n8n with s3 url of pushed file


def get_file_from_url(input_data):
    # go through input to find url and save as variable
    parsed_json = json.loads(input_data)
    url = parsed_json['from']['type']

    # use url in request code to get back json
    r = request.get(url)
    r.status_code
    r.headers['content-type']
    r.encoding
    r.text
    json_output = r.json()
    
    # return json
    return json_output
 
    
# ask about where we're getting the bucket name from
def push_to_s3(img_file, bucket_name):
    # connect to s3
    s3_connection = boto.connect_s3()
    
    # establish bucket
    bucket = s3_connection.get_bucket(bucket_name)
    
    # create key
    key = boto.s3.key.Key(bucket, img_file)
    
    # use key to send file
    with open(img_file) as f:
        key.send_file(f)
    
    
# need to format response as done in discord example    
def respond_to_n8n(img_file, bucket_name):
    # initialize client and resource
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    
    # create bucket
    bucket = s3_resource.Bucket(bucket_name)
    
    # find file in bucket and grab its url
    for current_file in bucket.objects.all():
        if current_file == img_file:
            params = {'Bucket': bucket_name, 'Key': current_file.key}
            url = s3_client.generate_presigned_url('get_object', params)
    
    # return formatted data
        # return url
        # return
            ''' {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string"
                },
                "error": {
                    "type": "string"
                }
            }
            }'''
            
    to_return_dict = {}
    to_return_dict["type"] = url
    
    error_return_dict = {}
    error_return_dict["type"] = "string"
    
    properties_return_dict = {}
    properties_return_dict["to"] = to_return_dict
    properties_return_dict["error" = error_return_dict

    return_dict = {}
    return_dict["type"] = "object"
    return_dict["properties"] = properties_return_dict
    

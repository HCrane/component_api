import json
import logging
from os import environ
import helper

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)



# client_s3 = boto3.resource("s3")
# bucket_s3 = client_s3.Bucket(environ.get("S3_BUCKET_NAME"))



def lambda_handler(event, context):

    image_hash = event.get("pathParameters").get("hash")
    image_flag, image_prediction = helper.check_img_exists(hash=image_hash)
    if image_flag:
        return{
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Image found in DB",
                    "prediction": [image_prediction],
                }
            ),
        }
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Image not found in DB",
                "prediction" : []
            }
        ),
    }

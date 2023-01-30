import logging
from os import environ

from typing import Tuple

import boto3


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def check_img_exists(hash:str) -> Tuple[bool, str]:
    """Function to check if image is in db

    :param hash: Crop resistant hash
    :type hash: str
    :return: Boolean, return True if exists else False
    :rtype: bool
    """
    client_dynamodb = boto3.client("dynamodb")
    response = client_dynamodb.get_item(
        TableName=environ.get("TABLE_NAME"),
        Key={
            "id": {
                "S": hash,
            }
        }
    )
    LOGGER.warning(response)
    if "Item" in response:
        resp_dict = {}
        resp_dict["id"] = response["Item"].get("id").get("S")
        resp_dict["classified_at"] = response["Item"].get("classified_at").get("N")
        resp_dict["prediction"] = {
            "neutral": float(response["Item"].get("prediction").get("M").get("neutral").get("N")),
            "porn": float(response["Item"].get("prediction").get("M").get("porn").get("N")),
            "simulated": float(response["Item"].get("prediction").get("M").get("simulated").get("N")),
            "suggestive": float(response["Item"].get("prediction").get("M").get("suggestive").get("N")),
        }
        return (True, resp_dict)
    return (False, "")
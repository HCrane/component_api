import base64
from io import BytesIO
import logging
from os import environ
from pathlib import Path

from typing import Tuple
from uuid import uuid4
from imagehash import crop_resistant_hash
import boto3
from PIL import Image
import datetime


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
    LOGGER.info(response)
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
  

def save_img_temp(image:bytes) -> Path:
    """Save img to tmp folder

    :param image: image in base64 encoded
    :type image: bytes
    :return: pathlib.Path to image
    :rtype: Path
    """
    image_bytes = image.encode("utf-8")
    with Image.open(BytesIO(base64.b64decode(image_bytes))).convert(mode="L") as image:
        image = image.resize((300, 300))
        filename = uuid4()
        path = Path(f"/tmp/{filename}.jpeg")
        image.convert("RGB")
        image.save(path, "JPEG", icc_profile=image.info.get("icc_profile"), quality=75)
        return path

def get_crop_hash(filepath:Path) -> str:
  """Get crop resistant hash for given image

  :param filepath: path to image
  :type filepath: str
  :return: String representation of ImageHash
  :rtype: str
  """
  crop_hash = crop_resistant_hash(
    Image.open(filepath), 
    min_segment_size=500
  )
  return str(crop_hash)

def dict_to_db_map(dict: dict) -> dict:
  """Converts given dict to M dynamodb type

  :param dict: dict to convert
  :type dict: dict
  :return: dict to insert
  :rtype: dict
  """
  ret_dict = {}
  
  for key in dict:
    ret_dict[key] = {"N": str(dict.get(key))}
  return ret_dict

def insert_dynamodb(
    hash:str,
    prediction: dict    
):
    """Function to insert hasha nd prediction into lookup DB

    :param hash: Crop Resistant hash
    :type hash: str
    :param prediction: Dict of predictions
    :type prediction: dict
    :return: _description_
    :rtype: _type_
    """
    client_dynamodb = boto3.client("dynamodb")
    
    presentDate = datetime.datetime.utcnow()
    unix_timestamp = int(round(datetime.datetime.timestamp(presentDate)))
    try:
        response = client_dynamodb.put_item(
            TableName=environ.get("TABLE_NAME"),
            Item={
                "id": {"S": hash},
                "prediction": {"M": dict_to_db_map(prediction)},
                "classified_at": {"N": str(unix_timestamp)}
            }
        )
    except Exception as err:
        LOGGER.warning(err)
        return False
    return True
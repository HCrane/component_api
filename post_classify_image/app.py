import json
import logging
import helper


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def lambda_handler(event, context):
    LOGGER.info(event)
    # try:
    image_path = helper.save_img_temp(event["body"])
    image_hash = helper.get_crop_hash(image_path)
    image_exists, prediction = helper.check_img_exists(image_hash)
    if image_exists:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Image fund in DB, no reclassification taken.",
                    "exists_in_db": True,
                    "prediction": [prediction],
                }
            )
        }
    
    import numpy as np
    import tensorflow as tf

    model_file = "/opt/ml/model.h5"
    model = tf.keras.models.load_model(model_file)
    image = tf.keras.preprocessing.image.load_img(path=image_path, target_size=(300, 300), color_mode="grayscale")
    img = np.array(image)
    img = img / 255.0
    img = img.reshape(-1,300,300,1)
    classes = ['neutral', 'porn', 'simulated', 'suggestive']
    
    prediction_model = model.predict(img)
    prediction_perc = prediction_model.tolist()[0]
    LOGGER.info(prediction_perc)
    prediction_dict = {}
    for entry, value in zip(classes, prediction_perc):
        prediction_dict[entry] = round(value * 100, 4)
    
    # Redo because classification takes time
    image_exists, prediction = helper.check_img_exists(image_hash)
    if image_exists:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Image fund in DB, no reclassification taken.",
                    "exists_in_db": True,
                    "prediction": [prediction],
                }
            )
        }
    
    if helper.insert_dynamodb(image_hash, prediction_dict):
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Image newly classified and imagehash saved in lookup DB.",
                    "exists_in_db": False,
                    "prediction": [prediction_dict],
                }
            )
        }
    # except Exception as error:
    #     LOGGER.warning(f"Something went very wrong!")
    #     LOGGER.warning(error)
    return {
        "statusCode": 500,
        "body": json.dumps(
            {
                "message": "An error occoured! Check Cloudwatch logs.",
                "exists_in_db": False,
                "prediction": [],
            }
        )
    }


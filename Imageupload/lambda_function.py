import json
import numpy as np
import cv2
import boto3
import uuid

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
TABLE_NAME = 'image_tag_url'
image_bucket = 'detect123'
yolo_bucket = 'detectconfig'
CONFIDENCE_THRESHOLD = 0.6


def get_labels(labels_path):
    response = s3.get_object(
        Bucket=yolo_bucket,
        Key=labels_path
    )
    LABELS = response['Body'].read().decode('utf-8').strip().split("\n")
    return LABELS


def get_weights(weights_path):
    response = s3.get_object(
        Bucket=yolo_bucket,
        Key=weights_path
    )
    WEIGHTS = response['Body'].read()
    return WEIGHTS


def get_config(config_path):
    response = s3.get_object(
        Bucket=yolo_bucket,
        Key=config_path
    )
    CONFIG = response['Body'].read()
    return CONFIG


def load_model(config_path, weights_path):
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    return net


def detect_objects(image):
    (H, W) = image.shape[:2]
    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    boxes = []
    confidences = []
    classIDs = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > CONFIDENCE_THRESHOLD:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, 0.3)

    detected_objects = []
    for i in indices:
        i = i[0]
        label = LABELS[classIDs[i]]
        confidence = confidences[i]
        detected_objects.append({"label": label, "confidence": confidence})

    return detected_objects


def lambda_handler(event, context):
    global net, LABELS, output_layers
    if not ('net' in globals() and 'LABELS' in globals() and 'output_layers' in globals()):
        LABELS = get_labels('coco.names')
        net = load_model(get_config('yolov3-tiny.cfg'), get_weights('yolov3-tiny.weights'))
        output_layers = net.getUnconnectedOutLayersNames()

    records = event['Records']
    for record in records:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )
        image_content = response['Body'].read()

        image = cv2.imdecode(np.frombuffer(image_content, np.uint8), cv2.IMREAD_COLOR)
        detected_objects = detect_objects(image)

        tags = [obj['label'] for obj in detected_objects]
        s3_url = f"https://{bucket}.s3.amazonaws.com/{key}"
        item_id = str(uuid.uuid4())

        item = {
            'id': {'S': item_id},
            'tags': {'L': [{'S': tag} for tag in tags]},
            's3-url': {'S': s3_url}
        }

        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing completed successfully.'})
    }

import json
import base64
import boto3
import numpy as np
import cv2
import os
import urllib.parse
import time
import uuid 

# Path for YOLO configuration files in Lambda Layer
yolo_path = "/opt/yolo_tiny_configs"

def get_labels(labels_path):
    LABELS = open(labels_path).read().strip().split("\n")
    return LABELS

def load_model(config_path, weights_path):
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    return net

def do_prediction(image, net, LABELS):
    (H, W) = image.shape[:2]
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

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

            if confidence > confthres:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres, nmsthres)
    
    result = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            result.append({
                "label": LABELS[classIDs[i]],
                "accuracy": confidences[i],
                "rectangle": {
                    "left": boxes[i][0],
                    "top": boxes[i][1],
                    "width": boxes[i][2],
                    "height": boxes[i][3]
                }
            })
    return result

# Paths for YOLO configuration files
labelsPath = os.path.join(yolo_path, "coco.names")
cfgPath = os.path.join(yolo_path, "yolov3-tiny.cfg")
weightsPath = os.path.join(yolo_path, "yolov3-tiny.weights")

# Load YOLO model
LABELS = get_labels(labelsPath)
net = load_model(cfgPath, weightsPath)
confthres = 0.3
nmsthres = 0.1

# Initialize S3 client
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    detection_results = []
    start_time = time.time()
    
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Decode the key
            key = urllib.parse.unquote(key)
            print(f"Decoded S3 key: {key}")
            s3_time = time.time()
            
            # Get the image from S3
            s3_response = s3.get_object(Bucket=bucket, Key=key)
            image_data = s3_response['Body'].read()
            
            # Decode the image
            nparr = np.frombuffer(image_data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            image_decode_time = time.time()

            # Perform object detection
            prediction_res = do_prediction(img_np, net, LABELS)
            detection_time = time.time()
            
            detection_results.append({
                "image": key,
                "detections": prediction_res
            })
            
            # Generate UUID for the image
            image_uuid = str(uuid.uuid4())
            
            # Construct the S3 URL
            s3_url = f"https://{bucket}.s3.amazonaws.com/{key}"
            
            # Extract labels from prediction results
            tags = [pred['label'] for pred in prediction_res]
            
            # Get metadata
            metadata = s3_response.get('Metadata', {})
            username = metadata.get('username')
            
            # Save detections to DynamoDB
            dynamodb.put_item(
                TableName='ImageLabels', # dynamodb table name
                Item={
                    'ImageKey': {'S': image_uuid}, 
                    'S3URL': {'S': s3_url},
                    'S3Path': {'S': key},
                    'Tags': {'S': json.dumps(tags)},
                    'UserName': {'S': username}
                }
            )

            print(f"Detected objects for image {key}: {json.dumps(prediction_res)}")
            print(f"Time to get image from S3: {s3_time - start_time}")
            print(f"Time to decode image: {image_decode_time - s3_time}")
            print(f"Time to perform detection: {detection_time - image_decode_time}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Object detection completed successfully!',
                'results': detection_results
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing image',
                'error': str(e)
            })
        }

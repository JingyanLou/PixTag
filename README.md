# PixTag: An AWS-powered Serverless Image Storage System

## Project Overview

PixTag is an AWS-based online system that allows users to upload images and perform object detection. The detected tags and image information are stored in DynamoDB. Users can query for specific images by tag, search for images based on tags, update or delete tags in DynamoDB, and subscribe to specific tags. When an image with a subscribed tag is added or updated, users receive email notifications. The application leverages AWS services such as S3, Lambda, API Gateway, DynamoDB, and SNS to provide a seamless experience for image management and retrieval.

## Features

- Upload images to S3 and automatically generate tags using object detection(yolo).
- Store image metadata and tags in DynamoDB.
- Query images based on tags via API Gateway.
- Find images based on the thumbnail’s url.
- Find images based on the tags of an image.
- Manual addition or removal of tags with bulk tagging.
- Subscribe to specific tags to receive notifications when new images with those tags are added.
- Unsubscribe to specific tags to stop receiving notification
- User authtication using AWS Cognito.
- User registeration using AWS Cognito.


## System Diagram

Here is the system diagram:

![systemdiagramnew](https://github.com/JingyanLou/PixTag/assets/92469426/55847664-6c1e-4801-9f86-80de84314f9b)

## User Interface

### Login
![WechatIMG155](https://github.com/JingyanLou/PixTag/assets/92469426/d4036dd1-3066-49a5-9c47-3eb9e43ef972
### Registeration
![WechatIMG156](https://github.com/JingyanLou/PixTag/assets/92469426/42e1a8d4-7998-4b34-8300-0e3029dee8a8)
### Upload image
![WechatIMG157](https://github.com/JingyanLou/PixTag/assets/92469426/beedd202-6082-4f09-82d8-a04f347111f7)
### Tag subscribe
![WechatIMG158](https://github.com/JingyanLou/PixTag/assets/92469426/a3b0046d-450c-4b46-8463-f3d16890c2cd)
### Update tags/Delete tags
![WechatIMG159](https://github.com/JingyanLou/PixTag/assets/92469426/2050dc26-da34-426a-862c-e95e7422c452)
### Search by tags
![WechatIMG160](https://github.com/JingyanLou/PixTag/assets/92469426/2b130f99-0646-492c-bb24-2290342fa886)
### Search by url
![WechatIMG161](https://github.com/JingyanLou/PixTag/assets/92469426/f46cc47c-24f4-4485-9f54-a6ad64687545)
### Find Similar Images
![WechatIMG162](https://github.com/JingyanLou/PixTag/assets/92469426/d66b17d0-d8b2-46b2-a2e0-4de0c25cd04b)


## Technologies Used

- **AWS S3**: Storage for images.
- **AWS Lambda**: Serverless functions used to perform the main logic
- **AWS API Gateway**: RESTful API endpoints for all queries.
- **AWS DynamoDB**: Database for storing image metadata and tags.
- **AWS SNS**: Notification service for tag-based subscriptions.
- **OpenCV**: Library for creating image thumbnails added as a layer in lambda.
- **Yolo-tiny-config**: Image processing model added as a layer in lambda.

## Team
- Team51
- Memeber: Jingyan LOU, Yanqi Zhu, Jinhui Li
- Developed as part of the FIT5225:Cloud-computing Coursework


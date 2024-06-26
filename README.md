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
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/6130b116-a752-4749-a46a-54118e12d7c7" alt="Login">
</p>

### Registeration
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/42e1a8d4-7998-4b34-8300-0e3029dee8a8" alt="Registeration">
</p>

### Upload image
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/beedd202-6082-4f09-82d8-a04f347111f7" alt="Upload image">
</p>

### Tag subscribe
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/a3b0046d-450c-4b46-8463-f3d16890c2cd" alt="Tag subscribe">
</p>

### Update tags/Delete tags
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/2050dc26-da34-426a-862c-e95e7422c452" alt="Update tags/Delete tags">
</p>

### Search by tags
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/2b130f99-0646-492c-bb24-2290342fa886" alt="Search by tags">
</p>

### Search by url
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/f46cc47c-24f4-4485-9f54-a6ad64687545" alt="Search by url">
</p>

### Find Similar Images
<p align="center">
  <img src="https://github.com/JingyanLou/PixTag/assets/92469426/d66b17d0-d8b2-46b2-a2e0-4de0c25cd04b" alt="Find Similar Images">
</p>



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


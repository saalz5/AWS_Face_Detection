# AWS Face Recognition

This App is intended to detect all faces on any image along with description for each face such as cordonates and age estimattion

## Technologies
  - Python 3
  - Flask Framework
  - SQLLite3 Database
  - AWS Rekognition 
  - AWS S3 Bucket

## Installation
  * Install python 3
  * Install the dependencies: `Flask boto3 PIL`
  * configure `host` and `port` inside `app.py`
    ```sh
    if __name__ == '__main__':
        app.run(host='127.0.0.1', port=5000, debug=True)
    ```
* run the application
     ```sh
        python3 app.py
    ```
    URL of the applciation will be shown on terminal like: `http://127.0.0.1:5000`


### References

[S3 Bucket](https://aws.amazon.com/s3/faqs)

[AWS Rekognition](https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html)

[AWS Rekognition](https://aws.amazon.com/rekognition/faqs/)

[AWS Rekognition](https://docs.aws.amazon.com/rekognition/latest/dg/API_Reference.html)

[lambda](https://aws.amazon.com/lambda/faqs/)

[AWS EC2](https://aws.amazon.com/ec2/faqs/)

[Flask](https://flask.palletsprojects.com/en/1.1.x/)


License
----

Saad Alyazidi



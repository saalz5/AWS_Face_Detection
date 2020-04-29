from flask import Flask, render_template, redirect
import sqlite3
from flask import request, session
import os
import io
import random
import boto3
from PIL import Image, ImageDraw, ExifTags, ImageColor


ACCESS_KEY = 'AKIA2ZXLTV4AQHSEO46C'
SECRET_KEY = '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'
        
        
app = Flask(__name__, static_folder='public', static_url_path='')
# app unique secret key, use any secret key 
SECRET_KEY_FLASK = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

app.secret_key = SECRET_KEY_FLASK


DATABASE = os.path.join(app.root_path, 'database', 'users.db')


    
    
@app.route("/")
def index():
	return redirect('home')


def upload_to_aws(local_file, bucket, s3_file):
    
    s3 = boto3.client('s3', region_name='us-east-1', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False





def show_faces(photo,bucket):
     
    client = boto3.client('rekognition',region_name='us-east-1', 
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

    # Load image from S3 bucket 
    s3_connection = boto3.resource('s3', region_name='us-east-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)
    
    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    
    #Call DetectFaces 
    response = client.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        Attributes=['ALL'])

    imgWidth, imgHeight = image.size  
    draw = ImageDraw.Draw(image)  
                    

    # calculate and display bounding boxes for each detected face       
    #rez = 'Detected faces for ' + photo + '<br>'   
    rez = []
    for faceDetail in response['FaceDetails']:
        rez.append( 'The detected face is between ' + str(faceDetail['AgeRange']['Low']) + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old' )
        
        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
                

        rez.append('Left: ' + '{0:.0f}'.format(left))
        rez.append('Top: ' + '{0:.0f}'.format(top))
        rez.append('Face Width: ' + "{0:.0f}".format(width))
        rez.append('Face Height: ' + "{0:.0f}".format(height))
        rez.append('')

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)

        )
        draw.line(points, fill='#00d400', width=2)
    
    #old_img = os.path.join(app.static_folder, 'reko', 'result.png')
    #if os.path.exists(old_img):
    #    os.remove(old_img)
    
    filelist = [ f for f in os.listdir(app.static_folder+'/reko') if f.endswith(".png") ]
    for f in filelist:
        os.remove(os.path.join(app.static_folder+'/reko', f))
    
    rand_name = 'rezult' + str(random.randint(1,9)) + str(random.randint(1,9))+ str(random.randint(1,9))+'.png'
    
    image_path = os.path.join(app.static_folder, 'reko', rand_name)
    #image.save(image_path)
    image.save(image_path, 'PNG')
    
    #image.show()

    return len(response['FaceDetails']), rez, rand_name
    
    
    
@app.route("/detection", methods=['GET'])
def faces_detection():
    photo = request.args.get('img')
    
    bucket="bkalziyadi"

    faces_count, rez, rezult_img =show_faces(photo,bucket)
    #print("faces detected: " + str(faces_count))
    
    return render_template('detection.html', data = rez, total = faces_count, images=rezult_img)
    
    


@app.route("/display", methods=['GET'])
def display():
    conn = boto3.client('s3', region_name='us-east-1', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    
    contents = []
    for key in conn.list_objects(Bucket='bkalziyadi')['Contents']:
        contents.append(key['Key'])
    
    return render_template('display.html', data = contents)

@app.route("/home", methods=['GET','POST'])
def home():

    if request.method == 'GET':
    
        if 'userid' in session:
            return render_template('home.html')
        else:
            return redirect("/login")
    
    print('before')
    if request.method == 'POST':
        print('true')
        img = request.files['img']
        filename = ''
        if img:
            filename = img.filename
        
        image_path = os.path.join(app.static_folder, 'img', img.filename)
        img.save(image_path)
        
       
        uploaded = upload_to_aws(image_path, 'bkalziyadi', filename)
        
        os.remove(os.path.join(app.static_folder, 'img', img.filename))

        return render_template('home.html', error = uploaded)
        

@app.route("/login",  methods=['GET','POST'])
def login():
	error = False

	if 'userid' in session: 
			return redirect('/home')

	if request.method == "POST":

		try:
			myform = request.form
			username = myform['username']
			password = myform['password']
			print(DATABASE)
			conn = sqlite3.connect(DATABASE)
			
			query = "SELECT *  FROM user WHERE username = ? and password = ? limit 1"
			cursor = conn.execute(query, (username, password))
			
			data = cursor.fetchall()[0]
			
			#print(data)

			names = [description[0] for description in cursor.description]
		

			data = {names[i]: data[i] for i in range(len(names))}


			
			conn.close()
			
			if not data:
				error = True 
				raise Exception('not found')

			if 'userid' not in session:
				session['userid'] = data['userid']
				session['fullname'] = data['fullname']
				session['role'] = data['role']

			return redirect("/home")

		except Exception as excp:
			print(excp)
			error = True 



	return render_template('login.html', error = error)


@app.route("/logout")
def logout():
	session.pop('userid', None)
	return redirect("/login") 


@app.route("/about")
def about():
	return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    #app.run(host='127.0.0.1', port=5000, debug=True)

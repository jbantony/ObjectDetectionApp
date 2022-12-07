#!/usr/bin/env conda run -n ml-serv python

from flask import Flask, render_template, request, session, Response
import pandas as pd
from pandas.io.json import json_normalize
import csv
import os
import cv2
import base64
import json
import pickle
from werkzeug.utils import secure_filename
import numpy as np
from collections import OrderedDict, defaultdict
import urllib.request

UPLOAD_FOLDER = os.path.join('statisFiles', 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'jpg', 'jpeg', 'gif', 'png', 'pdf'}

app = Flask(__name__, template_folder= 'templateFiles', static_folder='statisFiles')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'This is just a object detection test sample'

#object detection function
def detect_object(uploaded_image_path):
    img = cv2.imread(uploaded_image_path)
    #print(img.shape)

    #load Yolo
    # ------------ Optimize -----------
    if os.path.exists("data/model/yolov3.weights"):
        yolo_weight = "data/model/yolov3.weights"
    else:
        print("Downloading Model File......")
        URL = "https://pjreddie.com/media/files/yolov3.weights"
        yolo_weight= urllib.request.urlretrieve(URL, filename="data/model/yolov3.weights")
        print("Model download complete")
        

    yolo_weight = "data/model/yolov3.weights"
    yolo_config= "data/model/yolov3.cfg"
    coco_names = "data/model/coco.names"

    net = cv2.dnn.readNet(yolo_weight, yolo_config)

    classes = []

    with open(coco_names, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    #print(classes)

    height0, width0, channels0 = img.shape
    img_copy0= img

    # define the desired shape
    fWidth = 320
    fHeight = 320


    #resie image
    img = cv2.resize(img, (fWidth, fHeight))

    height, width, channels = img.shape

    

    #convert image to blob
    blob = cv2.dnn.blobFromImage(img, 1/255, (fWidth, fHeight), (0,0,0), True, crop= False)
    net.setInput(blob)

    layer_names= net.getLayerNames()
    #print(layer_names)
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    #print(output_layers)

    outs = net.forward(output_layers)
    #print(outs[0].shape)

    #generting random color for the 80 classes in coco
    colors = np.random.uniform(0,255, size=(len(classes), 3))

    # Extract information on the view
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            #extract score values
            scores = detection[5:]

            # Object id
            class_id = np.argmax(scores)

            # confidence score for each object ID
            confidence = scores[class_id]

            # if confidence > 0.5 and class_id == 0:
            if confidence > 0.5:
                # Extract values to draw bounding box
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
 
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    # Draw bounding box with text for each object
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    ordered_classes = {"label": [], "confidence": []}
    object_count = defaultdict(int)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            ordered_classes['label'].append(label)
            confidence_label = int(confidences[i] * 100)
            ordered_classes['confidence'].append(confidence_label)
            object_count[str(label)] +=1
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f'{label}', (x+25, y + 75), font, 1, color, 1)
 
    # Write output image (object detection output)
    output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image.jpg')
    cv2.imwrite(output_image_path, img)

    return(output_image_path, ordered_classes, object_count)



@app.route('/')
def index():

    try:
        if session.get('uploaded_source_image', None):
            img_file_path = session.get('uploaded_source_image', None)
            os.remove(img_file_path)
    except FileNotFoundError:
        print('You removed the cache file')

    return render_template('index_upload_show_data.html')

@app.route('/', methods= ["POST", "GET"])
def uploadFile():
    if request.method == "POST":
        uploaded_img = request.files['sourceImage']
        img_filename = secure_filename(uploaded_img.filename)
        uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        session['uploaded_source_image'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)

        return render_template('index_upload_show_data2.html')



@app.route('/show_image', methods= ["POST", "GET"])
def displayImage():
    img_file_path = session.get('uploaded_source_image', None)

    return render_template('index_show_image.html', user_image =  img_file_path)



@app.route('/detect_object', methods=["POST", "GET"])
def runDetection():
    

    if request.method == "POST":   
        img_file_path = session.get('uploaded_source_image', None)
        output_img_path, ordered_classes, object_count = detect_object(img_file_path)
        #print(output_img_path)
        detection_table = pd.DataFrame(ordered_classes)
        detection_table= detection_table.rename(columns={'label':'Detected Label', 'confidence':'Detection Confidence'}).to_html(index=False, classes='style1')

        counter_table = pd.DataFrame(object_count.items(), columns=['Detected Objects', 'Detection Count'])
        counter_table= counter_table.to_html(index=False, classes='style1')

        #return render_template('index_show_image2.html', user_image =  output_img_path, detections = detection_table, counts= sorted(object_count.items()))
        return render_template('index_show_image2.html', user_image =  output_img_path, detections = detection_table, counts= counter_table)
    


 
# flask clear browser cache (disable cache)
# Solve flask cache images issue
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
 
if __name__=='__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug = True, host='0.0.0.0', port=port) 

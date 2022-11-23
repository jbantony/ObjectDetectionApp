## Object Detection App based on Flask

This a simple Object Detection App working on browser using Flask and YOLOv3

- #### Model Used
 YOLOv3 320x320 from Darknet 
 Weights are available at [YOLOv3 Weights](https://pjreddie.com/darknet/yolo/)
 
 The configuration file used from [cfg File](https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg)
 The labels for COCO are used from [coco names](https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names)

 **Note** Download the model weights and save it under `data/model/` as `yolov3.weights` before running the App

### Dependencies

Create an enviorment for the app using 

`conda env create -f environment.yml`

The complete enviorment is listed under the file `environment_all.yml`


### API Calls

- `/show_image`

Used to visualise the uploaded image

- `/detect_object`

Used to perform object detection using YOLOv3


### Running the App

Run the app in Debug Mode

`flask --app flask_object_detection_app --debug run`

#### Page1

![page1](docs/page1.png)

#### Page 2
![page2](docs/page2.png)

#### Page 3
![page3](docs/page3.png)

#### Page 4
![page4](docs/page4.png)



#### Reference

Developed from the tutorial from [Thinkinfi](https://thinkinfi.com/yolo-object-detection-using-python-opencv/)

FROM python:3.9

LABEL maintainer="Jibinraj Antony <jibinraj.antony@dfki.de>"

ENV DEBIAN_FRONTEND = noninteractive

RUN apt-get update && yes | apt-get upgrade

RUN  apt-get install ffmpeg libsm6 libxext6  -y

RUN mkdir -p /work

RUN apt-get install -y python3-pip

WORKDIR /work

COPY . .

RUN pip install -r requirements.txt

WORKDIR /data/model

RUN curl -o yolov3.weights https://pjreddie.com/media/files/yolov3.weights

EXPOSE 80

WORKDIR /work

RUN mkdir -p /statisFiles/uploads

CMD ["flask", "--app", "flask_object_detection_app", "--debug", "--host", "0.0.0.0", "--port", "80", "run" ]


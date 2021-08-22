#!/usr/bin/env python
from flask import Flask, render_template, Response
from io import BytesIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time
import random
import datetime
from matplotlib import font_manager

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def generate_random_jpeg():
    file = BytesIO()
    image = Image.new('RGB', size=(500, 500), color=(random.randrange(256), random.randrange(256), random.randrange(256)))
    image.save(file, 'jpeg')
    file.name = 'test.jpeg'
    file.seek(0)
    return file.read()


def gen():
    while True:
        frame = generate_random_jpeg()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def mqtt_jpeg_streamer(camera):
    while True:
        file = BytesIO()
        image = Image.new('RGB', size=(500, 500), color=(random.randrange(256), random.randrange(256), random.randrange(256)))
        font = ImageFont.truetype('Helvetica', 16)
        draw = ImageDraw.Draw(image)
        text = '%s @ %s' % (camera, datetime.datetime.now())
        draw.text((0, 0), text, (0, 0, 0), font)
        image.save(file, 'jpeg')
        file.name = 'test.jpeg'
        file.seek(0)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + file.read() + b'\r\n')
        time.sleep(.001)


@app.route('/video_feed')
@app.route('/video_feed/<camera>')
def video_feed(camera='None'):
    return Response(mqtt_jpeg_streamer(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
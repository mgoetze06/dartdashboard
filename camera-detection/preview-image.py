#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This file is part of python-gphoto2.
#
# python-gphoto2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# python-gphoto2 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with python-gphoto2.  If not, see
# <https://www.gnu.org/licenses/>.

import io
import locale
import logging
import os
import subprocess
import sys
import numpy as np
import imutils

import cv2
from PIL import Image

import gphoto2 as gp
import time
import datetime

def main():
    subprocess.run(["pkill", "-f", "gphoto2"])


    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    # required configuration will depend on camera type!
    print('Checking camera config')
    # get configuration tree
    config = gp.check_result(gp.gp_camera_get_config(camera))
    # find the image format config item
    # camera dependent - 'imageformat' is 'imagequality' on some
    OK, image_format = gp.gp_widget_get_child_by_name(config, 'imageformat')
    if OK >= gp.GP_OK:
        # get current setting
        value = gp.check_result(gp.gp_widget_get_value(image_format))
        # make sure it's not raw
        if 'raw' in value.lower():
            print('Cannot preview raw images')
            return 1
    # find the capture size class config item
    # need to set this on my Canon 350d to get preview to work at all
    OK, capture_size_class = gp.gp_widget_get_child_by_name(
        config, 'capturesizeclass')
    if OK >= gp.GP_OK:
        # set value
        value = gp.check_result(gp.gp_widget_get_choice(capture_size_class, 2))
        gp.check_result(gp.gp_widget_set_value(capture_size_class, value))
        # set config
        gp.check_result(gp.gp_camera_set_config(camera, config))
    # capture preview image (not saved to camera memory card)
    print('Capturing preview image')
    i = 0
    cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)          
    cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while i < 1000:
        a = datetime.datetime.now()
        camera_file = gp.check_result(gp.gp_camera_capture_preview(camera))
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        # display image
        data = memoryview(file_data)
        #print(type(data), len(data))
        #print(data[:10].tolist())
        image_io = io.BytesIO(file_data)
        #image = Image.open(image_io)
        #image.show()
        #print(image.size)
        #print(image_io)
        image_io.seek(0)
        org_img = cv2.imdecode(np.frombuffer(image_io.read(), np.uint8), 1)
        #scr_w,scr_h = 1920,1080
        if org_img.shape[1] > 1920:
            org_img = imutils.resize(org_img, width=1920)


        b = datetime.datetime.now()
        cv2.imshow("image",org_img)
        cv2.waitKey(1)
        if i % 10 == 0:
            print(i)
            print("processed preview in %s ms"%((b-a).total_seconds()*1000))
        i += 1
        #time.sleep(0.2)
    cv2.destroyAllWindows()
    gp.check_result(gp.gp_camera_exit(camera))

    return 0


# camera = gp.Camera()
# camera.wait_for_event(100)
# camera.get_config()

# def getPreview(cam):
#     a = datetime.datetime.now()
#     camera_file = gp.check_result(gp.gp_camera_capture_preview(cam))
#     file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
#     data = memoryview(file_data)
#     gp.check_result(gp.gp_camera_exit(camera))
#     #camera.capture(gp.GP_CAPTURE_IMAGE)
#     image_io = io.BytesIO(file_data)
#     image = Image.open(image_io)
#     print(image.size)
#     b = datetime.datetime.now()
#     print("processed preview in %s ms"%((b-a).total_seconds()*1000))
#     return image,image_io

# #image is PIL Image; image_io is BytesIO representation of image --> used to convert to cv2
# image,image_io = getPreview(camera)
# image.show()
# print(image_io)
#for i in range(10):
#    getPreview(camera).show()
#    time.sleep(1000)

#_ = gp.check_result(gp.gp_camera_exit(camera))


if __name__ == "__main__":
    sys.exit(main())

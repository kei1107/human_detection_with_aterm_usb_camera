import base64
import os
import shutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import src
import sys
import time
from datetime import datetime
import pytz
from io import BytesIO
from PIL import Image

from keras.applications.imagenet_utils import preprocess_input
from keras.backend.tensorflow_backend import set_session
from keras.preprocessing import image
import numpy as np
import tensorflow as tf

from ssd import SSD300
from ssd_utils import BBoxUtility


def save_image(src, file_save_path):
    # Base64エンコードされた画像をデコードして保存する。
    if "base64," in src:
        with open(file_save_path, "wb") as f:
            f.write(base64.b64decode(src.split(",")[1]))

    # 画像のURLから画像を保存する。
    else:
        res = requests.get(src, stream=True)
        with open(file_save_path, "wb") as f:
            shutil.copyfileobj(res.raw, f)


# Main
# logger setting
logger = src.Setup_Logger.Setup_Logger()
np.set_printoptions(suppress=True)
# SSD setting
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.45
set_session(tf.Session(config=config))
voc_classes = ['Aeroplane', 'Bicycle', 'Bird', 'Boat', 'Bottle',
               'Bus', 'Car', 'Cat', 'Chair', 'Cow', 'Diningtable',
               'Dog', 'Horse', 'Motorbike', 'Person', 'Pottedplant',
               'Sheep', 'Sofa', 'Train', 'Tvmonitor']
NUM_CLASSES = len(voc_classes) + 1
input_shape = (300, 300, 3)
model = SSD300(input_shape, num_classes=NUM_CLASSES)
model.load_weights('weights/weights_SSD300.hdf5', by_name=True)
bbox_util = BBoxUtility(NUM_CLASSES)

# Chronium setting
user, pw, ip = src.Setup_Config.Setup_Config(logger=logger)
main_url = 'http://' + user + ':' + pw + '@' + ip + ':15790'
options = Options()
options.binary_location = None
if os.name == 'posix':
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
elif os.name == 'nt':
    options.binary_location = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'

if options.binary_location is None:
    logger.info('Support : Windows , OSX')
    sys.exit()
try:
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(main_url)
    logger.info('Accessing')

    start_button = driver.find_element_by_id('VMG_PRE_START_BTN')
    start_button.click()

    print("Start Detector")
    while True:
        try:
            BUF_UVCCAM2 = driver.find_element_by_id('BUF_UVCCAM2')
            img_url = BUF_UVCCAM2.get_attribute('src')

            img_response = requests.get(img_url)
            output_img = Image.open(BytesIO(img_response.content))

            img = output_img.copy()
            img = img.resize((300, 300))
            img = image.img_to_array(img)

            inputs = []
            inputs.append(img.copy())
        except Exception as e:
            continue

        inputs = preprocess_input(np.array(inputs))
        preds = model.predict(inputs, batch_size=1)
        results = bbox_util.detection_out(preds)

        # Parse the outputs.
        det_label = results[0][:, 0]
        det_conf = results[0][:, 1]

        cand_size = len(det_label)
        isPerson = False

        for i in range(cand_size):
            if det_conf[i] < 0.9:
                continue
            else:
                # Person is 15
                if int(det_label[i]) == 15:
                    isPerson = True
                    break

        if isPerson:
            # time de hozon
            now_time_str = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y%m%d_%H%M%S%f')[:-3]
            # print("Person detect :",now_time_str)

            try:
                image.save_img("./output/" + now_time_str + '.jpg', output_img)
            except Exception as e:
                continue
        time.sleep(0.5)

except Exception as e:
    logger.info('Web driver Error occured!')
    logger.exception(e)
    sys.exit()

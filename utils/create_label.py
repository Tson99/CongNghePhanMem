from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image
import io
import cv2
import numpy as np
import os
import re


def create_cropped_image(imgs, dest, model):
    for idx, img in enumerate(imgs):
        image = img.resize((640, 640), Image.ANTIALIAS)
        image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        image_detect_corner = model.detect_corner(image)
        cv2.imwrite(os.path.join(dest, '{:06d}.jpg'.format(idx+1)), image_detect_corner)


def create_text_annotation_ocr(imgs, dest):
    config = Cfg.load_config_from_name('vgg_transformer')
    config['export'] = 'transformerocr_checkpoint.pth'
    config['device'] = 'cuda'
    config['predictor']['beamsearch'] = False
    detector = Predictor(config)
    f = io.open(os.path.join(dest, "annotation.txt"), "a", encoding="utf-8")
    for idx, image in enumerate(imgs):
        text = detector.predict(image)
        if idx + 1 == len(imgs):
            f.write('crop_img/{:06d}.jpg\t{}'.format(idx + 1, text))
        else:
            f.write('crop_img/{:06d}.jpg\t{}\n'.format(idx+1, text))
    f.close()


def create_lines_image_ocr(imgs, dest, model):
    if not os.path.exists(os.path.join(dest, 'crop_img')):
        os.makedirs(os.path.join(dest, 'crop_img'))
    idx = 0
    for img in imgs:
        image = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        result = model.predict(image, is_Front=model.is_Front, infer=False)
        for cropped_image in result:
            idx += 1
            cv2.imwrite(os.path.join(dest, 'crop_img', '{:06d}.jpg'.format(idx)), cropped_image)
    images = [f for f in os.listdir(os.path.join(dest, 'crop_img'))
              if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(.jpg|.jpeg|.png)$', f)]
    imgs = []
    for filename in images:
        imgs.append(Image.open(os.path.join(dest, 'crop_img', filename)))
    create_text_annotation_ocr(imgs, dest)








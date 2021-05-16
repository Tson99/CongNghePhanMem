from utils.create_label import create_lines_image_ocr, create_cropped_image, create_text_annotation_ocr
from PIL import Image
import os
import argparse
import re
from main import CompletedModel

def iterate_dir(source, dest, mode, choice):
    source = source.replace('\\', '/')
    dest = dest.replace('\\', '/')
    images = [f for f in os.listdir(source)
              if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(.jpg|.jpeg|.png)$', f)]
    imgs = []
    for filename in images:
        imgs.append(Image.open(os.path.join(source, filename)))
    if choice == 'front':
        is_front = True
    elif choice == 'back':
        is_front = False
    else:
        raise ValueError("c must be front or back")
    model = CompletedModel()
    model.is_Front = is_front
    if mode == "corner":
        create_cropped_image(imgs, dest, model)
    elif mode == "text":
        create_lines_image_ocr(imgs, dest, model)
    else:
        raise ValueError("m must be corner or text")


parser = argparse.ArgumentParser(description='Make data train from model pretrain')

parser.add_argument(
    '-i', '--imageDir',
    help='Path to the folder where the image dataset is stored. If not specified, the CWD will be used.',
    type=str,
    default=os.getcwd()
)
parser.add_argument(
    '-o', '--outputDir',
    help='Path to the output folder where the train and test dirs should be created. ',
    type=str,
    default=None
)
parser.add_argument(
    '-c', '--choiceID',
    help='front: frontID'
         'back: backID',
    type=str,
    default='front'
)
parser.add_argument(
    '-m', '--mode',
    help="corner: Take raw image to input and output will be image crop 4 corners of id card"
         "text: Take id card and then output will be images of fields",
    type=str,
    default='corner'
)


args = parser.parse_args()
if args.mode == 'corner':
    if args.outputDir is None:
        if not os.path.exists('./corner_image_detection/'):
            os.makedirs('./corner_image_detection')
        args.outputDir = './corner_image_detection'
elif args.mode == 'text':
    if args.outputDir is None:
        if not os.path.exists('./lines_image_ocr/'):
            os.makedirs('./lines_image_ocr')
        args.outputDir = './lines_image_ocr'

iterate_dir(args.imageDir, args.outputDir, args.mode, args.choiceID)

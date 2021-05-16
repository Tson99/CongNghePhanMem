from detector import Detector
from recognition import TextRecognition
from utils.image_utils import align_image, sort_text_front, sort_text_back
import numpy as np
import re
import os
import cv2
import datetime
import threading
from PIL import Image
import difflib
import json
import mysql.connector


with open('dictionary.json', encoding='utf-8') as infile:
    Dictionary = json.load(infile)

with open('nation.json', encoding='utf-8') as infile:
    Nation = json.load(infile)


class CompletedModel(object):
    __instance = None
    def __init__(self):
        # Front ID card
        self.corner_detection_model_front = Detector(
            path_to_model='models/config_corner_detection/model_front_320x320.tflite',
            path_to_labels='models/config_corner_detection/label_map_front.pbtxt',
            nms_threshold=0.2, score_threshold=0.3)

        self.text_detection_model_front = Detector(
            path_to_model='models/config_text_detection/model_front_320x320.tflite',
            path_to_labels='models/config_text_detection/label_map_front.pbtxt',
            nms_threshold=0.2, score_threshold=0.2)

        # Back ID card
        self.corner_detection_model_back = Detector(
            path_to_model='models/config_corner_detection/model_back_640x640.tflite',
            path_to_labels='models/config_corner_detection/label_map_back.pbtxt',
            nms_threshold=0.2, score_threshold=0.3)

        self.text_detection_model_back = Detector(
            path_to_model='models/config_text_detection/model_back_640x640.tflite',
            path_to_labels='models/config_text_detection/label_map_back.pbtxt',
            nms_threshold=0.2, score_threshold=0.2)

        # Recognition OCR
        self.text_recognition_model = TextRecognition(
            path_to_checkpoint='models/config_text_recognition/transformerocr_new.pth')

        # init front boxes
        self.id_boxes = None
        self.name_boxes = None
        self.birth_boxes = None
        self.add_boxes = None
        self.home_boxes = None
        self.img_boxes = None

        # init back boxes
        self.nation_boxes = None
        self.religion_boxes = None
        self.identifying_characteristics_boxes = None
        self.registration_day_boxes = None
        self.place_of_registration_boxes = None

        # threading
        self.predict_lock = threading.Lock()

        # Is front?
        self.is_Front = True

    @staticmethod
    def get_instance():
        if CompletedModel.__instance is None:
            CompletedModel.__instance = CompletedModel()
        return CompletedModel.__instance

    def detect_corner(self, image):
        if self.is_Front:
            detection_boxes, detection_classes, category_index = self.corner_detection_model_front.predict(image)
        else:
            detection_boxes, detection_classes, category_index = self.corner_detection_model_back.predict(image)
        coordinate_dict = dict()
        height, width, _ = image.shape

        for i in range(len(detection_classes)):
            label = str(category_index[detection_classes[i]]['name'])
            real_y_min = int(max(1, detection_boxes[i][0]))
            real_x_min = int(max(1, detection_boxes[i][1]))
            real_y_max = int(min(height, detection_boxes[i][2]))
            real_x_max = int(min(width, detection_boxes[i][3]))
            coordinate_dict[label] = (real_x_min, real_y_min, real_x_max, real_y_max)

        align_img = align_image(image, coordinate_dict)
        return align_img

    def detect_text(self, cropped_image):
        if self.is_Front:
            detection_boxes, detection_classes, category_index = self.text_detection_model_front.predict(cropped_image)
            self.id_boxes, self.name_boxes, self.birth_boxes, self.home_boxes, self.add_boxes, self.img_boxes = sort_text_front(
                detection_boxes, detection_classes)  # ADD
        else:
            detection_boxes, detection_classes, category_index = self.text_detection_model_back.predict(cropped_image)
            self.nation_boxes, self.religion_boxes, self.identifying_characteristics_boxes, self.registration_day_boxes, self.place_of_registration_boxes = sort_text_back(
                detection_boxes, detection_classes)  # ADD

    @staticmethod
    def crop_and_recog(boxes, bbox, cropped_image):
        crop = []
        idx_pop = []
        for idx, box in enumerate(boxes):
            bbox_y_min, bbox_x_min, bbox_y_max, bbox_x_max = bbox
            y_min, x_min, y_max, x_max = box
            if (y_min >= bbox_y_min) and (y_max <= bbox_y_max) and (x_min >= bbox_x_min) and (x_max <= bbox_x_max):
                crop.append(cropped_image[y_min:y_max, x_min:x_max])
            else:
                print('Out of bbox', box)
                idx_pop.append(idx)
        for idx_p, value_p in enumerate(idx_pop):
            boxes.pop(value_p - idx_p)
        return crop

    def text_recognition_front(self, cropped_image, inference=True):
        bbox_field = dict()
        bbox_field['id'] = (50, 207, 200, 458)
        bbox_field['name'] = (85, 100, 160, 500)
        bbox_field['birth'] = (140, 230, 210, 500)
        bbox_field['home'] = (170, 140, 280, 500)
        bbox_field['add'] = (210, 130, 300, 500)
        # bbox_field['id'] = (0, 0, 300, 500)
        # bbox_field['name'] = (0, 0, 300, 500)
        # bbox_field['birth'] = (0, 0, 300, 500)
        # bbox_field['home'] = (0, 0, 300, 500)
        # bbox_field['add'] = (0, 0, 300, 500)
        list_ans = list(self.crop_and_recog(self.id_boxes, bbox_field['id'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.name_boxes, bbox_field['name'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.birth_boxes, bbox_field['birth'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.home_boxes, bbox_field['home'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.add_boxes, bbox_field['add'], cropped_image))

        if not inference:
            return list_ans
        result = self.text_recognition_model.predict_on_batch(np.array(list_ans))
        data = dict()
        begin = 0
        for idx in range(begin, begin + len(self.id_boxes)):
            if re.search(r'\d', result[idx]):
                temp_id = result[idx].replace('SỐ ', '')
                data['id'] = temp_id
                break

        begin += len(self.id_boxes)
        temp_name = []
        for idx in range(begin, begin + len(self.name_boxes)):
            if re.search(r'\d', result[idx]) is None:
                temp_name.append(result[idx])
        data['name'] = ' '.join(temp_name)

        begin += len(self.name_boxes)
        temp_birth = []
        for idx in range(begin, begin + len(self.birth_boxes)):
            if re.search(r'\d', result[idx]):
                temp_birth.append(result[idx])
                data['birth'] = result[idx]
                break

        begin += len(self.birth_boxes)
        temp_home_boxes = []
        for idx in range(begin, begin + len(self.home_boxes)):
            temp_home_boxes.append(result[idx])
        data['home'] = ' '.join(temp_home_boxes)

        begin += len(self.home_boxes)
        temp_add_boxes = []

        for idx in range(begin, begin + len(self.add_boxes)):
            temp_add_boxes.append(result[idx])
        data['address'] = ' '.join(temp_add_boxes)

        coordinate = self.img_boxes[0]
        crop_personal_img = cropped_image[coordinate[0]:coordinate[2], coordinate[1]:coordinate[3]]
        name = "CMND_front_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_{}".format(
            data['id']) + ".jpg"
        link_save = os.path.join('dataweb/PhotoCard', name)
        cv2.imwrite(link_save, crop_personal_img)
        return data

    def text_recognition_back(self, cropped_image, inference=True):
        bbox_field = dict()
        bbox_field['nation'] = (0, 76, 57, 245)
        bbox_field['religion'] = (0, 312, 60, 500)
        bbox_field['identifying_characteristics'] = (55, 181, 157, 500)
        bbox_field['registration_day'] = (125, 200, 192, 500)
        bbox_field['place_of_registration'] = (160, 260, 230, 500)
        # bbox_field['nation'] = (0, 0, 300, 500)
        # bbox_field['religion'] = (0, 0, 300, 500)
        # bbox_field['identifying_characteristics'] = (0, 0, 300, 500)
        # bbox_field['registration_day'] = (0, 0, 300, 500)
        # bbox_field['place_of_registration'] = (0, 0, 300, 500)
        list_ans = list(self.crop_and_recog(self.nation_boxes, bbox_field['nation'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.religion_boxes, bbox_field['religion'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.identifying_characteristics_boxes, bbox_field['identifying_characteristics'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.registration_day_boxes, bbox_field['registration_day'], cropped_image))
        list_ans.extend(self.crop_and_recog(self.place_of_registration_boxes, bbox_field['place_of_registration'], cropped_image))
        if not inference:
            return list_ans

        result = self.text_recognition_model.predict_on_batch(np.array(list_ans))

        data = dict()
        begin = 0
        temp_nation = []
        for idx in range(begin, begin + len(self.nation_boxes)):
            temp_nation.append(result[idx])
        data['nation'] = ' '.join(temp_nation)

        begin += len(self.nation_boxes)
        temp_religion = []
        for idx in range(begin, begin + len(self.religion_boxes)):
            temp_religion.append(result[idx])
        data['religion'] = ' '.join(temp_religion)

        begin += len(self.religion_boxes)
        temp_identifying_characteristics = []
        for idx in range(begin, begin + len(self.identifying_characteristics_boxes)):
            temp_identifying_characteristics.append(result[idx])
        data['identifying_characteristics'] = ' '.join(temp_identifying_characteristics)

        begin += len(self.identifying_characteristics_boxes)
        temp_registration_day = []
        for idx in range(begin, begin + len(self.registration_day_boxes)):
            temp_registration_day.append(result[idx])
        data['registration_day'] = ''.join(temp_registration_day)

        begin += len(self.registration_day_boxes)
        temp_place_of_registration = []
        for idx in range(begin, begin + len(self.place_of_registration_boxes)):
            temp_place_of_registration.append(result[idx])
        data['place_of_registration'] = ' '.join(temp_place_of_registration)
        return data

    @staticmethod
    def post_processing_home_address(data):
        calibration_address = [element.strip().lower() for element in data.split(',')]
        final_address = calibration_address
        ThanhPho, QuanHuyen, PhuongXa = None, None, None
        for idx, pattern in reversed(list(enumerate(calibration_address))):
            if len(calibration_address) < 2:
                break
            if ThanhPho is None:
                pre = str()
                text = re.findall(r"^(tp\.|tp|t/p\.|t/phố|t/p|thành phố|thànhphố)* *([\w|\s]*)", pattern)
                if text:
                    pre = text[0][0]
                    pattern = text[0][1]
                closet_dict = difflib.get_close_matches(pattern, Dictionary.keys(), n=1, cutoff=0.8)
                if len(closet_dict) == 1:
                    ThanhPho = closet_dict[0]
                    if pre == "":
                        final_address[idx] = closet_dict[0]
                    else:
                        final_address[idx] = " ".join((pre, closet_dict[0]))
                    continue
            elif QuanHuyen is None:
                if len(calibration_address) < 3:
                    break
                pre = str()
                text = re.findall(r"^(tp\.|tp|t/p\.|t/p|huyện|quận|thành phố|thị xã|h\.|q\.)* *([\w|\s]*)", pattern)
                # print(text)
                if text:
                    pre = text[0][0]
                    pattern = text[0][1]
                closet_dict = difflib.get_close_matches(pattern, Dictionary[ThanhPho].keys(), n=1, cutoff=0.8)
                # print(closet_dict)
                if len(closet_dict) == 1:
                    QuanHuyen = closet_dict[0]
                    if pre == "":
                        final_address[idx] = closet_dict[0]
                    else:
                        final_address[idx] = " ".join((pre, closet_dict[0]))
                    # print(final_address[idx])
                    continue
            elif PhuongXa is None:
                pre = str()
                text = re.findall(r"^(phường|xã|thị trấn|thịtrấn|p\.|x\.|tổ *\d*)* *([\w|\s]*)", pattern)
                # print(text)
                if text:
                    pre = text[0][0]
                    pattern = text[0][1]
                closet_dict = difflib.get_close_matches(pattern, Dictionary[ThanhPho][QuanHuyen], n=1, cutoff=0.8)
                if len(closet_dict) == 1:
                    PhuongXa = closet_dict[0]
                    if pre == "":
                        final_address[idx] = closet_dict[0]
                    else:
                        final_address[idx] = " ".join((pre, closet_dict[0]))
                continue
            break
        final_address = [element.title() for element in final_address]
        result = ', '.join(final_address)
        return result

    @staticmethod
    def post_processing_place_of_registration(data):
        pre = str()
        text = re.findall(r"^(tp\.|tp|t/p\.|t/phố|t/p|thành phố|thànhphố|t\.|tỉnh)* *([\w|\s]*)", data.lower())
        if text:
            pre = text[0][0]
            pattern = text[0][1]
        res = difflib.get_close_matches(pattern, Dictionary.keys(), n=1, cutoff=0.8)
        if len(res) == 1:
            if pre == "":
                return res[0].title()
            else:
                return " ".join((pre, res[0])).title()
        else:
            return data.title()

    @staticmethod
    def post_processing_nation(data):
        res = difflib.get_close_matches(data.lower(), Nation["Dân tộc"], n=1, cutoff=0.5)
        if len(res) == 1:
            return res[0].title()
        else:
            return data

    def predict(self, image, is_Front, infer=True):
        self.is_Front = is_Front
        self.predict_lock.acquire()
        field_dict = None
        mydb = mysql.connector.connect(
            host="localhost",
            user="tson99",
            password="Dotuansondnno1+",
            database="CongNghePhanMem_DB"
        )
        mycursor = mydb.cursor()
        try:
            cropped_image = self.detect_corner(image)
            self.detect_text(cropped_image)
            if self.is_Front:
                field_dict = self.text_recognition_front(cropped_image, inference=infer)
                print(field_dict)
                field_dict['home'] = self.post_processing_home_address(field_dict['home'])
                field_dict['address'] = self.post_processing_home_address(field_dict['address'])
                sql = "INSERT INTO Persons (Name, ID_Cmnd, Birth, Home, Address) VALUES (%s, %s, %s, %s, %s)"
                val = (field_dict['name'], field_dict['id'], field_dict['birth'], field_dict['home'],field_dict['address'])
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")
            # else:
            #     field_dict = self.text_recognition_back(cropped_image, inference=infer)
            #     print(field_dict)
            #     field_dict['place_of_registration'] = self.post_processing_place_of_registration(field_dict['place_of_registration'])
            #     field_dict['nation'] = self.post_processing_nation(field_dict['nation'])
        except:
            pass
        finally:
            self.predict_lock.release()
        return field_dict


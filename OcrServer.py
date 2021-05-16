import cv2
import logging
import os
import numpy as np
from threading import Thread
import json
import requests
import socket
from PIL import Image
from main import CompletedModel
import time
from utils import config_ast
from utils.db import Database
import datetime
import re


class MainUI:
    def __init__(self):
        """Lay thong tin config.ini"""
        self.configs = self.__getconfigs(config_ast.ConfigAST('config.ini'))
        self.SQL = Database(self.configs['DATABASE']['server'], self.configs['DATABASE']['database'],
                            self.configs['DATABASE']['uid'], self.configs['DATABASE']['pwd'])
        self.image = None
        self.data = None
        self.name = None
        self.output = None
        self.information = None
        self.model = CompletedModel.get_instance()
        host = self.configs['SOCKET']['host']
        port = int(self.configs['SOCKET']['port'])
        print(host, port)
        connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect.bind((host, port))
        connect.listen(12)
        print("Waiting request...")
        while True:
            socket_obj, addr = connect.accept()
            print('Connected : {}'.format(addr))
            Thread(target=self.receiver_msg, args=(socket_obj, addr,)).start()

    def receiver_msg(self, socket_obj, addr):
        data_recv = socket_obj.recv(1024)
        ID = data_recv.decode('utf-8')
        print("Receive ID : ", ID)
        self.data = self.SQL.get_id(ID, 'tbl_Object')
        self.get_information()
        if self.image is None:
            logging.error('No request')
            assert 'No request'
        else:
            category = 'IdentityCard'
            start = time.time()
            if category == 'IdentityCard':
                if self.data['IsFront']:
                    print("Front ID card")
                    self.output = self.model.predict(self.image, is_Front=True, infer=True)
                    self.post_processing_front()
                    self.information = '{"NumberId":"%s","FullName":"%s","Birthday":"%s","Nationality":"%s","NativeLand":"%s","Homeland":"%s"}' % (
                        self.output['id'], self.output['name'], self.output['birth'], 'VN', self.output['home'],
                        self.output['address'])
                else:
                    print("Back ID card")
                    self.output = self.model.predict(self.image, is_Front=False, infer=True)
                    self.post_processing_back()
                    self.information = '{"danToc":"%s","tonGiao":"%s","dacDiem":"%s","ngayCap":"%s","noiCap":"%s"}' % (
                        self.output['nation'], self.output['religion'], self.output['identifying_characteristics'],
                        self.output['registration_day'], self.output['place_of_registration'])
            end = time.time()
            print("Inference time 's model: ", end - start)
            print(addr, ' => ', self.information)
            # logging.info(' => '.join([self.name, self.information]))
            logging.info(self.information)
            obj = {'Identified': self.information, 'Status': 1, 'IDs': int(ID)}
            self.SQL.update(obj)
            if self.configs['ALERT']['send_api']:
                response, data = self.send_api('Atoma OCR', ID, self.information)
                print("Status code : {}".format(response))
                print("Content : {}".format(response.content))

    def send_api(self, title, ID, data):
        url_api = self.configs['ALERT']['url_api']
        headers = {'content-type': 'application/json'}
        data_api = {'title': '{}'.format(title),
                    'IDs': '{}'.format(ID),
                    'data': data}
        return requests.post(url_api, data=json.dumps(data_api), headers=headers), data_api

    def get_information(self):
        img_PIL = Image.open(requests.get(self.data['ImagePath'], stream=True).raw)
        img_PIL = img_PIL.resize((640, 640), Image.ANTIALIAS)
        self.image = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)

    def post_processing_front(self):
        for item in ['id', 'name', 'birth', 'home', 'address']:
            if (item not in self.output) or (len(self.output[item]) == 0):
                self.output[item] = ""
        self.output['birth'] = ''.join(self.output['birth'].split('-'))
        self.name = "CMND_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_{}".format(
            self.output['id']) + ".jpg"
        link_save = os.path.join('dataweb/IdentityCard/FrontID', self.name)
        cv2.imwrite(link_save, self.image)

    def post_processing_back(self):
        for item in ['nation', 'religion', 'identifying_characteristics', 'registration_day', 'place_of_registration']:
            if (item not in self.output) or (len(self.output[item]) == 0):
                self.output[item] = ""
        ctx = re.findall(r"\d+", self.output['registration_day'])
        self.output['registration_day'] = ''.join(ctx)
        self.name = "CMND_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
        link_save = os.path.join('dataweb/IdentityCard/BackID', self.name)
        cv2.imwrite(link_save, self.image)

    @staticmethod
    def __getconfigs(configs):
        cfg = configs.configs_dict
        "ALERT"
        if cfg.get('ALERT') is None:
            cfg['ALERT'] = {}
        cfg['ALERT']['send_api'] = cfg['ALERT'].get('send_api', False)
        cfg['ALERT']['url_api'] = cfg['ALERT'].get('url_api', '')
        "DATABASE"
        if cfg.get('DATABASE') is None:
            cfg['DATABASE'] = {}
        cfg['DATABASE']['driver'] = cfg['DATABASE'].get('driver', 'MySQL')
        cfg['DATABASE']['server'] = cfg['DATABASE'].get('server', 'localhost')
        cfg['DATABASE']['database'] = cfg['DATABASE'].get('database', 'congnghephanmem')
        cfg['DATABASE']['uid'] = cfg['DATABASE'].get('uid', 'root')
        cfg['DATABASE']['pwd'] = cfg['DATABASE'].get('pwd', 'Dotuansondnno1+')
        # "SOCKET"
        # if cfg.get('SOCKET') is None:
        #     cfg['SOCKET'] = {}
        # cfg['SOCKET']['host'] = cfg['SOCKET'].get('host', '0.0.0.0')
        # cfg['SOCKET']['port'] = cfg['SOCKET'].get('port', '12345')
        return cfg


if __name__ == "__main__":
    logging.basicConfig(
        handlers=[logging.FileHandler(filename="log_records.log", encoding='utf-8', mode='a+')],
        level=logging.INFO,
        datefmt='%d-%m-%y %H:%M:%S',
        format='[%(asctime)s] - [%(levelname)s] - %(message)s'
    )
    MainUI()

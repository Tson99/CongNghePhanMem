from PIL import Image
import gdown
import yaml
from predictor import Predictor
from vietocr.tool.config import Cfg


class TextRecognition(object):
    def __init__(self, path_to_checkpoint):
        self.config = self.load_config(path_to_checkpoint)
        self.detector = Predictor(self.config)

    def load_config(self, path_to_checkpoint):
        config = Cfg.load_config_from_file('./models/config_text_recognition/config.yml')
        config['cnn']['pretrained'] = False
        config['weights'] = path_to_checkpoint
        config['device'] = 'cpu'
        config['predictor']['beamsearch'] = False
        return config

    @staticmethod
    def download_config(url_id):
        url = 'https://drive.google.com/uc?id={}'.format(url_id)
        output = gdown.download(url, quiet=True)

        with open(output, encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    @staticmethod
    def read_from_config(file_yml):
        with open(file_yml, encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def predict(self, image):
        image = Image.fromarray(image)
        result = self.detector.predict(image)

        return result

    def predict_on_batch(self, batch_images):
        return self.detector.batch_predict(batch_images)

class ConfigAST:
    def __init__(self, conf_path):
        self.text = self.read(conf_path)
        self.configs_dict = {}
        self.read_convert()

    def read_convert(self):
        for line in self.text:
            line = line.strip()
            if line:
                if line.startswith(';'):
                    continue
                if line.startswith('[') and line.endswith(']'):
                    key = line[1:-1]
                    item_dict = {}
                elif '=' in line and '|' in line and key is not '':
                    item_key, item_data = line.split('=')
                    item_value, item_type = item_data.split('|')
                    if item_type == 'str':
                        item_dict[item_key.strip()] = eval('%s("%s")' % (item_type.strip(), item_value.strip()))
                    else:
                        item_dict[item_key.strip()] = eval('%s(%s)' % (item_type.strip(), item_value.strip()))
                else:
                    continue
                self.configs_dict[key] = item_dict
        return self.configs_dict

    def read(self, str_file_path):
        file = open(str_file_path, 'r', encoding='utf-8')
        lines = [line.strip() for line in file.readlines()]
        file.close()
        return lines

    def get_config(self, name):
        return self.configs_dict[name]

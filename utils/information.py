import re
from pyvi import ViUtils

def toString( s, p=''):
    """
    Args:
        s: array
        p: charater special between each element

    Returns: string
    """
    c = ''
    for i in s:
        if i == '':
            continue
        if '-' == i[0]:
            c += '- ' + i[1:].capitalize() + p
        else:
            c += i.capitalize() + p
    return c

"In Line"
def get_inf_cmndbf(lines):
    data = {}
    pos = 0
    for i, line in enumerate(lines):
        if 'SỐ' in line or 'Số' in line:
            c = line.split(' ')
            if len(c) > 1:
                data['so'] = c[1].strip(' ')
            elif re.search('\d', lines[i+1]):
                data['so'] = lines[i+1]
            pos = i
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'tên' in line:
            pos = i
            if ':' not in line:
                line = line.replace('tên', 'tên:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['ht'] = c[1].strip(' ')
            elif not re.search('\d', lines[i - 1]):
                data['ht'] = lines[i - 1]
            if 'Sinh' not in lines[i+1] and not re.search('\d', lines[i + 1]):
                if 'ht' in data:
                    data['ht'] += ' ' + lines[i+1]
                else:
                    data['ht'] = lines[i + 1]
                pos = i+1
                if 'Sinh' not in lines[i + 2] and not re.search('\d', lines[i + 2]):
                    if 'ht' in data:
                        data['ht'] += ' ' + lines[i + 2]
                    else:
                        data['ht'] = lines[i + 2]
                    pos = i + 2
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Sinh ngày' in line:
            pos = i
            if ':' not in line:
                line = line.replace('ngày', 'ngày:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['ns'] = c[1].strip(' ')
            elif re.search('\d', lines[i - 1]):
                data['ns'] = lines[i - 1]
            else:
                data['ns'] = lines[i + 1]
                pos = i+1
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Nguyên quán' in line:
            pos = i
            if 'Sinh ngày' not in lines[i-1] and not re.search('\d', lines[i - 1]):
                data['nq'] = lines[i-1]
            if ':' not in line:
                line = line.replace('Nguyên quán', 'Nguyên quán:')
            c = line.split(':')
            if 'nq' not in data:
                data['nq'] = ''
            if len(c[1]) > 0:
                data['nq'] = c[1].strip(' ')
            else:
                data['nq'] += ' ' + c[1].strip(' ')
            if 'ĐKHK' not in lines[i+1]:
                data['nq'] += ' ' + lines[i + 1]
                pos = i+1
            data['nq'] = data['nq'].strip(' ')
            if len(data['nq'].split(' ')) < 4 and 'ĐKHK' not in lines[i+2]:
                data['nq'] += ' ' + lines[i + 2]
                pos = i + 2
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'ĐKHK' in line:
            if i > pos+1: #and len(data['nq'].split(' ')) > 4
                data['tt'] = lines[pos+1]
            pos = i
            if ':' not in line:
                line = line.replace('thường trú', 'thường trú:')
            if 'tt' not in data:
                data['tt'] = ''
            c = line.split(':')
            data['tt'] += c[1]
            data['tt'] += ' ' + lines[i+1]
            if i+2 < len(lines):
                data['tt'] += ' ' + lines[i+2]

    # data['ns'] = re.sub("[-\sa-zA-Z]", "", data['ns'])
    try:
        data['ns'] = re.sub("[a-zA-Z-/]", '', data['ns'])
        if len(data['ns']) == 7:
            data['ns'] = data['ns'][:2]+'0'+data['ns'][2:]
        if len(data['ns']) > 8:
            data['ns'] = data['ns'][:2]+data['ns'][-6:]
    finally:
        return data

def get_inf_cmndat(lines):
    data = {}
    pos = 0
    if 'Dân' not in lines[0] and 'Dân' not in lines[1]:
        if 'Kinh' in lines[0]:
            data['dt'] = lines[0]
            data['tg'] = lines[1]
        else:
            data['dt'] = lines[1]
            data['tg'] = lines[0]
    else:
        for i, line in enumerate(lines):
            if 'Dân tộc' in line:
                pos = i
                if ':' not in line:
                    line = line.replace('Dân tộc', 'Dân tộc:')
                c = line.split(':')
                if len(c[1]) > 0:
                    data['dt'] = c[1]
                    pos = i
                elif i - 1 == 0:
                    data['dt'] = lines[i-1]
                elif 'Tôn' not in lines[i+1]:
                    data['dt'] = lines[i+1]
                    pos = i + 1
                break
        for i, line in enumerate(lines):
            if i <= pos:
                continue
            if 'Tôn giáo' in line:
                if ':' not in line:
                    line = line.replace('Tôn giáo', 'Tôn giáo:')
                c = line.split(':')
                if len(c[1]) > 0:
                    data['tg'] = c[1].strip(' ')
                elif 'DẤU' not in lines[i+1]:
                    data['tg'] = lines[i + 1]
                else:
                    data['tg'] = lines[i-1]
                break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Sẹo'in line or 'Nốt' in line:
            data['dd'] = line
            if 'Ngày' not in lines[i+1] and not re.search('\d', lines[i+1]):
                data['dd'] += ' ' + lines[i+1]
                if 'Ngày' not in lines[i + 2] and not re.search('\d', lines[i + 2]):
                    data['dd'] += ' ' + lines[i + 2]
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Ngày'in line and 'tháng' in line:
            data['da'] = toString(re.findall('\d', line))
            # if len(data['da'])!=8:

    return data

def get_inf_cc(lines):
    data = {}
    pos = 0
    for i, line in enumerate(lines):
        if 'Số' in line:
            if ':' not in line:
                line = line.replace('Số', 'Số:')
            c = line.split(':')
            if len(c) > 1:
                data['so'] = c[1].strip()
            elif re.search('\d', lines[i + 1]):
                data['so'] = lines[i + 1]
            pos = i
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Họ và tên" in line:
            data['ht'] = lines[i+1]
            pos = i+1
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Ngày, tháng" in line:
            if ':' not in line:
                line = line.replace('Ngày, tháng, năm sinh', 'Ngày, tháng, năm sinh:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['ns'] = c[1].strip()
                pos = i
            else:
                data['ns'] = lines[i+1]
                pos = i+1
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Giới tính' in line:
            if 'Nam' in line:
                data['gt'] = 'Nam'
            else:
                data['gt'] = 'Nữ'
            pos = i
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Quốc tịch' in line:
            if ':' not in line:
                line = line.replace('Quốc tịch', 'Quốc tịch:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['qt'] = c[1].strip()
                pos = i
            else:
                data['qt'] = lines[i + 1]
                pos = i + 1
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Quê quán' in line:
            if i > pos+1:
                data['nq'] = lines[i-1]
            if ':' not in line:
                line = line.replace('Quê quán', 'Quê quán:')
            c = line.split(':')
            if len(c[1]) > 0:
                if 'nq' not in data:
                    data['nq'] = c[1].strip()
                else:
                    data['nq'] += ' ' + c[1].strip()
                pos = i
            if 'Nơi thường' not in lines[i+1]:
                if 'nq' in data and len(data['nq'].split(' ')) > 4:
                    break
                if 'nq' not in data:
                    data['nq'] = lines[i + 1]
                else:
                    data['nq'] += ' ' + lines[i + 1]
                pos = i + 1
                if 'nq' in data and len(data['nq'].split(' ')) > 4:
                    break
                if i+2 < len(lines) and 'Nơi thường' not in lines[i+2] and not re.search("\d", lines[i+2]):
                    data['nq'] += ' ' + lines[i + 2]
                    pos =i + 2
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Nơi thường trú' in line:
            if i > pos+1:
                data['tt'] = lines[i-1]
            if ':' not in line:
                line = line.replace('Nơi thường trú', 'Nơi thường trú:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['tt'] = c[1].strip()
                pos = i
            if 'Có giá trị' not in lines[i + 1]:
                if 'tt' not in data:
                    data['tt'] = lines[i + 1]
                else:
                    data['tt'] += ' ' + lines[i + 1]
                pos = i + 1
                if i+2<len(lines) and 'Có giá trị' not in lines[i+2] and not re.search("\d", lines[i+2]):
                    data['tt'] += ' ' + lines[i + 2]
                    pos = i+2
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if 'Có giá trị đến' in line:
            if ':' not in line:
                line = line.replace('Có giá trị đến', 'Có giá trị đến:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['exp'] = c[1].strip()
                pos = i
            else:
                data['exp'] = lines[i + 1]
                pos = i + 1
            break
    if pos+1 < len(lines):
        data['tt'] += ' ' + lines[pos + 1]
    try:
        data['ns'] = re.sub("[a-zA-Z-/]", '', data['ns'])
        if len(data['ns']) == 7:
            data['ns'] = data['ns'][:2]+'0'+data['ns'][2:]
        if len(data['ns']) > 8:
            data['ns'] = data['ns'][:2]+data['ns'][-6:]
        data['exp'] = re.sub("[a-zA-Z-/]", '', data['exp'])
    finally:
        return data
def get_inf_gplx(lines):
    data = {}
    pos = 0
    for i, line in enumerate(lines):
        if 'No' in line or 'Số' in line:
            if ':' not in line:
                line = line.replace('No', 'No:')
            c = line.split(':')
            if len(c) > 1:
                data['so'] = c[1].strip()
            elif re.search('\d', lines[i + 1]):
                data['so'] = lines[i + 1]
            pos = i
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Full name" in line or'Họ tên' in line:
            pos = i
            if ':' not in line:
                line = line.replace('Full name', 'Full name:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['ht'] = c[1].strip()
            elif 'Birth' not in lines[i+1]:
                data['ht'] = lines[i+1]
                pos = i + 1
            elif not re.search('\d', lines[i-1]):
                data['ht'] = lines[i-1]
            break
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Birth" in line or 'Ngày sinh' in line:
            pos = i
            if ':' not in line:
                line = line.replace('Birth', 'Birth:')
            c = line.split(':')
            if len(c[1])>0:
                data['ns'] = c[1].strip()
            elif re.search('\d', lines[i-1]):
                data['ns'] = lines[i-1]
            elif re.search('\d', lines[i+1]):
                data['ns'] = lines[i + 1]
                pos = i+1
    data['qt'] = 'Việt Nam'
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Address" in line or "Nơi cư" in line:
            pos = i
            if 'VIỆT NAM' not in lines[i-1] and 'Nationality' not in lines[i-1]:
                data['tt'] = lines[i-1]
            if ':' not in line:
                line = line.replace('Address', 'Address:')
            c = line.split(':')
            if len(c[1]) > 0:
                if 'tt' not in data:
                    data['tt'] = c[1].strip()
                else:
                    data['tt'] += ' ' + c[1].strip()
            elif 'month' not in lines[i+1]:
                if 'tt' in data:
                    data['tt'] += ' ' + lines[i + 1]
                else:
                    data['tt'] = lines[i + 1]
                pos = i+1
                if 'month' not in lines[i+2] and not re.search('\d', lines[i+2]):
                    data['tt'] += ' ' + lines[i + 2]
                    pos = i + 2
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Class" in line:
            pos = i
            if ':' not in line:
                line = line.replace('Class', 'Class:')
            c = line.split(':')
            if len(c[1])>0:
                data['class'] = c[1].strip()
    for i, line in enumerate(lines):
        if i <= pos:
            continue
        if "Expires" in line:
            pos = i
            if ':' not in line:
                line = line.replace('Expires', 'Expires:')
            c = line.split(':')
            if len(c[1]) > 0:
                data['exp'] = c[1].strip()
    try:
        data['ns'] = re.sub("[a-zA-Z-/]", '', data['ns'])
        if len(data['ns']) == 7:
            data['ns'] = data['ns'][:2]+'0'+data['ns'][2:]
        if len(data['ns']) > 8:
            data['ns'] = data['ns'][:2]+data['ns'][-6:]
        data['exp'] = re.sub("[-/]", '', data['exp'])
    finally:
        return data
def get_inf_ccs(lines):
    data = {}
    for i, line in enumerate(lines):
         if 'Đặc điểm' in line or 'nhận dạng' in line:
            pos = i
            if ':' not in line:
                 line = line.replace('nhận dạng', 'nhận dạng:')
            if ('Sẹo' in lines[i-1] or 'Nốt' in lines[i-1]):
                data['dd'] = lines[i-1]
            c = line.split(':')
            if len(c[1])>0:
                if 'dd' in data:
                    data['dd'] += ' ' + c[1].strip()
                else:
                    data['dd'] = c[1].strip()
            if 'NGÓN' not in lines[i+1] and 'Ngày' not in lines[i+1]:
                if 'dd' in data:
                    data['dd'] += ' ' + lines[i+1]
                else:
                    data['dd'] = lines[i+1]
                pos = i+1
                if 'NGÓN' not in lines[i+2] and 'Ngày' not in lines[i+2]:
                    data['dd'] += ' ' + lines[i+2]
                    pos = i + 2
            break
    for i, line in enumerate(lines):
        if i< pos:
            continue
        if 'Ngày' in line or 'tháng' in line:
            data['da'] = toString(re.findall('\d', line))
    return data
def get_inf_hc(lines):
    try:
        data = {}
        number_line = 2
        if 'vn' in lines[str(number_line)][0] or 'vnm' in lines[str(number_line)][0] or 'vm' in lines[str(number_line)][0]:
            data['so'] = toString(lines[str(number_line)][1:])
        number_line += 1
        if 'ho' in ViUtils.remove_accents(lines[str(number_line)][0]).decode('utf-8'):
            number_line += 1
            data['ht'] = toString(lines[str(number_line)], ' ').upper()
        number_line += 1
        if 'national' in lines[str(number_line)][2]:
            data['qt'] = toString(lines[str(number_line)][3:5], ' ')
        number_line += 1
        data['ns'] = ''
        for item in lines[str(number_line)]:
            data['ns'] += toString(re.findall("\d", item))
        if data['ns'] == '':
            number_line += 1
            if len(lines[str(number_line)][2]) == 4:
                data['ns'] = toString(lines[str(number_line)][:3])
                data['nq'] = toString(lines[str(number_line)][3:], ' ')
            elif len(lines[str(number_line)][3]) == 4:
                data['ns'] = toString(lines[str(number_line)][:4])
                data['nq'] = toString(lines[str(number_line)][4:],  ' ')
            elif len(lines[str(number_line)][4]) == 4:
                data['ns'] = toString(lines[str(number_line)][:5])
                data['nq'] = toString(lines[str(number_line)][5:],  ' ')
        data['ns'] = re.sub('[/a-zA-Z]', '', data['ns'])
        number_line += 2
        data['gt'] = lines[str(number_line)][0].capitalize()
    except BaseException as e:
        print(e)
    return data
import os
from datetime import datetime
import re
from functools import cmp_to_key
import configparser


def format_lore(text):
    if '<HTML>' in text:
        text = re.sub(r'\n', '', text)
    else:
        text = re.sub(r'\n', '\\\\n', text)
        text = re.sub(r'"', '\\\\"', text)
    return text


white_list = [
    'title',
    'x',
    'y',
    'level',
    'scale',
    'lore'
]

black_list = [
    'id',
    'html'
]


def get_name_index(name):
    try:
        return white_list.index(name)
    except ValueError:
        return -1


def ini_sort(o1, o2):
    o1n = o1[0]
    o2n = o2[0]
    # print(o1n, o2n)
    o1ni = get_name_index(o1n)
    o2ni = get_name_index(o2n)
    # print(o1ni, o2ni)
    if o1ni < 0 and o2ni < 0:
        if o1n == o2n:
            return 0
        return 1 if o1n > o2n else -1
    elif o1ni < 0:
        return 1
    elif o2ni < 0:
        return -1
    return o1ni - o2ni


if __name__ == '__main__':

    area_dir = './Areas/'
    output_file = './AreaLore.lua'

    zone_output_data = []
    area_output_data = []

    zone_count = 0
    area_count = 0

    final_output = ""

    folder_list = os.listdir(area_dir)
    for folder in folder_list:
        if os.path.isdir(area_dir + folder):
            zone_name = folder
            file_list = os.listdir(area_dir + folder)

            zone_parser = configparser.ConfigParser(allow_no_value=True)
            with open(area_dir + folder + '/zone.ini', 'r', encoding='utf-8') as zone_file_data:
                zone_parser.read_string('[DEFAULT]\n' + zone_file_data.read())

            zone_id = zone_parser['DEFAULT']['id']
            if zone_id == '':
                zone_id = 0
            else:
                zone_id = int(zone_id)

            if zone_parser['DEFAULT']['enabled'] == 'no':
                continue

            zone_count += 1
            area_id_list = []

            area_output_data.append("-- %s: %s" % (zone_id, zone_parser['DEFAULT']['name']))

            for file in file_list:
                area_name, ext = os.path.splitext(file)
                if ext == '.txt':
                    file_path = area_dir + folder + '/' + file
                    print("Processing %s - %s" % (zone_name, area_name))
                    with open(file_path, 'r', encoding='utf-8') as file_data:
                        file_data_str = file_data.read()
                        if '-----' in file_data_str:
                            meta_str, lore_str = file_data_str.split('-----')
                            meta_str = meta_str.strip()
                            lore_str = lore_str.strip()
                            parser = configparser.ConfigParser(allow_no_value=True)
                            parser.read_string('[DEFAULT]\n' + meta_str)
                            meta = [x for x in parser['DEFAULT'].items() if x[0] not in black_list]
                            meta.append(('lore', format_lore(lore_str)))
                            meta = sorted(meta, key=cmp_to_key(ini_sort))
                            lua_table_data = []
                            for key, value in meta:
                                value_str = str(value)
                                if not value_str.isdecimal() and value_str[:1] != '{':
                                    value_str = "\"" + value_str + "\""
                                lua_table_data.append("[\"%s\"] = %s" % (key, value_str))

                            point_id = zone_id * 100 + int(parser['DEFAULT']['id'])

                            lua_table_str = ("[%s] = {" % point_id) + (",".join(lua_table_data)) + "}"
                            area_output_data.append(lua_table_str)

                            area_id_list.append(str(point_id))
                            area_count += 1

            zone_data = [
                ('id', zone_id),
                ('continent', zone_parser['DEFAULT']['continent']),
                ('name', zone_parser['DEFAULT']['name']),
                ('pointIds', "{" + (",".join(area_id_list)) + "}")
            ]
            lua_table_data = []
            for key, value in zone_data:
                value_str = str(value)
                if not value_str.isdecimal() and value_str[:1] != '{':
                    value_str = "\"" + value_str + "\""
                lua_table_data.append("[\"%s\"] = %s" % (key, value_str))
            lua_table_str = "{" + (",".join(lua_table_data)) + "}"
            zone_output_data.append(lua_table_str)

    final_output = "\n-- LoreLibrary Area Contents: [%s]\n" % datetime.now().isoformat()
    final_output += "\nlocal _addonName, _addon = ...;\n\nlocal _L = _addon.locals;\n\n_addon.PoI = {\n\t[\"zones\"] = {\n\t\t";
    final_output += ",\n\t\t".join(zone_output_data)
    final_output += "}\n\t,[\"points\"] = {\n\t\t"
    final_output += ",\n\t\t".join(area_output_data)
    final_output += "\n\t}\n}\n"

    with open(output_file, 'w', encoding='utf-8') as output_file_data:
        output_file_data.write(final_output)

    print("Done Compiling %s zones with %s areas" % (zone_count, area_count))

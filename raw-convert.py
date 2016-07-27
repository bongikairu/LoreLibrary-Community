import os
import sys
import re
from functools import cmp_to_key

# LDFLAGS="-L/usr/local/bin/lua" python3 -m pip install lupa==1.3 --no-binary :all:
import lupa
from lupa import LuaRuntime

lua = LuaRuntime()


def format_lore(text):
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'<BR/>', '<BR/>\n', text)
    return text


ini_list = [
    'title',
    'x',
    'y',
]


def get_name_index(name):
    try:
        return ini_list.index(name)
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

    area_dir = './Areas-Raw/'
    output_dir = './Areas/'

    file_list = os.listdir(area_dir)
    for file in file_list:
        if file[0] != '_':
            print('Processing %s' % file)
            zone_name, ext = os.path.splitext(file)
            with open(area_dir + file, 'r', encoding='utf-8') as file_data:
                for line in file_data.readlines():
                    line_cleaned = line.strip()
                    if line_cleaned:
                        lua_str = line_cleaned
                        # print(lua_str)
                        try:
                            data = lua.eval(lua_str)
                            if data:
                                # print([i for i in data.items()])
                                area_name = data.title
                                print("Writing %s - %s" % (zone_name, area_name))
                                if not os.path.isdir(output_dir + zone_name):
                                    os.makedirs(output_dir + zone_name)
                                with open(output_dir + zone_name + '/' + area_name + '.txt', 'w', encoding='utf-8') as output_file_data:
                                    data_list = [d for d in data.items()]
                                    # print(data_list)
                                    data_list = sorted(data_list, key=cmp_to_key(ini_sort))
                                    # print(data_list)
                                    for key, value in data_list:
                                        if key != 'lore':
                                            output_file_data.write('%s=%s\n' % (key, value))
                                    if '<HTML>' in data.lore:
                                        output_file_data.write('html=yes\n')
                                    else:
                                        output_file_data.write('html=no\n')
                                    output_file_data.write('-----\n')
                                    output_file_data.write(format_lore(data.lore))
                        except lupa.LuaSyntaxError:
                            continue

            print("Check Zone file")
            zone_file_name = output_dir + zone_name + '/zone.ini'
            if not os.path.exists(zone_file_name):
                with open(zone_file_name, 'w', encoding='utf-8') as zone_file_data:
                    zone_file_data.write("id=\ncontinent=\nname=%s\npointIds=\nenabled=\n" % zone_name)
            print("File Done")
    print("All Done")

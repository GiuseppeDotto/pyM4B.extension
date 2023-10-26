#! python3

import os
import configparser

def add_settings(content):
    if 'DisableRoomAreaSpaceAutomaticLeader' in content:
        first_half, second_half = content.split('DisableRoomAreaSpaceAutomaticLeader')
        return first_half + 'DisableRoomAreaSpaceAutomaticLeader=1' +\
        second_half[second_half.index('\n'):]
    else:
        return content.replace('[Misc]', '[Misc]\nDisableRoomAreaSpaceAutomaticLeader=0')

folder = os.getenv('APPDATA')
folder = os.path.join(folder, 'Autodesk', 'Revit')

for dirpath, dirnames, filenames in os.walk(folder):
    for f in filenames:
        if f == 'Revit.ini':

            file_path = os.path.join(dirpath, f)

            with open(file_path, 'r', encoding='utf-16') as f:
                content = f.read()
                new_text = add_settings(content)
            with open(file_path, 'w', encoding='utf-16') as f:
                f.write(new_text)
                print(f'EDIT: {file_path}')

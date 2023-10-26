
import os

folder = os.path.dirname(__file__)

enum = 0
addition = '-----'
for dirpath, dirnames, filenames in os.walk(folder):
    
    for d in dirnames:
        complete_dir = os.path.join(dirpath, d)
        os.rename(complete_dir, complete_dir.replace(addition,''))
        print(f'{complete_dir}{addition}')
        enum += 1

    #     if enum == 50:  break
    # if enum == 50:  break
print(enum)

import os


def rename_nested(folder, addition, enum):
    for dirpath, dirnames, filenames in os.walk(folder):
        for d in dirnames:
            complete_dir = os.path.join(dirpath, d)
            # new_path = complete_dir+addition
            new_path = complete_dir.replace(addition,'')
            os.rename(complete_dir, new_path)
            enum += 1
            rename_nested(new_path, addition, enum)
        break


folder = os.path.dirname(__file__)

enum = 0
addition = '-----'

rename_nested(folder, addition, enum)

print(enum)
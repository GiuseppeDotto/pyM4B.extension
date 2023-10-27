
import os

def rename_nested(folder, suffix, enum, add=True):
    """
    Order to follow to solve the case-sensitive issue:
        1. run the function with add=True
        2. commit the changes
        3. run the function with add=False
        4. commit for the last time

    Args:
        folder (str): the main folder to rename, with the nested as well
        suffix (str): the unique string to add/remove from the path
    """
    for dirpath, dirnames, filenames in os.walk(folder):
        for d in dirnames:
            complete_dir = os.path.join(dirpath, d)
            if add:
                new_path = complete_dir+suffix
            else:
                new_path = complete_dir.replace(suffix,'')
            os.rename(complete_dir, new_path)
            enum += 1
            rename_nested(new_path, suffix, enum)
        break

folder = os.path.dirname(__file__)

enum = 0
suffix = '-----'

# rename_nested(folder, suffix, enum)
rename_nested(folder, suffix, enum, add=False)
print(f'{enum} folders renamed successfully.')

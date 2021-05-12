import os
import uuid
import random
import hashlib
from nose.tools import nottest

def format_timestamp_gui(timestamp):
    """
    Given a DateTime object, returns a properly 
    formatted timestamp to be shown on the GUI.
    """
    return timestamp.strftime('%Y-%m-%d %H:%M')

def join_file_path(*args):
    """
    Preprocesses the given values and runs them through os.path.join.
    """
    args = list(args)
    if args[0] == '':
        args[0] = '/'
    for i in range(1, len(args)): # First value can start with /
        args[i] = args[i].strip('/')
    return os.path.join(*args)

def remove_prefix(string, prefix):
    """
    Removes a prefix from the string, if it exists.
    """
    # print("Attempting to remove prefix {} from string {}".format(prefix, string))
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string[:]

@nottest
def create_test_files(path, file_count):
    """
    Generates new random empty files/folders to the given path.
    File_count specifies how many files/folders will be generated
    in total.
    """
    prefix = str(uuid.uuid4()).split("-")[0]
    random_files = [prefix + "_" + str(i) for i in range(0, file_count)]
    if len(random_files) != len(set(random_files)): ## If collissions, try again
        create_test_files(path, file_count)
        return
    cur_f = path
    for random_file in random_files:
        is_dir = random.randint(0, 1)
        if is_dir:
            cur_f = os.path.join(cur_f, random_file + "_DIRECTORY")
            if not os.path.exists(cur_f):
                os.mkdir(cur_f)
        else:
            open(os.path.join(cur_f, random_file + "_FILE"), 'w').write(random_file)


def path_to_folders(path):
    """
    Given a path to folder, returns a list of paths of each folder in the original path.
    """
    folders = []
    while path:
        folders.append(path)
        path = path.rsplit('/', 1)[0]
    return folders


def calculate_checksum(path):
    """
    Calculates a MD5 hash of the file at the given path.
    """
    if os.path.isdir(path):
        return '0'
    else:
        content = open(path, 'rb').read()
        checksum = hashlib.md5()
        checksum.update(content)
        checksum = checksum.hexdigest()
        return checksum


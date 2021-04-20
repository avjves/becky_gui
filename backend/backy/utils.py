import os

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

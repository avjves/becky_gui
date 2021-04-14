def format_timestamp_gui(timestamp):
    """
    Given a DateTime object, returns a properly 
    formatted timestamp to be shown on the GUI.
    """
    return timestamp.strftime('%Y-%m-%d %H:%M')

import logging

def get_logger(name=None):
    root_logger_name = 'combine'

    # Build the name of the sub-logger
    if name:
        name = root_logger_name + '.' + name
    else:
        name = root_logger_name

    root_logger = logging.getLogger(root_logger_name)  

    # If the root logger has no handlers, add them
    # in any case return the sub-logger
    if root_logger.handlers:
        return logging.getLogger(name)
    else:
        root_logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler() # default to sys.stderr
        ch.setLevel(logging.DEBUG) # todo: make it configurable
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
        return logging.getLogger(name)
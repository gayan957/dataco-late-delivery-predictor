import logging #record events that happen while your program runs.

def get_logger(name: str) -> logging.Logger: # give hint return value is a logging.Logger object.
    logger = logging.getLogger(name)
    # level is INFO/DEBUG/WARNING/ERROR/CRITICAL, the logger will display
    logger.setLevel(logging.INFO)

    #Without this check, Python would add another console handler and another file handler.
    if not logger.handlers:
        # create Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(ch)

        #create File handler
        fh = logging.FileHandler("pipeline.log")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(fh)

    return logger
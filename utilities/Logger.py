from datetime import datetime
from sys import stdout


def log(text):
    stdout.write('%s - %s\n' % (datetime.now(), text))
    stdout.flush()
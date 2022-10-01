import os
import pathlib
import datetime

PATH = pathlib.Path(__file__).parent.absolute()
VERSION_PATH = os.path.join(PATH, 'VERSION')
TEMPLATE_PATH = os.path.join(PATH, 'template.svg')

MONTH_NAMES = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'Mai',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}


def get_version():
    with open(VERSION_PATH) as file:
        content = file.read()
        return content.replace(' ', '').replace('\n', '')


def timedelta_string(time_delta: datetime.timedelta,
                     clip_seconds: bool = True) -> str:
    string = str(time_delta)

    if clip_seconds:
        string = string[:-3]

    if string[0] != '0':
        string = '0' + string

    return string

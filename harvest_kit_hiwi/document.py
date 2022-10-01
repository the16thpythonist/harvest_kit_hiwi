from typing import List, Dict

import svgutils.transform as sg

from harvest_kit_hiwi.util import TEMPLATE_PATH
from harvest_kit_hiwi.util import timedelta_string
from harvest_kit_hiwi.processing import TimeSpan, ArbeitszeitData


def create_azd_svg(azd_data: ArbeitszeitData,
                   output_path: str,
                   template_path: str = TEMPLATE_PATH):
    fig = sg.fromfile(template_path)

    # ~ Filling in the static data
    txt_month = sg.TextElement(600, 142, str(azd_data.month), size=15)
    txt_year = sg.TextElement(690, 142, str(azd_data.year), size=15)
    txt_name = sg.TextElement(390, 172, str(azd_data.name), size=15)
    txt_id = sg.TextElement(390, 204, str(azd_data.personnel_number), size=15)
    txt_institute = sg.TextElement(390, 236, str(azd_data.institute), size=15)
    txt_time = sg.TextElement(390, 270, str(azd_data.working_hours), size=15)
    txt_rate = sg.TextElement(650, 270, str(azd_data.hourly_rate), size=15)

    fig.append([txt_month, txt_year, txt_name, txt_id, txt_institute, txt_time, txt_rate])

    # ~ Filling in the time spans into the table
    size = 12
    x_description = 72
    x_date = 275
    x_begin = 375
    x_end = 475
    x_working_time = 680
    y = 363
    delta_y = 19.4
    for ts in azd_data.time_spans:
        txt_description = sg.TextElement(x_description, y, ts.description, size=size)

        string_date = ts.start_datetime.strftime('%d.%m.%Y')
        txt_date = sg.TextElement(x_date, y, string_date, size=size)

        string_begin = ts.start_datetime.strftime('%H:%M')
        txt_begin = sg.TextElement(x_begin, y, string_begin, size=size)

        string_end = ts.end_datetime.strftime('%H:%M')
        txt_end = sg.TextElement(x_end, y, string_end, size=size)

        string_working_time = timedelta_string(ts.time_delta)
        txt_working_time = sg.TextElement(x_working_time, y, string_working_time, size=size)

        fig.append([txt_description, txt_date, txt_begin, txt_end, txt_working_time])

        y += delta_y

    # ~ Filling in the static data at the bottom of the table
    txt_leave = sg.TextElement(680, 848, '04:00', size=size)
    string_sum = timedelta_string(azd_data.total_time_delta)
    txt_sum = sg.TextElement(680, 848 + delta_y, string_sum, size=size)
    txt_carry_before = sg.TextElement(680, 848 + delta_y * 2, '00:00', size=size)
    txt_carry_after = sg.TextElement(680, 848 + delta_y * 3, '00:00', size=size)

    fig.append([txt_leave, txt_sum, txt_carry_before, txt_carry_after])

    fig.save(output_path)
    return fig

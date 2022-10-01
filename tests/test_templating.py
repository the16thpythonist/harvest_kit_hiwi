import unittest
import os
from collections import namedtuple

import cairosvg
import svgutils.transform as sg

from .util import ASSETS_PATH


class Size:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class TestSvgManipulation(unittest.TestCase):

    svg_path = os.path.join(ASSETS_PATH, 'out.svg')
    pdf_path = os.path.join(ASSETS_PATH, 'out.pdf')

    def setUp(self) -> None:
        if os.path.exists(self.svg_path):
            os.remove(self.svg_path)

        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)

    def test_writing_text(self):
        fig = sg.SVGFigure(width=Size(100), height=Size(100))
        txt = sg.TextElement(10, 10, "Hello World", size=12, weight="bold")
        fig.append([txt])
        fig.save(self.svg_path)
        self.assertTrue(os.path.exists(self.svg_path))

        # Now we need to convert it to PDF with cairo
        with open(self.svg_path, mode='rb') as svg_file, open(self.pdf_path, mode='wb') as pdf_file:
            content = svg_file.read()
            pdf_content = cairosvg.svg2pdf(bytestring=content)
            pdf_file.write(pdf_content)

        self.assertTrue(os.path.exists(self.pdf_path))

    def test_loading_template_and_converting_to_pdf(self):
        template_path = os.path.join(ASSETS_PATH, 'template.svg')
        fig = sg.fromfile(template_path)
        fig.save(self.svg_path)
        self.assertTrue(os.path.exists(self.svg_path))

        with open(self.svg_path, mode='rb') as svg_file, open(self.pdf_path, mode='wb') as pdf_file:
            content = svg_file.read()
            pdf_content = cairosvg.svg2pdf(bytestring=content)
            pdf_file.write(pdf_content)

        self.assertTrue(os.path.exists(self.pdf_path))

    def test_writing_into_template(self):
        template_path = os.path.join(ASSETS_PATH, 'template.svg')
        fig = sg.fromfile(template_path)

        # Here we try to add some basic information as text to the template
        # All of these are for the header which has fixed positions
        txt_month = sg.TextElement(600, 142, '10', size=15)
        txt_year = sg.TextElement(690, 142, '2022', size=15)
        txt_name = sg.TextElement(390, 172, 'Max Mustermann', size=15)
        txt_id = sg.TextElement(390, 204, '1982907', size=15)
        txt_institute = sg.TextElement(390, 236, 'Karlsruher Institut für Technologie', size=15)
        txt_time = sg.TextElement(390, 270, '12.5h', size=15)
        txt_rate = sg.TextElement(650, 270, '11.5€', size=15)

        fig.append([txt_month, txt_year, txt_name, txt_id, txt_institute, txt_time, txt_rate])

        # This next section is an attempt to procedurally fill the actual working timetable
        x_description = 72
        x_date = 275
        x_begin = 375
        x_end = 475
        x_working_time = 680
        y = 363
        for i in range(24):
            txt_description = sg.TextElement(x_description, y, 'description', size=12)
            txt_date = sg.TextElement(x_date, y, '01.01.2001', size=12)
            txt_begin = sg.TextElement(x_begin, y, '09:00', size=12)
            txt_end = sg.TextElement(x_end, y, '17:00', size=12)
            txt_working_time = sg.TextElement(x_working_time, y, '08:00', size=12)

            fig.append([txt_description, txt_date, txt_begin, txt_end, txt_time, txt_working_time])
            y += 19.4

        # And now in the end we fill in the fixed positions for the working time total etc.
        txt_vacation = sg.TextElement(680, 848, '04:00', size=12)
        txt_sum = sg.TextElement(680, 848 + 19.4, '40:00', size=12)
        txt_carry_before = sg.TextElement(680, 848 + 19.4 * 2, '00:00', size=12)
        txt_carry_after = sg.TextElement(680, 848 + 19.4 * 3, '00:00', size=12)

        fig.append([txt_vacation, txt_sum, txt_carry_before, txt_carry_after])

        fig.save(self.svg_path)
        self.assertTrue(os.path.exists(self.svg_path))

        with open(self.svg_path, mode='rb') as svg_file, open(self.pdf_path, mode='wb') as pdf_file:
            content = svg_file.read()
            pdf_content = cairosvg.svg2pdf(bytestring=content)
            pdf_file.write(pdf_content)

        self.assertTrue(os.path.exists(self.pdf_path))


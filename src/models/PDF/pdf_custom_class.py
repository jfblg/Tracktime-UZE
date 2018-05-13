import datetime
import os
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        #self.cell(15)
        # Title
        self.cell(0, 10, 'UZE Sprinter {}'.format(PDF.get_calendar_year()), 0, 0, 'L')
        # Logo
        self.image(PDF.get_logo_path(), 150, 8, 33)
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Seite ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def category_title(self, category_name):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Title
        self.cell(0, 10, 'Kategorie: {}'.format(category_name), 0, 0, 'L')
        # Line break
        self.ln(4)

    def result_records(self, records):
        # Times 12
        self.set_font('Courier', '', 10)
        for position, last_name, first_name, time in records:
            self.cell(0, 10, '{} - {} - {} - {}'.format(position, last_name, first_name, time), 0, 0, 'L')

    def startlist_records(self, records):
        pass

    def print_result_category(self, category_name, records=[]):
        self.add_page()
        self.category_title(category_name)
        #self.result_records(records)

    def print_startlist_category(self, category_name, records=[]):
        self.add_page()
        self.category_title(category_name)
        self.startlist_records(records)

    @staticmethod
    def get_logo_path():
        logo_filename = "lcuzwil-logo.png"
        return os.path.abspath(os.path.join(os.getcwd(), "static", "pdf", logo_filename))

    @staticmethod
    def get_calendar_year():
        now = datetime.datetime.now()
        return now.year
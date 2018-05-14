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
        # problem with printing out of 'ä', therefore
        category_name = category_name.replace(u'\u0308', 'e').encode()
        self.set_font('Arial', '', 12)
        self.cell(0, 5, 'Kategorie:', 0, 1, 'L')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, category_name.decode("latin-1"), 0, 1, 'L')
        # Line break
        self.ln(4)

    def result_records(self, records):
        # Times 12
        # print header of the table
        self.set_font('Courier', 'B', 10)
        self.cell(0, 5, '{:10}{:20}{:20}{:20}'.format("#", "Nachname", "Vorname", "Zeit"), 0, 1, 'L')
        self.set_font('Courier', '', 10)
        for position, last_name, first_name, time in records:
            print(position, last_name, first_name, time)
            self.cell(0, 5, '{:10}{:20}{:20}{:20}'.format(position, last_name, first_name, time), 0, 1, 'L')

    def startlist_all_records(self, records):
        pass

    def print_result_category(self, category_name, records=[]):
        self.add_page()
        self.category_title(category_name)
        self.result_records(records)

    def print_result_all_category(self, input_data):
        '''
        Process input_data
        :param input_data: dictionary - key: category name, value: tuple with results in format
        (position, last_name, first_name, time) - all strings
        '''
        for category, results in input_data.items():
            self.print_result_category(category, results)

    def print_startlist_all_category(self, category_name, records=[]):
        self.category_title(category_name)
        self.startlist_all_records(records)

    @staticmethod
    def get_logo_path():
        logo_filename = "lcuzwil-logo.png"
        return os.path.abspath(os.path.join(os.getcwd(), "static", "pdf", logo_filename))

    @staticmethod
    def get_calendar_year():
        now = datetime.datetime.now()
        return now.year
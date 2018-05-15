import xlrd
from os import remove
from os.path import join, abspath, dirname, isfile
from src.models.participants.participants import ParticipantModel

from pprint import pprint

# TODO implemented checks are buggy and not complete. If you have time, implement more precise checks and error handling


class MassImport:

    @staticmethod
    def insert_many(path_to_file):
        """ Insert loaded data to the db
        """

        if isfile(path_to_file):
            loaded_data = MassImport.read_wb(path_to_file)

            for item in loaded_data:
                record = ParticipantModel(**item)
                record.save_to_db()
            remove(path_to_file)
            return True
        else:
            return False


    @staticmethod
    def read_wb(wb_path):
        """Load participants data from xls data
        """
        keys = "last_name first_name gender year".split(" ")
        loaded_data = []

        xl_workbook = xlrd.open_workbook(wb_path)
        xl_sheet = xl_workbook.sheet_by_index(0)

        header_list = [item.value.lower() for item in xl_sheet.row(0)]

        indexes = {}

        indexes["last_name"] = MassImport.get_last_name_column_index(header_list)
        indexes["first_name"] = MassImport.get_first_name_column_index(header_list)
        indexes["gender"] = MassImport.get_gender_column_index(header_list)
        indexes["year"] = MassImport.get_year_column_index(header_list)
        # TODO add check if all indexes are different from each other

        for row_idx in range(1, xl_sheet.nrows):
            row_values = [item.value for item in xl_sheet.row(row_idx)]
            # converting year from float to int

            cleaned_row_values = []
            # list must contain values with following indexes
            # 0 - last name / string
            # 1 - first name / string
            # 2 - gender: either "boy" or "girl" / string
            # 3 - year / integer.

            cleaned_row_values.append(row_values[indexes["last_name"]])
            cleaned_row_values.append(row_values[indexes["first_name"]])
            cleaned_gender = MassImport.clean_gender_value(row_values[indexes["gender"]])
            cleaned_row_values.append(cleaned_gender)
            cleaned_year = MassImport.clean_year_value(row_values[indexes["year"]])
            cleaned_row_values.append(cleaned_year)

            # pprint(row_values)
            # pprint(cleaned_row_values)

            values = dict(zip(keys, cleaned_row_values))
            loaded_data.append(values)

        return loaded_data

    @staticmethod
    def clean_gender_value(input_value):
        if "boy" in input_value.lower():
            return "boy"
        if "knabe" in input_value.lower():
            return "boy"
        if "girl" in input_value.lower():
            return "girl"
        if "mädchen" in input_value.lower():
            return "girl"
        if "dchen" in input_value.lower():
            return "girl"

        return None

    @staticmethod
    def clean_year_value(input_value):
        if isinstance(input_value, float):
            return int(input_value)
        if isinstance(input_value, int):
            return input_value
        if isinstance(input_value, str) and "/" in input_value.lower():
            return int(input_value.split("/")[0])
        if isinstance(input_value, str):
            return input_value
        return None

    @staticmethod
    def get_last_name_column_index(header):
        for i in range(0, len(header)):
            if "nachname" in header[i]:
                return i
            if "nach" in header[i]:
                return i
            if "last" in header[i]:
                return i

        return None

    @staticmethod
    def get_first_name_column_index(header):
        for i in range(0, len(header)):
            if "vorname" in header[i]:
                return i
            if "vor" in header[i]:
                return i
            if "first" in header[i]:
                return i

        return None

    @staticmethod
    def get_gender_column_index(header):
        for i in range(0, len(header)):
            if "knabe" in header[i]:
                return i
            if "dchen" in header[i]:
                return i
            if "geschlecht" in header[i]:
                return i
            if "sex" in header[i]:
                return i
            if "gender" in header[i]:
                return i
        return None

    @staticmethod
    def get_year_column_index(header):
        for i in range(0, len(header)):
            if "jahrgang" in header[i]:
                return i
            if "jahr" in header[i]:
                return i
            if "year" in header[i]:
                return i

        return None

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']

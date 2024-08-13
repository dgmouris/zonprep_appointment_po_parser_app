import os
import pprint
import pdfplumber
import json

class TypeAPDFParser: 
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_data = None # data straight from the PDF
        self.clean_data = {} # data that has been cleaned from the pdf

    def __str__(self):
        return f"TypeAPDFParser({self.pdf_path})"

    '''
    Full extraction of text from the PDF

    Returns:
    {
        "appointment_data": {...}
        "po_data": {...}
    }
    '''
    def extract_text(self):
        self.pdf_data = self._parse_pdf()
        self.clean_json_data = self._extract_pdf_data_to_clean_data()
        return self.clean_data
    
    '''
    This is going to parse the pdf and return a list of tables.
    '''
    def _parse_pdf(self):
        pdf_tables_data = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    pdf_tables_data.append(table)
        return pdf_tables_data
    
    def _extract_pdf_data_to_clean_data(self):
        self.clean_data["appointment_data"] = self._get_appointment_data()
        self.clean_data["po_data"] = self._get_po_data()

    '''
    This is going to get the appointment data first table in the PDF.
    '''
    def _get_appointment_data(self):
        APPOINTMENT_TABLE_INDEX = 0
        
        # the keys where to find the data in the table.
        DATA_KEY_INDEX = 0
        DATA_VALUE_INDEX = 1
        
        # Get the first table
        first_table = self.pdf_data[APPOINTMENT_TABLE_INDEX]
        appointment_data = {}
        for row in first_table:
            key = row[DATA_KEY_INDEX]
            value = row[DATA_VALUE_INDEX]
            appointment_data[key] = value
        
        return appointment_data
    
    '''
    This is going to get the PO data from every table after the first table in the PDF.
    '''
    def _get_po_data(self):
        PO_TABLE_INDEX_START = 1

        po_table = self.pdf_data[PO_TABLE_INDEX_START:]

        HEADER_TABLE_INDEX = 0
        HEADER_ROW_INDEX = 0

        # the key is the index of the column in the table.
        # the value is a dictionary, name is the name of the column, type is the type of the column.
        # type can be a string which is just the value as is.
        # type can be a list which is a list of values which need to be split with a comma.
        PO_COLUMN_MAPPING = {
            0: {
                "name": "shipment_id",
                "type": "string"
            },
            1: {
                "name": "pallets",
                "type": "string"
            },
            2: {
                "name": "cartons",
                "type": "string"
            },
            3: {
                "name": "units",
                "type": "string"
            },
            4: {
                "name": "pos", # list of pos
                "type": "list"
            },
            5: {
                "name": "pro",
                "type": "string"
            },
            6: {
                "name": "bols",
                "type": "list"
            },
            7: {
                "name": "ASNs", # list of pos
                "type": "list"
            },
            8: {
                "name": "ARN",
                "type": "string"
            },
            9: {
                "name": "freight_terms",
                "type": "string"
            },
            10: {
                "name": "vendor",
                "type": "string"
            },
            11: {
                "name": "shipment_label",
                "type": "string"
            }
        }


        po_rows = []
        for table_index, table in enumerate(po_table):
            for row_index, row in enumerate(table):
                # handle the header row and skip it.
                if row_index == HEADER_ROW_INDEX and table_index == HEADER_TABLE_INDEX:
                    continue           
                row_data = {}
                for column_index, column_data in enumerate(row):
                    if column_index not in PO_COLUMN_MAPPING.keys():
                        continue
                    column_mapping = PO_COLUMN_MAPPING[column_index]
                    column_name = column_mapping["name"]

                    if column_mapping["type"] == "string":
                        row_data[column_name] = self._clean_pdf_string_data(column_data)
                    elif column_mapping["type"] == "list":
                         row_data[column_name] =  self._clean_pdf_string_data(column_data).split(",")

                po_rows.append(row_data)
        return po_rows        


    '''
    Remove all of the escape characters from the string.
    '''
    def _clean_pdf_string_data(self, value):
        if value is None:
            return ""
        escape_characters = "\n\t\r\b\f\v\\\'\"" # characters to escape
        translation_table = str.maketrans('', '', escape_characters)
        cleaned_string = value.translate(translation_table)

        return cleaned_string
    

    def save_json(self, file_path):
        json_output = json.dumps(self.clean_data, indent=4)
        
        with open(file_path, 'w+') as json_file:
            json_file.write(json_output)
import easyocr
import json
import pprint


class TypeCImageParser:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image_data = None # data straight from the image
        self.clean_data = None # image for mthe

    '''
    Full Extraction of the data from the image

    // will take shape of the following.
    [
        {
            "cols_0": {
                "value": "DAMALD",
                "x_min": 1262,
                "x_max": 1422
            },
            "cols_1": {
                "value": "LAALCTLD",
                "x_min": 1492,
                "x_max": 1676
            },
        },
    ]

    The data from the above will be 3 rows in total for each sku
        - row 1:
            cols_0 to cols_9 or cols_10
            - have most of the data.
        - row 2: last to match col with x_min and x_max
            cols_0
                - units for last cols_3 of last row
            cols_1
                - date for cols_
            cols_2
                - date
        - row 3
            prep details which will be it's own thing.
    '''
    def extract_text(self):
        return self.extract_table()


    def extract_table(self):
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'], gpu=False)

        # Extract text from the image
        result = reader.readtext(self.image_path)


        # Extract text coordinates
        # Assuming the table cells are arranged in a grid pattern
        boxes = []
        for item in result:
            coordinates = item[0]
            value = item[1]
            confidence = item[2]
            top_left = coordinates[0]
            top_right = coordinates[1]
            bottom_right = coordinates[2]
            bottom_left = coordinates[3]
            boxes.append({
                "coordinates": (top_left, top_right, bottom_right, bottom_left),
                "value": value,
                "confidence": confidence,
            })

        rows = self.extract_human_readable_table(boxes)

        self.clean_data = rows
        return rows

    @staticmethod
    def get_xmin(box):
        return min(box[0][0], box[1][0], box[2][0], box[3][0])

    # Define a function to sort values within each array based on xmin coordinate
    @staticmethod
    def sort_values_by_xmin(array):
        return sorted(array, key=lambda x: TypeCImageParser.get_xmin(x['coordinates']))

    @staticmethod
    def extract_human_readable_table( data):
        # Lightly working
        # # Extracting coordinates and values
        coordinates = [entry['coordinates'] for entry in data]
        values = [entry['value'] for entry in data]
        # breakpoint()
        # Extracting ymin and ymax separately
        ymin_coordinates = [min(point[0][1], point[1][1], point[2][1], point[3][1]) for point in coordinates]
        ymax_coordinates = [max(point[0][1], point[1][1], point[2][1], point[3][1]) for point in coordinates]


        # Sorting based on ymin-coordinates to group into rows
        sorted_indices = sorted(range(len(ymin_coordinates)), key=lambda k: ymin_coordinates[k])

        # Organizing values into rows and columns
        organized_values = []
        current_row_values = []
        prev_ymax = ymin_coordinates[sorted_indices[0]]

        for i, index in enumerate(sorted_indices):
            ymin = ymin_coordinates[index]
            ymax = ymax_coordinates[index]

            if ymin > prev_ymax:
                organized_values.append(current_row_values)
                current_row_values = []

            current_row_values.append({
                "coordinates": coordinates[index],
                "value": values[index]
            })
            prev_ymax = ymax

        # Append the last row
        organized_values.append(current_row_values)

        # Printing the organized values
        pprint.pprint(organized_values)

        # sort each row by y-coordinate
        end_rows = []
        for array in organized_values:
            sorted_values = TypeCImageParser.sort_values_by_xmin(array)
            row = {}
            for i, value in enumerate(sorted_values):

                # the values are already organized by row,
                # give the xmin and xmax so that further rows can be
                # grouped together
                # take a look at the coordinates section above.
                x_min = int(value["coordinates"][0][0])
                x_max = int(value["coordinates"][1][0])
                row[F'cols_{i}'] = {
                    "value": value['value'],
                    "x_min": x_min,
                    "x_max": x_max,
                }
            end_rows.append(row)

        return end_rows

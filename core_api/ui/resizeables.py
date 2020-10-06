from Qt import QtWidgets


class ResizeableTableWidget(QtWidgets.QTableWidget):
    def __init__(self, width=150, min=50, max=750):
        self.column_width = width
        self.column_width_multiplier = float()
        self.column_width_slider = QtWidgets.QHorizontalSlider()
        self.column_width_slider.setMinimum(1)
        self.column_width_slider.setMinimum(100)

    def resize(self):
        pass

    def smart_resize(self, use_max=False, use_mode=True):
        """
        :param use_max: bool use the largest/widest key in the column as the width for the entire column
        Resizes the column based on the mode width of all the columns in the table. (ie. if 85% of columns are 150,
        then we will set the width of that column to 150.
        :return:
        """
        column_data = dict()
        for row in self.rowCount():
            for col in self.columnCount():
                if row not in column_data.keys():
                    column_data[col] = len(str(self.item(row, col).text()))
                else:
                    column_data.update({col: len(str(self.item(row, col).text))})

        for col in self.columnCount():
            if use_max:
                self.setColumnWidth(row, max(column_data[col].values()))
            if use_mode:
                self.setColumnWidth(max(set(column_data[col]), key=column_data[col].count))

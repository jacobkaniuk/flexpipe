import os
from conf import get_database_prefix_address
import csv


def remove_namespaces(item):
    if not isinstance(item, dict):
        raise TypeError("Could not remove namespaces from item(s). Expecting type: {} Got: {}".format(
            dict, type(item)))

    no_namespace_dict = dict()
    for key, value in item.items():
        key = str(key).rsplit('__')[-1]
        no_namespace_dict[key] = value
    return no_namespace_dict


def generate_relative_path(asset):
    """
    Generates a db relative path to an asset from asset info. ie. flex:\\test_project\ENV_TEST\PROP_HAMMER_A\model\4
    :param asset: BaseAsset asset we want to get the path to
    :return: str platform specific path to provided asset
    """

    return "{}{}{sep}{}{sep}{}{sep}{}".format(get_database_prefix_address(),
                                              asset.get_asset_project(),
                                              asset.get_asset_shot(),
                                              asset.get_asset_name() + '_' +
                                              asset.get_asset_type_suffix(),
                                              asset.get_asset_version(), sep=os.path.sep)


def unpack_csv(csv_file, mode='r', output_path=None, output_function=None):
    """
    Utility function to create a list of key value pairs for items in a CSV file. Useful for bulk read/write operations.
    :param csv_file: str path to input CSV file
    :param mode: str file mode to open file in ie. with open(file, mode)
    :param output_path: str path to output file if we want to modify/create new data
    :param output_function: func function we want to run our input data through before (re)writing it
    :return: list key value pairs (dict) for items in a CSV file
    """

    file_modes =            ['r', 'r+', 'rb', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+']
    writable_file_modes =   ['r+', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+']
    excel_extensions =      ['.xls', '.xlsb', '.xlsm', '.xlsx', '.xlt', '.xltx']

    # check to make
    if not os.path.exists(os.path.realpath(csv_file)):
        raise OSError("Path provided does not exist. Please check and try again...\n")

    if os.path.splitext(os.path.realpath(csv_file))[-1] in excel_extensions:
        raise ValueError("File provided is a Microsoft Excel file. Please convert to CSV format first and try again.")

    if not os.path.splitext(os.path.realpath(csv_file))[-1] == '.csv':
        raise ValueError("File provided is not a CSV file or does not have .csv extension. "
                         "Please provide a valid csv file.")

    if mode not in file_modes:
        raise ValueError("Provided file mode invalid. Please check mode and try again. "
                         "Supported modes: {} ".format(','.join(file_modes)))

    with open(csv_file, mode=mode) as input_file:
        input_reader = csv.DictReader(input_file)
        input_data   = [i for i in input_reader]

        for item in input_data:
            for key, value in item.items():
                if value == 'NULL':
                    del item[key]

        if output_path:
            if not os.path.exists(os.path.dirname(output_path)):
                raise OSError("Parent path to output file provided does not exist. Please check and try again...\n")
            if mode not in writable_file_modes:
                raise ValueError(
                    "Output file path provided but file mode is read-only. Please provide a writable file mode"
                    "and try again.")
            if output_function is not None:
                csv.DictWriter(output_path, output_function(input_data))
            else:
                csv.DictWriter(output_path, input_data)

        return input_data



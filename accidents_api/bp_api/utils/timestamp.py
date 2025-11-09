from datetime import datetime


def generate_timestamp(date_string):
    """
    Convert a date in dd.mm.yyyy format into a Unix timestamp in milliseconds.

    :param date_string: Date as a string in the format dd.mm.yyyy
    :return: Unix timestamp in milliseconds (int)
    """
    try:
        date_object = datetime.strptime(date_string, "%d.%m.%Y")
        timestamp_ms = int(date_object.timestamp() * 1000)
        return timestamp_ms
    except ValueError:
        return "Invalid date format. Please use dd.mm.yyyy."

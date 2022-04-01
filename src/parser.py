import datetime

from src.day_template import month_dict, day_dict


def parser(received_datetime: str):
    try:
        today_year = datetime.datetime.now().year
        split_datetime = received_datetime.split(' ')
        split_datetime.remove('в') if 'в' in split_datetime else None
        if split_datetime[1] in month_dict:
            converted_month = month_dict[split_datetime[1].lower()]
            converted_datetime = f'{today_year}-{converted_month}-{split_datetime[0]} {split_datetime[-1]}:00'

        else:
            converted_month = day_dict[split_datetime[0].lower()]
            converted_datetime = f'{today_year}-{converted_month.month}-{converted_month.day} {split_datetime[-1]}:00'
        if datetime.datetime.strptime(converted_datetime, '%Y-%m-%d %H:%M:%S') >= datetime.datetime.now():
            return converted_datetime
        else:
            return False
    except:
        return False

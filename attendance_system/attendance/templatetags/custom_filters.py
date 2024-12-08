from django import template
from itertools import groupby
from operator import itemgetter

register = template.Library()

@register.filter(name='max_record')
def max_record(records, roll_number):
    try:
        roll_number = str(roll_number)

        # Group records by roll number and get the record with the maximum attendance percentage
        records_by_roll = {
            str(k): max(group, key=itemgetter('attendance_percentage'))
            for k, group in groupby(
                sorted(records, key=itemgetter('roll_number')), 
                key=itemgetter('roll_number')
            )
        }

        return records_by_roll.get(roll_number)

    except Exception as e:
        print(f"Detailed Max Record Filter Error: {e}")
        import traceback
        traceback.print_exc()
        return None

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

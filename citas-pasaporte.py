import requests
import json
import datetime
import calendar


def get_appointment_dates(start_date,end_date):
    headers = {
        'referer': 'https://www.citaconsular.es/'
    }
    params = (
        ('callback', ''),
        ('type', 'default'),
        ('publickey', '28e1e70e15c0c9e53c7ee319e97281d07'),
        ('lang', 'es'),
        ('services[]', 'bkt968275'),
        ('agendas[]', 'bkt332409'),
        ('src', 'https://www.citaconsular.es/es/hosteds/widgetdefault/28e1e70e15c0c9e53c7ee319e97281d07#services'),    
        ('start', '2023-04-01'),
        ('end', '2023-04-30'),
    )

    response = requests.get('https://www.citaconsular.es/onlinebookings/datetime/', headers=headers, params=params)
    return json.loads(response.content[10:-2])


def last_day_of_month(date):
    _, last_day = calendar.monthrange(date.year, date.month)
    return date.replace(day=last_day)

def first_day_of_month(date):
    return date.replace(day=1)


def first_day_of_next_month(date):
    return (date.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

def date_to_yyyymmdd(date):
    return date.strftime('%Y-%m-%d')

today = datetime.date.today()
a = first_day_of_month(today)
b = first_day_of_next_month(a)
c = first_day_of_next_month(b)

dates = [(date_to_yyyymmdd(x), date_to_yyyymmdd(last_day_of_month(x))) for x in [a,b,c]]

result = []
for start,end in dates:
    print(start,end)
    data = get_appointment_dates(start,end)
    result += [(slot['date'], len(slot['times'])) for slot in data['Slots'] if slot['times']]
    for r in result:
        print(r)
    




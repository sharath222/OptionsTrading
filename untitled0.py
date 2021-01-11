# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 13:19:56 2020

@author: chand
"""

from datetime import date

dt = "2021 Aug 6 04:50:03.131192"

_year, _month, _date, _time = dt.split(" ")


month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
Nmonth = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

for i in range(len(month)):
    for j in range(len(Nmonth)):
        if _month == month[i]:
            _month = Nmonth[j]

_year = int(_year)
_month = int(_month)
_date = int(_date)
# _time = float(_time)


# ttlDate = date(_year, _month, _date)

# from datetime import datetime

# datetime_str = '09 Jan 18 13:55:26.155661'

# datetime_object = datetime.strptime(datetime_str, '%d %b %y %H:%M:%S.%f')

# print(datetime_object)

# from datetime import datetime

# datetime_str = '2021 Jan 6 13:55:26.155661'

# datetime_object = datetime.strptime(datetime_str, '%Y %b %d %H:%M:%S.%f')

# print(datetime_object)

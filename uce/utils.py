#!/usr/bin/env python
# encoding: utf-8

import datetime
from uce.libs import Course, Event


# convert Course instance to  event
def course2event(course_list, start_date):
    START_DATE = start_date
    class_duration = 45  # how long a class last
    class_interval_mini = 5  # short braek between the same class
    time_list = ['0830', '0920', '1020', '1110', '1430', '1520', '1620', '1720', '1930', '2020', '2110',
                 '2200']  # when each class begins
    week_list = ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')
    unit_count = 12
    event_list = list()

    for course in course_list:
        start_date = START_DATE
        start_time = ''
        end_time = ''
        byday = ''
        remind_time = 15  # default set to 15 min
        valid_weeks = list(course.valid_weeks)
        count = 0
        interval = 0
        location = course.room_name
        summary =course.teacher_name+' '+course.course_name
        description = ''

        # calculate count
        start_week = valid_weeks.index('1') - 1
        start_date = datetime.datetime.strftime(datetime.datetime.strptime(start_date, "%Y%m%d") + datetime.timedelta(
            days=7) * start_week + datetime.timedelta(days=1) * int(course.index[0] / 12), "%Y%m%d")
        # calculate interval, assume that intervals are the same
        for i in range(start_week + 1, len(valid_weeks) - 1):
            if valid_weeks[i] == '1':
                interval = i - start_week - 1
                break
        # format start_time and end_time
        index = course.index
        byday = week_list[int(index[0] / unit_count)]  # calculate byday
        class_count = len(index)
        start_time = time_list[int(index[0] % unit_count)]
        last_time = class_duration * class_count + class_interval_mini * (class_count - 1)
        end_time = datetime.datetime.strftime(
            (datetime.datetime.strptime(start_time, "%H%M") + datetime.timedelta(minutes=last_time)), "%H%M")
        start_time = start_date + 'T' + start_time + '00'
        end_time = start_date + 'T' + end_time + '00'

        event_list.append(
            Event(start_time, end_time, interval, count, byday, description, location, summary, remind_time))

    return event_list

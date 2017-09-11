#!/usr/bin/env python
# encoding: utf-8
import re
import requests
from bs4 import BeautifulSoup


class Course(object):
    def __init__(self, teacher_id, teacher_name, course_id, course_name, room_id, room_name, valid_weeks, index):
        # type: (string, string, string, string, string, string, string, index) -> None
        super(Course, self).__init__()
        self.teacher_id = teacher_id
        self.teacher_name = teacher_name
        self.course_id = course_id
        self.course_name = course_name
        self.room_id = room_id
        self.room_name = room_name
        self.valid_weeks = valid_weeks
        self.index = index

    def to_list(self):
        l = list()
        l.append(self.teacher_id)
        l.append(self.teacher_name)
        l.append(self.course_id)
        l.append(self.course_name)
        l.append(self.room_id)
        l.append(self.room_name)
        l.append(self.valid_weeks)
        l.append(self.index)
        return l


class Event(object):
    def __init__(self, start_time, end_time, interval, count, byday, description, location, summary, remind_time):
        super(Event, self).__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self.count = count
        self.byday = byday
        self.description = description
        self.location = location
        self.summary = summary
        self.remind_time = remind_time


class CourseSpider(object):
    def __init__(self):
        super(CourseSpider, self).__init__()
        self.session = None  # session
        self.login_url = "http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F"  # login url
        self.logout_url = "http://eams.uestc.edu.cn/eams/logout.action?jsdEkingstar=1&redirect=http%3A%2F%2Fportal.uestc.edu.cn%2Flogout.portal"
        self.course_table_url = "http://eams.uestc.edu.cn/eams/courseTableForStd.action"  # course table url
        self.course_data_url = "http://eams.uestc.edu.cn/eams/courseTableForStd!courseTable.action" #course data query url
        self.login_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
            "Content - Type": "application / x - www - form - urlencoded"}  # request headers
        self.login_payload = {  # payload with out username and password
            "dllt": "userNamePasswordLogin",
            "_eventId": "submit",
            "rmShown": "1"
        }

        self.data_query_url = "http://eams.uestc.edu.cn/eams/dataQuery.action"
        self.date_query_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
            "Content - Type": "application / x - www - form - urlencoded",
            "X-Requested-With": "XMLHttpRequest"}

    # login
    def login(self, username, password):
        is_login = False  #
        self.login_payload['username'] = username
        self.login_payload['password'] = password
        self.session = requests.session()

        # get dynamic login args
        login_page = self.session.get(self.login_url)
        soup = BeautifulSoup(login_page.text, 'lxml')
        # add dynamic args to login_payload
        self.login_payload["lt"] = soup.find('input', {'name': 'lt'}).get('value')
        self.login_payload["execution"] = soup.find('input', {'name': 'execution'}).get('value')

        # login
        login_result_page = self.session.post(self.login_url, self.login_payload, self.login_header)
        # print(login_result_page.text)
        if "电子科技大学信息门户" in login_result_page.text:
            is_login = True
        return is_login

    # parse course,return a list of courses
    def parse_course(self, query_year, semester, ):
        index = list()  # course index
        parsedCourse = list()  # Course instance
        ids = ''  # a dynamic argument maybe,i don't know what it is but necesary,maybe differs from student to student
        semester_code = ''  # a specific code for each semester of a specific year
        course_table_page = self.session.get(self.course_table_url)
        if "重复登录" in course_table_page.text:
            course_table_page = self.session.get(self.course_table_url + ";jsessionid=" + str(
                self.session.cookies.get(name="JESSIONID", domain="eams.uestc.edu.cn")))
        ids = re.findall(r"ids.*", course_table_page.text)[0].split("\"")[2]

        semester_code_page = self.session.post(self.data_query_url, {"dataType": "semesterCalendar"},
                                               self.date_query_header)
        # print(semester_code_page.text)
        semester_code = \
            re.findall(r"\{id:\w+,schoolYear:\"" + str(query_year) + "\",name:\"" + str(semester),
                       semester_code_page.text)[
                0].split(":")[1].split(",")[0]
        # print(semester_code)
        # print(ids)
        course_table_data = self.session.post(self.course_data_url, {"ignoreHead": "1",
                                                                     "setting.kind": "std",
                                                                     "startWeek": "1",
                                                                     "semester.id": semester_code,
                                                                     "ids": ids}, self.date_query_header)
        self.session.get(self.logout_url)  # logout
        self.session.close()

        soup = BeautifulSoup(course_table_data.text, 'lxml')
        courses = re.findall(r"\(\"[0-9,?]+\",.*\)", soup.text)
        # print(soup.text)
        # parse and calculate course index(a number deciding where the course is in the course table)
        unitCount = 12  # number of the row of the course table,needed for eval(formula parsed from course_page)

        all_activity = re.findall(r"activity\s=[\s\S]*table0.marshalTable\(2,1,20\);", soup.text)
        all_activity = all_activity[0][:-len("table0.marshalTable(2,1,20);")].strip()
        activities = all_activity.split('activity =')

        for i in activities:
            if i == '':
                activities.remove(i)
        for i in activities:
            index.append(re.findall(r"index\s=[0-9]+\*unitCount\+[0-9]+", i))  # get index formula

        for i in index:
            for j in i:
                i[i.index(j)] = eval(j.split('=')[1])  # calculate index

        # craete Courses instance list
        for i in courses:
            divided = i[1:-1].split("\"")
            for j in divided:
                if j == '' or j == ',':
                    divided.remove(j)
            courses[courses.index(i)] = divided

        for i in range(0, len(courses)):
            parsedCourse.append(
                Course(courses[i][0], courses[i][1], courses[i][2], courses[i][3], courses[i][4], courses[i][5],
                       courses[i][6], index[i]))

        return parsedCourse


class ICS(object):
    def __init__(self):
        super(ICS, self).__init__()
        self.header = "BEGIN:VCALENDAR\n" \
                      "PRODID:-//Google Inc//Google Calendar 70.9054//EN\n" \
                      "VERSION:2.0\nCALSCALE:GREGORIAN\n" \
                      "METHOD:PUBLISH\n" \
                      "X-WR-TIMEZONE:Asia/Shanghai\n" \
                      "BEGIN:VTIMEZONE\n" \
                      "TZID:Asia/Shanghai\n" \
                      "X-LIC-LOCATION:Asia/Shanghai\n" \
                      "BEGIN:STANDARD\n" \
                      "TZOFFSETFROM:+0800\n" \
                      "TZOFFSETTO:+0800\n" \
                      "TZNAME:CST\n" \
                      "DTSTART:19700101T000000\n" \
                      "END:STANDARD\n" \
                      "END:VTIMEZONE\n"

        self.event = "BEGIN:VEVENT\n" \
                     "DTSTART;TZID=Asia/Shanghai:%s\n" \
                     "DTEND;TZID=Asia/Shanghai:%s\n" \
                     "RRULE:FREQ=WEEKLY;INTERVAL=%d;COUNT=%d;BYDAY=%s\n" \
                     "DESCRIPTION:%s\n" \
                     "LOCATION:%s\n" \
                     "SEQUENCE:0\n" \
                     "STATUS:CONFIRMED\n" \
                     "SUMMARY:%s\n" \
                     "TRANSP:OPAQUE\n" \
                     "BEGIN:VALARM\n" \
                     "ACTION:DISPLAY\n" \
                     "DESCRIPTION:This is an event reminder\n" \
                     "TRIGGER:-P0DT0H%dM0S\n" \
                     "END:VALARM\nEND:VEVENT\n"

        self.tail = "END:VCALENDAR"

    def generate_ics(self, event_list):
        vcalendar = self.header
        for event in event_list:
            vcalendar = vcalendar + (self.event % (event.start_time,
                                                   event.end_time,
                                                   event.interval,
                                                   event.count,
                                                   event.byday,
                                                   event.description,
                                                   event.location,
                                                   event.summary,
                                                   event.remind_time))

        vcalendar = vcalendar + self.tail

        return vcalendar

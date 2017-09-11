#!/usr/bin/env python
# encoding: utf-8
import getpass
from uce.libs import CourseSpider, ICS
import uce.utils as utils


def main():
    print('导出电子科技大学本科生的课表为日历文件，导入该文件到某邮箱账号即可，推荐outlook或gmail')
    username = input('学号: ')
    query_year = input('学年(eg:2017-2018): ')
    start_date = input('开始上课日期(eg:20170904): ')
    semester = input('学期(1/2): ')
    password = getpass.getpass('密码: ')

    spider = CourseSpider()
    if spider.login(username, password):
        print("登录成功，开始获取课表信息")
        course_list = spider.parse_course(query_year, semester)
        if len(course_list) > 0:
            print('获取课表信息完毕：')
            for i in course_list:
                print(i.to_list())

            f = ICS()
            event_list = utils.course2event(course_list, start_date)
            ics = f.generate_ics(event_list)

            f_path = username + '_' + query_year + '_' + str(semester) + '.ics'
            print('ics日历文件保存在：./' + f_path)

            with open(f_path, 'w') as output_file:
                output_file.write(ics)
        else:
            print('获取课表信息失败')
    else:
        print('登录失败')
        exit()


if __name__ == '__main__':
    main()

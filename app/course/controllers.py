# -*- coding:utf-8 -*-
import xlwt
from StringIO import StringIO
from datetime import datetime
from flask import request, send_file
from flask.ext.security import roles_accepted, login_required, current_user
from app.utils.api import BaseResource
from app.utils.validate import PhoneParam, StringParam, DateParam
from app import errorcode, RoleType
from app.utils.excel import set_style
from app.utils.utils import page_total
from .models import CourseApply, CourseTable, StudyFeedback
from app.user_system.models import User, Role, role_user_relationship, user_datastore


class CourseResource(BaseResource):
    def post(self, action=None):
        if action == 'apply':
            return self.add_source_apply()
        self.bad_request(errorcode.BAD_REQUEST)

    def get(self, action=None):
        if action == 'apply_info':
            return self.get_course_apply()
        self.bad_request(errorcode.BAD_REQUEST)

    def delete(self, action=None):
        if action == 'apply_info':
            return self.delete_course_apply()
        self.bad_request(errorcode.BAD_REQUEST)

    def add_source_apply(self):
        parser = self.get_parser()
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('teacher', type=StringParam.check, required=False, location='json', min=1, max=20,
                            default='')
        ca = CourseApply()
        ca.phone = self.get_param('phone')
        ca.name = self.get_param('name')
        ca.teacher = self.get_param('teacher')
        ca.save()
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def get_course_apply(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        page, page_size = self.get_params('page', 'page_size')
        total, items = CourseApply.get_all(page, page_size)
        datas = []
        for item in items:
            data = {
                'id': item.id,
                'phone': item.phone,
                'name': item.name,
                'teacher': item.teacher,
                'create_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            datas.append(data)
        return {
            'page': page,
            'page_total': page_total(total, page_size),
            'items': datas,
        }

    @roles_accepted(RoleType.admin)
    def delete_course_apply(self):
        parser = self.get_parser()
        parser.add_argument('apply_ids', type=str, required=True, location='args')
        try:
            apply_ids = self.get_param('apply_ids').split(',')
            apply_ids = [int(i) for i in apply_ids]
        except:
            self.bad_request(errorcode.BAD_REQUEST)
        for apply_id in apply_ids:
            case = CourseApply.get(id=apply_id)
            if case:
                case.delete()
        return self.ok('ok')


class CourseTB(BaseResource):
    def post(self, action=None):
        return self.add_course_table()

    def get(self, action=None):
        if action == 'tables':
            return self.get_course_table()
        elif action == 'students':
            return self.get_students()
        elif action == 'teachers':
            return self.get_teachers()
        elif action == 'available_teacher':
            return self.get_available_teacher()
        self.bad_request(errorcode.BAD_REQUEST)

    def put(self, action=None):
        return self.update_course_table()

    @roles_accepted(RoleType.admin)
    def delete(self, action=None):
        parser = self.get_parser()
        parser.add_argument('table_id', type=int, required=True, location='args')
        tb = CourseTable.get(id=self.get_param('table_id'))
        if tb:
            tb.delete()
        return self.ok('ok')

    @login_required
    def get_course_table(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != user.id:
            if not current_user.has_role(RoleType.admin):
                self.unauthorized(errorcode.UNAUTHORIZED)
            user = User.get(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        tbs = []
        if user.has_role(RoleType.teacher):
            tbs = CourseTable.get_all(teacher_id=user.id)
        elif user.has_role(RoleType.student):
            tbs = CourseTable.get_all(student_id=user.id)
        items = []
        for tb in tbs:
            data = {
                'id': tb.id,
                'day': tb.day,
                'start_time': tb.start_time,
                'stop_time': tb.stop_time,
                'course_name': tb.course_name,
            }
            if user.has_role(RoleType.teacher):
                data['chinese_name'] = User.get(id=tb.student_id).chinese_name
            else:
                data['chinese_name'] = User.get(id=tb.teacher_id).chinese_name
            items.append(data)
        return items

    @roles_accepted(RoleType.admin)
    def get_students(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        parser.add_argument('key', type=StringParam.check, required=False, location='args', min=1, max=20)
        page, page_size, key = self.get_params('page', 'page_size', 'key')
        total, users = user_datastore.get_users(RoleType.student, page, page_size, 'enabled', key)
        items = []
        for user in users:
            tbs = CourseTable.query.filter_by(student_id=user.id).\
                order_by(CourseTable.update_time.desc()).paginate(1, 1).items
            status = u'已创建' if len(tbs) != 0 else u'未创建'
            update_time = tbs[0].update_time.strftime('%Y-%m-%d') if len(tbs) != 0 else ''
            data = {
                'id': user.id,
                'chinese_name': user.chinese_name,
                'course_name': user.student.course_name,
                'study_country': user.student.study_country,
                'location': user.student.location,
                'learn_range': user.student.learn_range,
                'phone': user.phone,
                'status': status,
                'create_time': user.create_time.strftime('%Y-%m-%d'),
                'update_time': update_time,
            }
            items.append(data)
        return {
            'page_total': page_total(total, page_size),
            'page': page,
            'items': items,
        }

    @roles_accepted(RoleType.admin)
    def get_teachers(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        parser.add_argument('key', type=StringParam.check, required=False, location='args', min=1, max=20)
        page, page_size, key = self.get_params('page', 'page_size', 'key')
        total, users = user_datastore.get_users(RoleType.teacher, page, page_size, 'enabled', key)
        items = []
        for user in users:
            tbs = CourseTable.query.filter_by(teacher_id=user.id).\
                order_by(CourseTable.update_time.desc()).paginate(1, 1).items
            status = u'已创建' if len(tbs) != 0 else u'未创建'
            update_time = tbs[0].update_time.strftime('%Y-%m-%d') if len(tbs) != 0 else ''
            data = {
                'id': user.id,
                'chinese_name': user.chinese_name,
                'status': status,
                'update_time': update_time,
            }
            items.append(data)
        return {
            'page_total': page_total(total, page_size),
            'page': page,
            'items': items,
        }

    @roles_accepted(RoleType.admin)
    def get_available_teacher(self):
        parser = self.get_parser()
        parser.add_argument('day', type=int, required=True, location='args')
        parser.add_argument('start_time', type=str, required=True, location='args')
        parser.add_argument('stop_time', type=str, required=True, location='args')
        day, start_time, stop_time = self.get_params('day', 'start_time', 'stop_time')
        user_ids = self._get_not_available_user_ids(day, start_time, stop_time, RoleType.teacher)
        users = User.query.join(role_user_relationship, Role).\
            filter(Role.name == RoleType.teacher).filter(User.id.notin_(user_ids)).all()
        items = []
        for user in users:
            data = {
                'id': user.id,
                'chinese_name': user.chinese_name,
            }
            items.append(data)
        return items

    @roles_accepted(RoleType.admin)
    def add_course_table(self):
        parser = self.get_parser()
        parser.add_argument('course_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('teacher_user_id', type=int, required=True, location='json')
        parser.add_argument('student_user_id', type=int, required=True, location='json')
        parser.add_argument('day', type=int, required=True, location='json')
        parser.add_argument('start_time', type=str, required=True, location='json')
        parser.add_argument('stop_time', type=str, required=True, location='json')
        course_name, teacher_id, student_id = \
            self.get_params('course_name', 'teacher_user_id', 'student_user_id')
        if not User.get(id=teacher_id) or not User.get(id=student_id):
            self.bad_request(errorcode.BAD_REQUEST)
        day, start_time, stop_time = self.get_params('day', 'start_time', 'stop_time')
        user_ids = self._get_not_available_user_ids(day, start_time, stop_time)
        if teacher_id in user_ids or student_id in user_ids:
            self.bad_request(errorcode.BAD_REQUEST_USER_CONFLICT)
        tb = CourseTable()
        tb.course_name = course_name
        tb.teacher_id = teacher_id
        tb.student_id = student_id
        tb.start_time = start_time
        tb.stop_time = stop_time
        tb.day = day
        if stop_time.startswith('10'):
            tb.time_type = 1
        elif stop_time.startswith('12'):
            tb.time_type = 2
        elif stop_time.startswith('15'):
            tb.time_type = 3
        elif stop_time.startswith('17'):
            tb.time_type = 4
        elif stop_time.startswith('21'):
            tb.time_type = 5
        else:
            tb.time_type = 6
        tb.save()
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def update_course_table(self):
        parser = self.get_parser()
        parser.add_argument('table_id', type=int, required=True, location='args')
        parser.add_argument('course_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('teacher_user_id', type=int, required=True, location='json')
        tb_id = self.get_param('table_id')
        course_name, teacher_id = self.get_params('course_name', 'teacher_user_id')
        tb = CourseTable.get(id=tb_id)
        if not tb:
            self.bad_request(errorcode.NOT_FOUND)
        if not User.get(id=teacher_id):
            self.bad_request(errorcode.BAD_REQUEST)
        user_ids = self._get_not_available_user_ids(tb.day, tb.start_time, tb.stop_time, RoleType.teacher)
        if teacher_id in user_ids:
            self.bad_request(errorcode.BAD_REQUEST_USER_CONFLICT)
        tb.course_name = course_name
        tb.teacher_id = teacher_id
        tb.update_time = datetime.now()
        tb.save()

    def _get_not_available_user_ids(self, day, start, stop, role_name=None):
        tbs = CourseTable.query.filter_by(day=day, start_time=start, stop_time=stop).all()
        if not tbs:
            return []
        teacher_ids = []
        student_ids = []
        for tb in tbs:
            teacher_ids.append(tb.teacher_id)
            student_ids.append(tb.student_id)
        teacher_ids = list(set(teacher_ids))
        student_ids = list(set(student_ids))
        if role_name == RoleType.teacher:
            user_ids = teacher_ids
        elif role_name == RoleType.student:
            user_ids = student_ids
        else:
            user_ids = teacher_ids + student_ids
        return user_ids


class Feedback(BaseResource):
    @roles_accepted(RoleType.admin)
    def post(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        fb = StudyFeedback()
        fb.student_id = self.get_param('user_id')
        return self.set_feedback(parser, fb)

    @roles_accepted(RoleType.admin)
    def put(self):
        parser = self.get_parser()
        parser.add_argument('fb_id', type=int, required=True, location='args')
        fb = StudyFeedback.get(id=self.get_param('fb_id'))
        if not fb:
            self.bad_request(errorcode.NOT_FOUND)
        return self.set_feedback(parser, fb)

    @login_required
    def get(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=False, location='args')
        user_id = self.get_param('user_id')
        if user_id:
            return self.get_feedback(parser, user_id)
        else:
            return self.get_student(parser)

    @roles_accepted(RoleType.admin)
    def delete(self):
        parser = self.get_parser()
        parser.add_argument('fb_id', type=int, required=False, location='args')
        parser.add_argument('user_id', type=int, required=False, location='args')
        fb_id = self.get_param('fb_id')
        user_id = self.get_param('user_id')
        if fb_id:
            fb = StudyFeedback.get(id=self.get_param('fb_id'))
            if fb:
                fb.delete()
        elif user_id:
            user = User.get(id=user_id)
            if user.has_role(RoleType.student):
                for fb in user.student.feedbacks:
                    fb.delete()
        return self.ok('ok')

    def get_student(self, parser):
        self.add_pagination_args(parser)
        page, page_size = self.get_params('page', 'page_size')
        total, users = user_datastore.get_users(RoleType.student, page, page_size, 'enabled')
        items = []
        for user in users:
            q = StudyFeedback.query.filter_by(student_id=user.id)
            count = q.count()
            fbs = q.order_by(StudyFeedback.study_date.desc()).paginate(1, 1).items
            update_time = fbs[0].update_time.strftime('%Y-%m-%d') if count != 0 else ''
            data = {
                'id': user.id,
                'chinese_name': user.chinese_name,
                'course_name': user.student.course_name,
                'school': user.student.school,
                'location': user.student.location,
                'learn_range': user.student.learn_range,
                'phone': user.phone,
                'create_time': user.create_time.strftime('%Y-%m-%d'),
                'update_time': update_time,
                'count': count,
            }
            items.append(data)
        return {
            'page_total': page_total(total, page_size),
            'page': page,
            'items': items,
        }

    def get_feedback(self, parser, user_id):
        self.add_pagination_args(parser)
        page, page_size = self.get_params('page', 'page_size')
        q = StudyFeedback.query.filter_by(student_id=user_id)
        total = q.count()
        fbs = q.order_by(StudyFeedback.study_date.desc()).paginate(page, page_size).items
        items = []
        for fb in fbs:
            data = {
                'id': fb.id,
                'chinese_name': fb.chinese_name,
                'study_date': fb.study_date.strftime('%Y-%m-%d'),
                'class_time': fb.class_time,
                'study_time': fb.study_time,
                'course_name': fb.course_name,
                'section': fb.section,
                'contents': fb.contents,
                'homework': fb.homework,
                'feedback': fb.feedback,
            }
            items.append(data)
        return {
            'page_total': page_total(total, page_size),
            'page': page,
            'items': items,
        }

    def set_feedback(self, parser, fb):
        parser.add_argument('chinese_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('study_date', type=DateParam.check, required=True, location='json')
        parser.add_argument('class_time', type=str, required=True, location='json')
        parser.add_argument('study_time', type=str, required=True, location='json')
        parser.add_argument('course_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('section', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('contents', type=StringParam.check, required=True, location='json', min=1, max=50)
        parser.add_argument('homework', type=StringParam.check, required=True, location='json', min=1, max=75)
        parser.add_argument('feedback', type=StringParam.check, required=True, location='json', min=1, max=125)
        fb.chinese_name = self.get_param('chinese_name')
        fb.study_date = self.get_param('study_date')
        fb.class_time = self.get_param('class_time')
        fb.study_time = self.get_param('study_time')
        fb.course_name = self.get_param('course_name')
        fb.section = self.get_param('section')
        fb.contents = self.get_param('contents')
        fb.homework = self.get_param('homework')
        fb.feedback = self.get_param('feedback')
        fb.update_time = datetime.now()
        fb.save()
        return self.ok('ok')


@login_required
def export_course_table():
    try:
        user_id = request.args['user_id']
        user_id = int(user_id)
        user = User.get(id=user_id)
        if not user:
            raise
    except:
        BaseResource.bad_request(errorcode.BAD_REQUEST)
    if not user.has_role(RoleType.student) or user.has_role(RoleType.teacher):
        BaseResource.bad_request(errorcode.BAD_REQUEST)
    wb = export_course_tb(user)
    output = StringIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype='application/octet-stream',
                     attachment_filename='课程表.xls', as_attachment=True)


@login_required
def export_studt_feedback():
    try:
        user_id = request.args['user_id']
        user_id = int(user_id)
        user = User.get(id=user_id)
        if not user:
            raise
    except:
        BaseResource.bad_request(errorcode.BAD_REQUEST)
    if not user.has_role(RoleType.student):
        BaseResource.bad_request(errorcode.BAD_REQUEST)
    wb = export_feedback(user)
    output = StringIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype='application/octet-stream',
                     attachment_filename='学习反馈.xls', as_attachment=True)


def export_course_tb(user, sheetname='课程表', wb=None):
    if not wb:
        wb = xlwt.Workbook()
    sheet = wb.add_sheet(sheetname.decode('utf-8'))
    row1 = [u'节次', u'时间', u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期天']
    column1 = [u'上午', u'上午', u'下午', u'下午', u'晚上']
    column2 = [u'8:30-10:00', u'10:00-12:00', u'13:30-15:30', u'15:30-17:30', u'19:00-21:00']
    for i in range(1, 9):
        sheet.col(i).width = 256*18
    for i in range(0, len(row1)):
        sheet.write(0, i, row1[i], set_style())
    for i in range(0, len(column1)):
        sheet.write(i+1, 0, column1[i], set_style())
        sheet.write(i+1, 1, column2[i], set_style())
    if user.has_role(RoleType.student):
        tbs = CourseTable.get_all(student_id=user.id)
    elif user.has_role(RoleType.teacher):
        tbs = CourseTable.get_all(teacher_id=user.id)
    for tb in tbs:
        row = tb.day + 1
        col = tb.time_type
        if user.has_role(RoleType.student):
            lable = '%s\n%s' % (tb.course_name, User.get(id=tb.teacher_id).chinese_name)
        elif user.has_role(RoleType.teacher):
            lable = '%s\n%s' % (tb.course_name, User.get(id=tb.student_id).chinese_name)
        sheet.write(col, row, lable, set_style())
    return wb


def export_feedback(user, sheetname='学习反馈', wb=None):
    if not wb:
        wb = xlwt.Workbook()
    q = StudyFeedback.query.filter_by(student_id=user.id)
    fbs = q.order_by(StudyFeedback.study_date.desc()).all()
    column0 = [u'中文名称', u'上课时间', u'课程类型']
    column2 = [u'日期', u'学习时间', u'授课范围']
    for fb in fbs:
        study_date = fb.study_date.strftime('%Y-%m-%d')
        sheetname = sheetname + study_date
        sheet = wb.add_sheet(sheetname.decode('utf-8'))
        column1 = [user.chinese_name, fb.class_time, fb.course_name]
        column3 = [study_date, fb.study_time, fb.section]
        for i in range(0, 4):
            sheet.col(i).width = 256 * 18
        for i in range(0, len(column0)):
            sheet.write(i, 0, column0[i], set_style())
            sheet.write(i, 1, column1[i], set_style())
            sheet.write(i, 2, column2[i], set_style())
            sheet.write(i, 3, column3[i], set_style())
        sheet.write_merge(4, 7, 0, 3, u'课程内容:\n%s' % fb.contents, set_style(horz_center=False))
        sheet.write_merge(8, 11, 0, 3, u'课后作业:\n%s' % fb.homework, set_style(horz_center=False))
        sheet.write_merge(12, 15, 0, 3, u'课堂反馈:\n%s' % fb.feedback, set_style(horz_center=False))
    return wb
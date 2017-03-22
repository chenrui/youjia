from flask.ext.security import roles_accepted
from app.utils.api import BaseResource
from app.utils.validate import PhoneParam
from app import errorcode, RoleType
from .models import CourseApply, Course, CourseTable
from app.user_system.models import User


class CourseResource(BaseResource):
    def post(self, action=None):
        if action == 'apply':
            return self.add_source_apply()
        elif action == 'add':
            return self.add_course()
        self.bad_request(errorcode.BAD_REQUEST)

    def get(self, action=None):
        if action == 'apply_info':
            return self.get_course_apply()
        self.bad_request(errorcode.BAD_REQUEST)

    def delete(self, action=None):
        return self.delete_course()

    def add_source_apply(self):
        parser = self.get_parser()
        parser.add_argument('course_id', type=int, required=True, location='json')
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        course_id, phone = self.get_params('course_id', 'phone')
        if not Course.get(id=course_id):
            self.bad_request(errorcode.BAD_REQUEST)
        ca = CourseApply()
        ca.course_id = course_id
        ca.phone = phone
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
                'phone': item.phone,
                'course_name': item.course.name,
                'create_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            datas.append(data)
        return {
            'total': total,
            'items': datas,
        }

    @roles_accepted(RoleType.admin)
    def add_course(self):
        return []

    @roles_accepted(RoleType.admin)
    def delete_course(self):
        parser = self.get_parser()
        parser.add_argument('course_id', type=int, required=True, location='args')
        course = Course.get(id=self.get_param('course_id'))
        if course:
            course.delete()
        return self.ok('ok')


class CourseTB(BaseResource):
    def post(self):
        return self.add_course_table()

    @roles_accepted(RoleType.admin)
    def add_course_table(self):
        parser = self.get_parser()
        parser.add_argument('course_id', type=int, required=True, location='json')
        parser.add_argument('teacher_user_id', type=int, required=True, location='json')
        parser.add_argument('student_user_id', type=int, required=True, location='json')
        # parser.add_argument('start_time', type=str, required=True, location='json')
        # parser.add_argument('stop_time', type=str, required=True, location='json')
        course_id, teacher_id, student_id = \
            self.get_params('course_id', 'teacher_user_id', 'student_user_id')
        if not Course.get(id=course_id) or not User.get(id=teacher_id) or not User.get(id=student_id):
            self.bad_request(errorcode.BAD_REQUEST)
        tb = CourseTable()
        tb.course_id = course_id
        tb.teacher_id = teacher_id
        tb.student_id = student_id
        tb.save()
        return self.ok('ok')

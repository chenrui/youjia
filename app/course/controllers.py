from flask.ext.security import roles_accepted, login_required, current_user
from app.utils.api import BaseResource
from app.utils.validate import PhoneParam
from app import errorcode, RoleType
from .models import CourseApply, Course, CourseTable
from app.user_system.models import User, Role, role_user_relationship


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
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        phone = self.get_param('phone')
        ca = CourseApply()
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
    def post(self, action=None):
        return self.add_course_table()

    def get(self, action=None):
        if action == 'tables':
            return self.get_course_table()
        elif action == 'available_teacher':
            return self.get_available_teacher()

    def put(self, action=None):
        return self.update_course_table()

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
            tbs = user.teacher.course_tables
        elif user.has_role(RoleType.student):
            tbs = user.student.course_tables
        items = []
        for tb in tbs:
            data = {
                'id': tb.id,
                'day': tb.day,
                'start_time': tb.start_time,
                'stop_time': tb.stop_time,
                'course_name': tb.course.name,
            }
            if user.has_role(RoleType.teacher):
                data['user'] = User.get(id=tb.student_id).email
            else:
                data['user'] = User.get(id=tb.teacher_id).email
            items.append(data)
        return items

    @roles_accepted(RoleType.admin)
    def get_available_teacher(self):
        parser = self.get_parser()
        parser.add_argument('day', type=int, required=True, location='args')
        parser.add_argument('start_time', type=int, required=True, location='args')
        parser.add_argument('stop_time', type=int, required=True, location='args')
        day, start_time, stop_time = self.get_params('day', 'start_time', 'stop_time')
        user_ids = self._get_not_available_user_ids(day, start_time, stop_time, RoleType.teacher)
        users = User.query.join(role_user_relationship, Role).\
            filter(Role.name == RoleType.teacher).filter(User.id.notin_(user_ids)).all()
        items = []
        for user in users:
            data = {
                'id': user.id,
                'email': user.email,
            }
            items.append(data)
        return items

    @roles_accepted(RoleType.admin)
    def add_course_table(self):
        parser = self.get_parser()
        parser.add_argument('course_id', type=int, required=True, location='json')
        parser.add_argument('teacher_user_id', type=int, required=True, location='json')
        parser.add_argument('student_user_id', type=int, required=True, location='json')
        parser.add_argument('day', type=int, required=True, location='json')
        parser.add_argument('start_time', type=int, required=True, location='json')
        parser.add_argument('stop_time', type=int, required=True, location='json')
        course_id, teacher_id, student_id = \
            self.get_params('course_id', 'teacher_user_id', 'student_user_id')
        if not Course.get(id=course_id) or not User.get(id=teacher_id) or not User.get(id=student_id):
            self.bad_request(errorcode.BAD_REQUEST)
        day, start_time, stop_time = self.get_params('day', 'start_time', 'stop_time')
        user_ids = self._get_not_available_user_ids(day, start_time, stop_time)
        if teacher_id in user_ids or student_id in user_ids:
            self.bad_request(errorcode.BAD_REQUEST_USER_CONFLICT)
        tb = CourseTable()
        tb.course_id = course_id
        tb.teacher_id = teacher_id
        tb.student_id = student_id
        tb.start_time = start_time
        tb.stop_time = stop_time
        tb.day = day
        tb.save()
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def update_course_table(self):
        parser = self.get_parser()
        parser.add_argument('table_id', type=int, required=True, location='args')
        parser.add_argument('course_id', type=int, required=True, location='json')
        parser.add_argument('teacher_user_id', type=int, required=True, location='json')
        tb_id = self.get_param('table_id')
        course_id, teacher_id = self.get_params('course_id', 'teacher_user_id')
        tb = CourseTable.get(id=tb_id)
        if not tb:
            self.bad_request(errorcode.NOT_FOUND)
        if not Course.get(id=course_id) or not User.get(id=teacher_id):
            self.bad_request(errorcode.BAD_REQUEST)
        user_ids = self._get_not_available_user_ids(tb.day, tb.start_time, tb.stop_time, RoleType.teacher)
        if teacher_id in user_ids:
            self.bad_request(errorcode.BAD_REQUEST_USER_CONFLICT)
        tb.course_id = course_id
        tb.teacher_id = teacher_id
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

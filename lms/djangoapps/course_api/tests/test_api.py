"""
Test for course API
"""

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory
from rest_framework.exceptions import PermissionDenied

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase, ModuleStoreTestCase

from ..api import course_detail, list_courses
from .mixins import CourseApiFactoryMixin


class CourseApiTestMixin(CourseApiFactoryMixin):
    """
    Establish basic functionality for Course API tests
    """

    maxDiff = 1000  # long enough to show mismatched dicts

    expected_course_data = {
        'blocks_url': '/api/courses/v1/blocks/?course_id=edX%2Ftoy%2F2012_Fall',
        'course_image': u'/c4x/edX/toy/asset/just_a_test.jpg',
        'description': u'A course about toys.',
        'end': u'2015-09-19T18:00:00Z',
        'enrollment_end': u'2015-07-15T00:00:00Z',
        'enrollment_start': u'2015-06-15T00:00:00Z',
        'id': u'edX/toy/2012_Fall',
        'name': u'Toy Course',
        'number': u'toy',
        'org': u'edX',
        'start': u'2015-07-17T12:00:00Z',
        'start_display': u'July 17, 2015',
        'start_type': u'timestamp',
    }

    @classmethod
    def setUpClass(cls):
        super(CourseApiTestMixin, cls).setUpClass()
        cls.request_factory = RequestFactory()


class TestGetCourseDetail(CourseApiTestMixin, SharedModuleStoreTestCase):
    """
    Test course_detail api function
    """
    @classmethod
    def setUpClass(cls):
        super(TestGetCourseDetail, cls).setUpClass()
        cls.course = cls.create_course()
        cls.hidden_course = cls.create_course(course=u'hidden', visible_to_staff_only=True)
        cls.honor_user = cls.create_user('honor', is_staff=False)
        cls.staff_user = cls.create_user('staff', is_staff=True)

    def _make_api_call(self, requesting_user, target_user, course_key):
        """
        Call the `course_detail` api endpoint to get information on the course
        identified by `course_key`.
        """
        request = self.request_factory.get('/')
        request.user = requesting_user
        return course_detail(request.user, target_user, course_key, request)

    def test_get_existing_course(self):
        course_key = CourseKey.from_string(u'edX/toy/2012_Fall')
        result = self._make_api_call(self.honor_user, self.honor_user.username, course_key)
        self.assertEqual(self.expected_course_data, result.data)

    def test_get_nonexistent_course(self):
        course_key = CourseKey.from_string(u'edX/toy/nope')
        with self.assertRaises(Http404):
            self._make_api_call(self.honor_user, self.honor_user.username, course_key)

    def test_hidden_course_for_honor(self):
        course_key = CourseKey.from_string(u'edX/hidden/2012_Fall')
        with self.assertRaises(Http404):
            self._make_api_call(self.honor_user, self.honor_user.username, course_key)

    def test_hidden_course_for_staff(self):
        course_key = CourseKey.from_string(u'edX/hidden/2012_Fall')
        result = self._make_api_call(self.staff_user, self.staff_user.username, course_key)
        self.assertIsInstance(result.data, dict)

    def test_hidden_course_for_staff_as_honor(self):
        course_key = CourseKey.from_string(u'edX/hidden/2012_Fall')
        with self.assertRaises(Http404):
            self._make_api_call(self.honor_user, self.honor_user.username, course_key)


class CourseListTestMixin(CourseApiTestMixin):
    """
    Common behavior for list_courses tests
    """
    def _make_api_call(self, requesting_user, specified_user):
        """
        Call the list_courses api endpoint to get information about
        `specified_user` on behalf of `requesting_user`.
        """
        request = self.request_factory.get('/')
        request.user = requesting_user
        return list_courses(requesting_user, specified_user.username, request)


class TestGetCourseList(CourseListTestMixin, SharedModuleStoreTestCase):
    """
    Test the behavior of the `list_courses` api function.
    """
    @classmethod
    def setUpClass(cls):
        super(TestGetCourseList, cls).setUpClass()
        cls.create_course()
        cls.staff_user = cls.create_user("staff", is_staff=True)
        cls.honor_user = cls.create_user("honor", is_staff=False)

    def test_as_staff(self):
        courses = self._make_api_call(self.staff_user, self.staff_user)
        self.assertEqual(len(courses.data), 1)
        self.assertEqual(courses.data[0], self.expected_course_data)

    def test_for_honor_user_as_staff(self):
        courses = self._make_api_call(self.staff_user, self.honor_user)
        self.assertEqual(len(courses.data), 1)
        self.assertEqual(courses.data[0], self.expected_course_data)

    def test_as_honor(self):
        courses = self._make_api_call(self.honor_user, self.honor_user)
        self.assertEqual(len(courses.data), 1)
        self.assertEqual(courses.data[0], self.expected_course_data)

    def test_for_staff_user_as_honor(self):
        with self.assertRaises(PermissionDenied):
            self._make_api_call(self.honor_user, self.staff_user)

    def test_as_anonymous(self):
        anonuser = AnonymousUser()
        courses = self._make_api_call(anonuser, anonuser)
        self.assertEqual(len(courses.data), 1)
        self.assertEqual(courses.data[0], self.expected_course_data)

    def test_for_honor_user_as_anonymous(self):
        anonuser = AnonymousUser()
        with self.assertRaises(PermissionDenied):
            self._make_api_call(anonuser, self.staff_user)

    def test_multiple_courses(self):
        self.create_course(course='second')
        courses = self._make_api_call(self.honor_user, self.honor_user)
        self.assertEqual(len(courses.data), 2)


class TestGetCourseListExtras(CourseListTestMixin, ModuleStoreTestCase):
    """
    Tests of course_list api function that require alternative configurations
    of created courses.
    """
    @classmethod
    def setUpClass(cls):
        super(TestGetCourseListExtras, cls).setUpClass()
        cls.staff_user = cls.create_user("staff", is_staff=True)
        cls.honor_user = cls.create_user("honor", is_staff=False)

    def test_no_courses(self):
        courses = self._make_api_call(self.honor_user, self.honor_user)
        self.assertEqual(len(courses.data), 0)

    def test_hidden_course_for_honor(self):
        self.create_course(visible_to_staff_only=True)
        courses = self._make_api_call(self.honor_user, self.honor_user)
        self.assertEqual(len(courses.data), 0)

    def test_hidden_course_for_staff(self):
        self.create_course(visible_to_staff_only=True)
        courses = self._make_api_call(self.staff_user, self.staff_user)
        self.assertEqual(len(courses.data), 1)
        self.assertEqual(courses.data[0], self.expected_course_data)

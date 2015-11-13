"""
Test for course API
"""

from lettuce import world
from django.test import RequestFactory

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import ToyCourseFactory

from lms.djangoapps.course_api.api import list_courses


class TestGetCourseList(ModuleStoreTestCase):
    """
    Test the behavior of the course list api
    """

    expected_course_data = {
        'blocks_url': '/api/courses/v1/blocks/?course_id=edX%2Ftoy%2F2012_Fall',
        'course_image': u'/c4x/edX/toy/asset/just_a_test.jpg',
        'description': u'A course about toys.',
        'end': None,
        'enrollment_end': None,
        'enrollment_start': None,
        'id': u'edX/toy/2012_Fall',
        'name': u'Toy Course',
        'number': u'toy',
        'org': u'edX',
        'start': u'2015-07-17T12:00:00Z',
        'start_display': u'July 17, 2015',
        'start_type': 'timestamp',
    }

    @classmethod
    def setUpClass(cls):
        super(TestGetCourseList, cls).setUpClass()
        cls.request_factory = RequestFactory()

    def setUp(self):
        super(TestGetCourseList, self).setUp()
        self.create_course()
        self.staff_user = self.create_user("staff", "staff@example.com", "edx", True)
        self.honor_user = self.create_user("honor", "honor@example.com", "edx", False)

    def create_user(self, username, email, password, is_staff):
        """
        Create a user as identified by username, email, password and is_staff.
        """
        user = world.UserFactory(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff)
        return user

    def create_course(self):
        """
        Create a course for use in test cases
        """
        return ToyCourseFactory.create()

    def _make_api_call(self, requesting_user, specified_user):
        """
        Call the list_courses api endpoint to get information about
        `specified_user` on behalf of `requesting_user`.
        """
        request = self.request_factory.get('/')
        request.user = requesting_user
        return list_courses(requesting_user, specified_user.username, request)

    def test_user_course_list_as_staff(self):
        courses = self._make_api_call(self.staff_user, self.staff_user)
        self.assertEqual([dict(course) for course in courses.data], [self.expected_course_data])

    def test_honor_user_course_list_as_staff(self):
        courses = self._make_api_call(self.staff_user, self.honor_user)
        self.assertEqual([dict(course) for course in courses.data], [self.expected_course_data])

    def test_user_course_list_as_honor(self):
        courses = self._make_api_call(self.honor_user, self.honor_user)
        self.assertEqual(courses.data, [self.expected_course_data])

    def test_staff_user_course_list_as(self):
        with self.assertRaises(ValueError):
            self._make_api_call(self.honor_user, self.staff_user)

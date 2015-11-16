"""
Tests for Blocks Views
"""

from django.core.urlresolvers import reverse
from lettuce import world

from student.models import CourseEnrollment
from student.tests.factories import CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import ToyCourseFactory



class CourseApiTestViewMixin(object):
    """
    Mixin class for test helpers for Course API views
    """
    @classmethod
    def create_course(cls):
        """
        Create a sample course
        """
        return ToyCourseFactory.create()

    def create_user(self, username, email, password, is_staff):
        return world.UserFactory(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff
        )

    def setup_user(self, requesting_user, enrolled_user=None):
        """
        Create a user, logged in, and enrolled in the sample course
        """
        self.user = requesting_user  # pylint: disable=attribute-defined-outside-init
        self.client.login(username=self.user.username, password='edx')
        CourseEnrollmentFactory.create(user=enrolled_user or self.user, course_id=self.course.id)

    def verify_response(self, expected_status_code=200, params=None, url=None):
        """
        Ensure that the sending a GET request to the specified URL (or self.url)
        returns the expected status code (200 by default).

        Arguments:
            expected_status_code: (default 200)
            params:
                query parameters to include in the request (includes
                username=[self.user.username]&depth=all by default)
            url: (default [self.url])

        Returns:
            response: The HttpResponse returned by the request
        """
        query_params = {
            'username': self.user
        }
        query_params.update(params or {})
        response = self.client.get(url or self.url, param=query_params)
        self.assertEqual(response.status_code, expected_status_code)
        return response


class CourseListViewTestCase(CourseApiTestViewMixin, SharedModuleStoreTestCase):

    @classmethod
    def setUpClass(cls):
        super(CourseListViewTestCase, cls).setUpClass()
        cls.course = ToyCourseFactory.create()
        cls.url = reverse('course-list')

    def setUp(self):
        super(CourseListViewTestCase, self).setUp()
        self.staff_user = world.UserFactory(username='staff', email='staff@example.com', password='edx', is_staff=True)
        self.honor_user = world.UserFactory(username='honor', email='honor@example.com', password='edx', is_staff=False)

    def test_staff_for_self(self):
        self.setup_user(self.staff_user)
        self.verify_response()

    def test_staff_for_other(self):
        self.setup_user(self.staff_user, enrolled_user=self.honor_user)
        self.verify_response(params={'username': self.honor_user.username})

    def test_student_for_self(self):
        self.setup_user(self.honor_user)
        self.verify_response()

    def test_student_for_other(self):
        self.setup_user(self.honor_user, enrolled_user=self.staff_user)
        self.verify_response(expected_status_code=404, params={'username': self.staff_user.username})

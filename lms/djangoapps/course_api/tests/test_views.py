"""
Tests for Blocks Views
"""

from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import ToyCourseFactory

TEST_PASSWORD = 'edx'


class CourseApiTestViewMixin(object):
    """
    Mixin class for test helpers for Course API views
    """

    @staticmethod
    def create_course():
        """
        Create a sample course.
        """
        return ToyCourseFactory.create()

    @staticmethod
    def create_user(username, email, is_staff):
        """
        Create a user for testing purposes.

        Arguments:
            `username`: (string)
            `email`: (string)
            `is_staff`: (boolean)

        Return value:
            User object
        """
        return UserFactory(
            username=username,
            email=email,
            password=TEST_PASSWORD,
            is_staff=is_staff
        )

    def setup_user(self, requesting_user):
        """
        log in the specified user, and remember it as `self.user`
        """
        self.user = requesting_user  # pylint: disable=attribute-defined-outside-init
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def verify_response(self, expected_status_code=200, params=None):
        """
        Ensure that sending a GET request to self.url returns the expected
        status code (200 by default).

        Arguments:
            expected_status_code: (default 200)
            params:
                query parameters to include in the request. Can include
                `username`.

        Returns:
            response: (HttpResponse) The response returned by the request
        """
        query_params = {}
        query_params.update(params or {})
        response = self.client.get(self.url, data=query_params)
        self.assertEqual(response.status_code, expected_status_code)
        return response


class CourseListViewTestCase(CourseApiTestViewMixin, SharedModuleStoreTestCase):
    """
    Test responses returned from CourseListView.
    """

    @classmethod
    def setUpClass(cls):
        super(CourseListViewTestCase, cls).setUpClass()
        cls.course = ToyCourseFactory.create()
        cls.staff_user = cls.create_user(username='staff', email='staff@example.com', is_staff=True)
        cls.honor_user = cls.create_user(username='honor', email='honor@example.com', is_staff=False)
        cls.url = reverse('course-list')

    def setUp(self):
        super(CourseListViewTestCase, self).setUp()

    def test_as_staff(self):
        self.setup_user(self.staff_user)
        self.verify_response()

    def test_as_staff_for_other(self):
        self.setup_user(self.staff_user)
        self.verify_response(params={'username': self.honor_user.username})

    def test_as_student(self):
        self.setup_user(self.honor_user)
        self.verify_response()

    def test_as_student_for_explicit_self(self):
        self.setup_user(self.honor_user)
        self.verify_response(params={'username': self.honor_user.username})

    def test_as_student_for_other(self):
        self.setup_user(self.honor_user)
        self.verify_response(expected_status_code=404, params={'username': self.staff_user.username})

    def test_not_logged_in(self):
        self.client.logout()
        self.verify_response()


class CourseDetailViewTestCase(CourseApiTestViewMixin, SharedModuleStoreTestCase):
    """
    Test responses returned from CourseDetailView.
    """

    def test_tests_defined(self):
        self.fail()

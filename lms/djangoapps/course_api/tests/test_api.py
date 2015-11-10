"""
Test for course API
"""

from lettuce import world
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from rest_framework import status

from lms.djangoapps.course_api.api import list_courses


class TestGetCourseList(ModuleStoreTestCase):
    """
    Test the behavior of the course list api
    """

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
        pass

    def setUp(self):
        super(TestGetCourseList, self).setUp()
        self.create_course()

    def test_user_course_list_as_staff(self):
        user = self.create_user("staff", "staff@example.com", "edx", True)
        courses = list_courses(user, "staff")
        self.assertEqual(courses, [])

    def test_user_course_list_as_honor(self):
        user = self.create_user("honor", "honor@example.com", "edx", False)
        courses = list_courses(user, "honor")
        self.assertEqual(courses, [])

    def test_user_course_list_as_honor_staff(self):
        user = self.create_user("honor", "honor@example.com", "edx", False)
        with self.assertRaises(ValueError):
            list_courses(user, "staff")
        #self.assertEqual(courses.status_code, status.HTTP_403_FORBIDDEN)

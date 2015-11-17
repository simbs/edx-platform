"""
Course API
"""

from django.contrib.auth.models import User
from lms.djangoapps.courseware.courses import (
    get_courses,
    get_course_by_id
)

from rest_framework.exceptions import PermissionDenied

from .permissions import can_view_courses_for_username
from .serializers import CourseSerializer


def course_detail(course_key, request):
    """
    Return a single course identified by `course_key`

    Arguments:
        `course_key`: (CourseKey)
            Identifies the course of interest

        `request`: (HTTPRequest)
            Is used to retrieve the course description from modulestore

    Return value:
        CourseSerializer object representing the requested course
    """
    course = get_course_by_id(course_key)
    return CourseSerializer(course, context={'request': request})


def list_courses(requesting_user, username, request):
    """
    Return a list of courses visible to the user identified by `username` on
    behalf of `requesting_user`.
    """

    if not can_view_courses_for_username(requesting_user, username):
        raise PermissionDenied

    if username:
        user = User.objects.get(username=username)
    else:
        user = requesting_user

    courses = get_courses(user)
    return CourseSerializer(courses, context={'request': request}, many=True)

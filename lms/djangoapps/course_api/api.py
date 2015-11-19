"""
Course API
"""

from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied

from lms.djangoapps.courseware.courses import get_courses, get_course_with_access

from .permissions import can_view_courses_for_username
from .serializers import CourseSerializer


def get_effective_user(requesting_user, target_username):
    """
    Get the user we want to view information on behalf of.
    """
    if target_username == requesting_user.username or None:
        return requesting_user
    elif can_view_courses_for_username(requesting_user, target_username):
        return User.objects.get(username=target_username)
    else:
        raise PermissionDenied()


def course_detail(requesting_user, target_username, course_key, request):
    """
    Return a single course identified by `course_key`.

    The course must be visible to the user identified by `target_username` and
    `requesting_user` should have permission to view courses available to that
    user.

    Arguments:
        requesting_user (User): The user asking for course information
        target_username (string):
            The name of the user `requesting_user would like to be identified as.
        course_key (CourseKey): Identifies the course of interest
        request (HTTPRequest):
            Used to instantiate the course module to retrieve the
            course about description

    Return value:
        CourseSerializer object representing the requested course
    """
    user = get_effective_user(requesting_user, target_username)
    course = get_course_with_access(user, 'see_exists', course_key)
    return CourseSerializer(course, context={'request': request})


def list_courses(requesting_user, target_username, request):
    """
    Return a list of available courses.

    The courses returned are all be visible to the user identified by
    `target_username` and `requesting_user` should have permission to
    view courses available to that user.

    Arguments:
        requesting_user (User): The user asking for course information
        target_username (string):
            The name of the user `requesting_user would like to be
            identified as
        request (HTTPRequest):
            Used to instantiate the course module to retrieve the
            course about description

    Return value:
        A CourseSerializer object representing the collection of courses.
    """
    user = get_effective_user(requesting_user, target_username)
    courses = get_courses(user)
    return CourseSerializer(courses, context={'request': request}, many=True)

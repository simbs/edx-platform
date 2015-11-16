"""
Course API
"""

from django.contrib.auth.models import User
from lms.djangoapps.courseware.courses import (
    get_courses,
    get_course_by_id
)
from opaque_keys.edx.keys import CourseKey

from .serializers import CourseSerializer


def _has_permission(requesting_user, username):
    """
    Returns true if `requesting_user` has permission to access the user
    identified by `username`.

    Arguments:
        requesting_user (User): The user requesting permission to view another
        username (string): The name of the user `requesting_user` would like
        to access.

    Return value:
        Boolean
    """
    if not username:
        return False
    return requesting_user.is_staff or requesting_user.username == username


def course_detail(course_key_string, request):
    """
    Return a single course
    """
    # course_key = CourseKey.from_string(course_key_string)
    # course_usage_key = modulestore().make_course_usage_key(course_key)

    course = get_course_by_id(CourseKey.from_string(course_key_string))
    return CourseSerializer(course, context={'request': request})


def list_courses(requesting_user, username, request):
    """
    Return a list of courses visible to the user identified by `username` on
    behalf of `requesting_user`
    """

    if _has_permission(requesting_user, username) is not True:
        raise ValueError  # Raise something better than this
    if username:
        user = User.objects.get(username=username)
    else:
        user = requesting_user

    courses = get_courses(user)
    return CourseSerializer(courses, context={'request': request}, many=True)

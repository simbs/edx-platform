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


def course_detail(requesting_user, username, course_key, request):
    """
    Return a single course identified by `course_key`

    Arguments:
        `requesting_user`: (User)

        `username`: (string)
        `course_key`: (CourseKey)
            Identifies the course of interest

        `request`: (HTTPRequest)
            Is used to retrieve the course description from modulestore

    Return value:
        CourseSerializer object representing the requested course
    """
    user = get_effective_user(requesting_user, username)
    course = get_course_with_access(user, 'see_exists', course_key)
    return CourseSerializer(course, context={'request': request})


def list_courses(requesting_user, username, request):
    """
    Return a list of courses visible to the user identified by `username` on
    behalf of `requesting_user`.
    """
    user = get_effective_user(requesting_user, username)
    courses = get_courses(user)
    return CourseSerializer(courses, context={'request': request}, many=True)

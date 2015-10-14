"""
Course API Views
"""

from rest_framework.views import APIView

from openedx.core.lib.api.view_utils import view_auth_classes

from .api import (
    list_courses,
    course_view
)

@view_auth_classes()
class CourseView(APIView):
    """
    Course API view
    """

    def get(self, request, course_key_string):
        """
        Request information on a course specified by `course_key_string`.
            Body consists of a `blocks_url` that can be used to fetch the
            blocks for the requested course.

        Arguments:
            request (HttpRequest)
            course_key_string

        Returns:
            HttpResponse: 200 on success


        Example Usage:

            GET /api/courses/v1/[course_key_string]
            200 OK

        Example response:

            {"blocks_url": "https://server/api/courses/v1/blocks/[usage_key]"}
        """
        return course_view(request, course_key_string)


class CourseListView(APIView):
    """
    View class to list courses
    """
    def get(self, request):

        username = request.query_params.get('user', '')

        return list_courses(request, username)

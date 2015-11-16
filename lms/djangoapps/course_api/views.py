"""
Course API Views
"""

from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView, Response

from opaque_keys import InvalidKeyError

from openedx.core.lib.api.view_utils import view_auth_classes

from .api import (
    course_detail,
    list_courses,
)


@view_auth_classes()
class CourseDetailView(APIView):
    """
    Course API view
    """

    def get(self, request, course_key_string):
        """
        Request information on a course specified by `course_key_string`.

        Body consists of a `blocks_url` that can be used to fetch the blocks
        for the requested course.

        Arguments:
            request (HttpRequest)
            course_key_string: string representing the course key

        Returns:
            HttpResponse: 200 on success


        Example Usage:

            GET /api/courses/v1/[course_key_string]
            200 OK

        Example response:

            {"blocks_url": "https://server/api/courses/v1/blocks/[usage_key]"}
        """
        try:
            content = course_detail(course_key_string, request)
        except InvalidKeyError:
            raise Http404()
        return Response(content)


class CourseListView(APIView):
    """
    View class to list multiple courses
    """

    def get(self, request):
        """
        Request information on all courses visible to the specified user

        Body consists of a lit of objects as returned by `CourseView`.

        Arguments:

            request (HttpRequest)

        Parameters:

            username (optional):
                The username of the specified user whose visible courses we
                want to see.  Defaults to the current user.

        Returns:

            - A 404 response, if the specified user does not exist, or the
              requesting user does not have permission to view their
              courses.

            - A 200 response, if the request is successful, with a list of
              course discovery objects as returned by `CourseView`.
        """

        username = request.query_params.get('username', request.user.username)

        try:
            content = list_courses(request.user, username, request)
        except ValueError:
            return Response('Unauthorized', status=status.HTTP_404_NOT_FOUND)
        return Response(content)

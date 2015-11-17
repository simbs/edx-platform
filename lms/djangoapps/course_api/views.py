"""
Course API Views
"""

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import APIView, Response

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey


from openedx.core.lib.api.view_utils import view_auth_classes

from .api import course_detail, list_courses


@view_auth_classes()
class CourseDetailView(APIView):
    """
    Course API view
    """

    def get(self, request, course_key_string):
        """
        Request information on a course specified by `course_key_string`.

        Body consists of the following fields:
            * `blocks_url`: can be used to fetch the blocks
            * `course_image`:
            * `description`:
            * `end`: Date the course ends
            * `enrollment_end`: Date enrollment ends
            * `enrollment_start`: Date enrollment begins
            * `id`: Course key
            * `name`: Name of the course
            * `number`: Catalog number of the course
            * `org`: Name of the organization that owns the course
            * `start`: Date the course begins
            * `start_display`: Readably formatted start of the course
            * `start_type`: Hint describing how `start_display` is set. One of:
                  - `"string"`: manually set
                  - `"timestamp"`: generated form `start` timestamp
                  - `"empty"`: the start date should not be shown

        Arguments:
            request: (HttpRequest)
            course_key_string: (string) Key for the desired course

        Returns:
            HttpResponse: 200 on success

        Example Usage:
            GET /api/courses/v1/[course_key_string]
            200 OK

        Example response:
            {
                "blocks_url": "/api/courses/v1/blocks/?course_id=edX%2Ftoy%2F2012_Fall",
                "course_image": "/c4x/edX/toy/asset/just_a_test.jpg",
                "description": "A course about toys.",
                "end": "2015-09-19T18:00:00Z",
                "enrollment_end": "2015-07-15T00:00:00Z",
                "enrollment_start": "2015-06-15T00:00:00Z",
                "id": "edX/toy/2012_Fall",
                "name": "Toy Course",
                "number": "toy",
                "org": "edX",
                "start": "2015-07-17T12:00:00Z",
                "start_display": "July 17, 2015",
                "start_type": "timestamp"
            }
        """
        try:
            course_key = CourseKey.from_string(course_key_string)
        except InvalidKeyError:
            raise NotFound()
        return Response(course_detail(course_key, request))


class CourseListView(APIView):
    """
    View class to list multiple courses
    """

    def get(self, request):
        """
        Request information on all courses visible to the specified user.

        Body consists of a list of objects as returned by `CourseDetailView`.

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
              course discovery objects as returned by `CourseDetailView`.
        """
        username = request.query_params.get('username', request.user.username)

        try:
            content = list_courses(request.user, username, request)
        except PermissionDenied:
            return NotFound()
        return Response(content.data)

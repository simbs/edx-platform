"""
Course API Serializers.  Representing course catalog data
"""

import urllib

from django.core.urlresolvers import reverse
from django.template import defaultfilters

from rest_framework import serializers

from xmodule.course_module import DEFAULT_START_DATE
from lms.djangoapps.courseware.courses import (
    course_image_url,
    get_course_about_section,
)

START_TYPE_CHOICES = [('string', 'string'), ('timestamp', 'timestamp'), ('empty', 'empty')]


class CourseSerializer(serializers.Serializer):
    """
    Serializer for Course objects
    """

    id = serializers.CharField(read_only=True)  # pylint: disable=invalid-name
    name = serializers.CharField(source='display_name_with_default')
    number = serializers.CharField(source='display_number_with_default')
    org = serializers.CharField(source='display_org_with_default')
    start = serializers.DateTimeField()
    # start_type = serializers.ChoiceField(choices=START_TYPE_CHOICES)
    # start_display = serializers.CharField()
    end = serializers.DateTimeField()
    enrollment_start = serializers.DateTimeField()
    enrollment_end = serializers.DateTimeField()
    # course_image = serializers.URLField()
    # blocks_url = serializers.URLField()

    def create(self, *args, **kwargs):
        """
        Course creation is not supported through this API
        """
        pass

    def update(self, *args, **kwargs):
        """
        Course updates are not supported through this API
        """
        pass

    def to_representation(self, course):
        """
        Create a dictionary representation of a course for serialization
        """
        data = super(CourseSerializer, self).to_representation(course)

        if course.advertised_start is not None:
            start_type = 'string'
            start_display = course.advertised_start
        elif course.start != DEFAULT_START_DATE:
            start_type = 'timestamp'
            start_display = defaultfilters.date(course.start, "DATE_FORMAT")
        else:
            start_type = 'empty'
            start_display = None
        data['start_type'] = start_type
        data['start_display'] = start_display

        data['description'] = get_course_about_section(course, 'short_description').strip()
        data['course_image'] = course_image_url(course)
        data['blocks_url'] = '?'.join([
            reverse('blocks_in_course'),
            urllib.urlencode({'course_id': course.id}),
        ])
        return data

"""
Factories for Badge tests
"""
import factory
from django.core.files.base import ContentFile
from factory import DjangoModelFactory
from factory.django import ImageField

from badges.models import BadgeAssertion, CourseCompleteImageConfiguration, BadgeClass
from student.tests.factories import UserFactory


def generate_dummy_image(_unused):
    """
    Used for image fields to create a sane default.
    """
    return ContentFile(
        ImageField()._make_data(  # pylint: disable=protected-access
            {'color': 'blue', 'width': 50, 'height': 50, 'format': 'PNG'}
        ), 'test.png'
    )


class CourseCompleteImageConfigurationFactory(DjangoModelFactory):
    """
    Factory for BadgeImageConfigurations
    """
    class Meta(object):
        model = CourseCompleteImageConfiguration

    mode = 'honor'
    icon = factory.LazyAttribute(generate_dummy_image)


class BadgeClassFactory(DjangoModelFactory):
    """
    Factory for BadgeClass
    """
    class Meta(object):
        model = BadgeClass

    slug = 'test_slug'
    issuing_component = 'test_component'
    display_name = 'Test Badge'
    description = "Yay! It's a test badge."
    criteria = 'https://example.com/syllabus'
    mode = 'honor'
    image = factory.LazyAttribute(generate_dummy_image)


class BadgeAssertionFactory(DjangoModelFactory):
    """
    Factory for BadgeAssertions
    """
    class Meta(object):
        model = BadgeAssertion

    user = factory.SubFactory(UserFactory)
    badge_class = factory.SubFactory(BadgeClassFactory)
    data = {}
    assertion_url = 'http://example.com/example.json'
    image_url = 'http://example.com/image.png'

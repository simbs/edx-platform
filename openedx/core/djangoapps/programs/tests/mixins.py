"""Mixins for use during testing."""
from openedx.core.djangoapps.programs.models import ProgramsApiConfig


class ProgramsApiConfigMixin(object):
    """Utilities for working with Programs configuration during testing."""

    DEFAULTS = {
        'enabled': True,
        'api_version_number': 1,
        'internal_service_url': 'http://internal.programs.org/',
        'public_service_url': 'http://public.programs.org/',
        'authoring_app_js_path': '/path/to/js',
        'authoring_app_css_path': '/path/to/css',
        'enable_student_dashboard': True,
        'enable_studio_tab': True,
    }

    def create_config(self, **kwargs):
        """Creates a new ProgramsApiConfig with DEFAULTS, updated with any provided overrides."""
        fields = dict(self.DEFAULTS, **kwargs)
        ProgramsApiConfig(**fields).save()

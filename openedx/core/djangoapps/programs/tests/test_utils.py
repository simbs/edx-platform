"""Tests covering Programs utilities."""
import json
from unittest import skipUnless

from django.conf import settings
from django.test import TestCase
import httpretty
import mock
from provider.constants import CONFIDENTIAL
from provider.oauth2.models import Client

from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.tests.mixins import ProgramsApiConfigMixin
from openedx.core.djangoapps.programs.utils import get_programs, get_programs_for_dashboard
from student.tests.factories import UserFactory


# TODO (RFL): This code is now also used in Studio; is it still only valid for the LMS?
@skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class TestProgramRetrieval(ProgramsApiConfigMixin, TestCase):
    """Tests covering the retrieval of programs from the Programs service."""
    COURSE_KEYS = [
        'organization-a/course-a/fall',
        'organization-a/course-a/winter',
        'organization-a/course-b/fall',
        'organization-a/course-b/winter',
        'organization-b/course-c/fall',
        'organization-b/course-c/winter',
        'organization-b/course-d/fall',
        'organization-b/course-d/winter',
    ]

    PROGRAMS_API_RESPONSE = {
        'results': [
            {
                'id': 1,
                'name': 'Test Program A',
                'subtitle': 'A program used for testing purposes',
                'category': 'xseries',
                'status': 'unpublished',
                'marketing_slug': '',
                'organizations': [
                    {
                        'display_name': 'Test Organization A',
                        'key': 'organization-a'
                    }
                ],
                'course_codes': [
                    {
                        'display_name': 'Test Course A',
                        'key': 'course-a',
                        'organization': {
                            'display_name': 'Test Organization A',
                            'key': 'organization-a'
                        },
                        'run_modes': [
                            {
                                'course_key': COURSE_KEYS[0],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'fall'
                            },
                            {
                                'course_key': COURSE_KEYS[1],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'winter'
                            }
                        ]
                    },
                    {
                        'display_name': 'Test Course B',
                        'key': 'course-b',
                        'organization': {
                            'display_name': 'Test Organization A',
                            'key': 'organization-a'
                        },
                        'run_modes': [
                            {
                                'course_key': COURSE_KEYS[2],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'fall'
                            },
                            {
                                'course_key': COURSE_KEYS[3],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'winter'
                            }
                        ]
                    }
                ],
                'created': '2015-10-26T17:52:32.861000Z',
                'modified': '2015-11-18T22:21:30.826365Z'
            },
            {
                'id': 2,
                'name': 'Test Program B',
                'subtitle': 'Another program used for testing purposes',
                'category': 'xseries',
                'status': 'unpublished',
                'marketing_slug': '',
                'organizations': [
                    {
                        'display_name': 'Test Organization B',
                        'key': 'organization-b'
                    }
                ],
                'course_codes': [
                    {
                        'display_name': 'Test Course C',
                        'key': 'course-c',
                        'organization': {
                            'display_name': 'Test Organization B',
                            'key': 'organization-b'
                        },
                        'run_modes': [
                            {
                                'course_key': COURSE_KEYS[4],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'fall'
                            },
                            {
                                'course_key': COURSE_KEYS[5],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'winter'
                            }
                        ]
                    },
                    {
                        'display_name': 'Test Course D',
                        'key': 'course-d',
                        'organization': {
                            'display_name': 'Test Organization B',
                            'key': 'organization-b'
                        },
                        'run_modes': [
                            {
                                'course_key': COURSE_KEYS[6],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'fall'
                            },
                            {
                                'course_key': COURSE_KEYS[7],
                                'mode_slug': 'verified',
                                'sku': '',
                                'start_date': '2015-11-05T07:39:02.791741Z',
                                'run_key': 'winter'
                            }
                        ]
                    }
                ],
                'created': '2015-10-26T19:59:03.064000Z',
                'modified': '2015-10-26T19:59:18.536000Z'
            }
        ]
    }

    def setUp(self):
        super(TestProgramRetrieval, self).setUp()

        Client.objects.create(name=ProgramsApiConfig.OAUTH2_CLIENT_NAME, client_type=CONFIDENTIAL)
        self.user = UserFactory()

    def _mock_programs_apis(self, data=PROGRAMS_API_RESPONSE, status_code=200):
        self.assertTrue(httpretty.is_enabled(), msg='httpretty must be enabled to mock Programs API calls.')

        url = ProgramsApiConfig.current().internal_api_url.strip('/') + '/programs/'
        body = json.dumps(data)

        httpretty.register_uri(httpretty.GET, url, body=body, content_type='application/json', status=status_code)

    @httpretty.activate
    def test_get_programs(self):
        """Verify programs data can be retrieved."""
        self.create_config()
        self._mock_programs_apis()

        actual = get_programs(self.user)
        self.assertEqual(
            actual,
            self.PROGRAMS_API_RESPONSE['results']
        )

    def test_get_programs_programs_disabled(self):
        """Verify behavior when programs is disabled."""
        self.create_config(enabled=False)

        actual = get_programs(self.user)
        self.assertEqual(actual, [])

    @mock.patch('edx_rest_api_client.client.EdxRestApiClient.__init__')
    def test_get_programs_client_initialization_failure(self, mock_init):
        """Verify behavior when API client fails to initialize."""
        self.create_config()
        mock_init.side_effect = Exception

        actual = get_programs(self.user)
        self.assertEqual(actual, [])
        self.assertTrue(mock_init.called)

    @httpretty.activate
    def test_get_programs_data_retrieval_failure(self):
        """Verify behavior when data can't be retrieved from Programs."""
        self.create_config()
        self._mock_programs_apis(status_code=500)

        actual = get_programs(self.user)
        self.assertEqual(actual, [])

    @httpretty.activate
    def test_get_programs_for_dashboard(self):
        """Verify programs data can be retrieved and parsed correctly."""
        self.create_config()
        self._mock_programs_apis()

        actual = get_programs_for_dashboard(self.user, self.COURSE_KEYS)
        expected = {}
        for program in self.PROGRAMS_API_RESPONSE['results']:
            for course_code in program['course_codes']:
                for run in course_code['run_modes']:
                    course_key = run['course_key']
                    expected[course_key] = program

        self.assertEqual(actual, expected)

    def test_get_programs_for_dashboard_dashboard_display_disabled(self):
        """Verify behavior when student dashboard display is disabled."""
        self.create_config(enable_student_dashboard=False)

        actual = get_programs_for_dashboard(self.user, self.COURSE_KEYS)
        self.assertEqual(actual, {})

    @httpretty.activate
    def test_get_programs_for_dashboard_no_data(self):
        """Verify behavior when no programs data is found for the user."""
        self.create_config()
        self._mock_programs_apis(data={'results': []})

        actual = get_programs_for_dashboard(self.user, self.COURSE_KEYS)
        self.assertEqual(actual, {})

    @httpretty.activate
    def test_get_programs_for_dashboard_invalid_data(self):
        """Verify behavior when the Programs API returns invalid data and parsing fails."""
        self.create_config()

        invalid_program = {'invalid_key': 'invalid_data'}
        self._mock_programs_apis(data={'results': [invalid_program]})

        actual = get_programs_for_dashboard(self.user, self.COURSE_KEYS)
        self.assertEqual(actual, {})

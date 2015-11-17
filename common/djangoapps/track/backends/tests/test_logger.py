# -*- coding: utf-8 -*-
"""
Tests for tracking logger.
"""
from __future__ import absolute_import

import json
import logging
import datetime
from mock import patch

from django.test import TestCase

from track.backends.logger import LoggerBackend


class TestLoggerBackend(TestCase):
    def setUp(self):
        super(TestLoggerBackend, self).setUp()
        self.handler = MockLoggingHandler()
        self.handler.setLevel(logging.INFO)

        logger_name = 'track.backends.logger.test'
        logger = logging.getLogger(logger_name)
        logger.addHandler(self.handler)

        self.backend = LoggerBackend(name=logger_name)
        self.handler.reset()

    def test_logger_backend(self):
        # Send a couple of events and check if they were recorded
        # by the logger. The events are serialized to JSON.

        event = {
            'test': True,
            'time': datetime.datetime(2012, 05, 01, 07, 27, 01, 200),
            'date': datetime.date(2012, 05, 07),
        }

        self.backend.send(event)
        self.backend.send(event)

        saved_events = [json.loads(e) for e in self.handler.messages['info']]

        unpacked_event = {
            'test': True,
            'time': '2012-05-01T07:27:01.000200+00:00',
            'date': '2012-05-07'
        }

        self.assertEqual(saved_events[0], unpacked_event)
        self.assertEqual(saved_events[1], unpacked_event)

    @patch('track.backends.logger.application_log')
    def test_logger_backend_unicode_character(self, application_log):
        """
        When event information contain utf and latin1 characters
        """
        # Utf-8 characters
        unicode_characters = {'test': u'测试'}
        unicode_characters_string = {'test': '测试'}
        encoded_unicode_characters = {
            'test': unicode_characters['test'].encode('utf-8')
        }
        # Latin1 characters
        unicode_latin_characters = {'test': u'Ó é ñ'}
        latin_characters_string = {'test': 'Ó é ñ'}
        encoded_latin_characters_string = {
            'test': unicode_latin_characters['test'].encode('latin1')
        }  # pylint: disable=invalid-name
        # Mix utf-8 and latin characters
        latin_and_unicode_characters = {'test': u'Ó é ñ and 测试'}
        latin_and_unicode_string = {'test': 'Ó é ñ and 测试'}
        encoded_latin_and_unicode_characters = {
            'test': unicode_characters['test'].encode('utf-8') + ' and ' + \
                    unicode_latin_characters['test'].encode('latin1')
        }

        self.backend.send(unicode_characters)
        self.backend.send(unicode_characters_string)
        self.backend.send(encoded_unicode_characters)

        self.backend.send(unicode_latin_characters)
        self.backend.send(latin_characters_string)
        self.backend.send(encoded_latin_characters_string)
        # encoded_latin_characters_string will raise UnicodeDecodeError due to encoded latin characters
        application_log.warning.assert_called_with(
            "UnicodeDecodeError Event-Data: %s", encoded_latin_characters_string
        )

        self.backend.send(latin_and_unicode_characters)
        self.backend.send(latin_and_unicode_string)
        self.backend.send(encoded_latin_and_unicode_characters)
        # encoded_latin_and_unicode_characters will raise UnicodeDecodeError due to encoded latin characters
        application_log.warning.assert_called_with(
            "UnicodeDecodeError Event-Data: %s", encoded_latin_and_unicode_characters
        )

        saved_events = [json.loads(e) for e in self.handler.messages['info']]
        # Utf-8 characters saved events correctness
        self.assertEqual(saved_events[0], unicode_characters)
        self.assertEqual(saved_events[1], unicode_characters)
        self.assertEqual(saved_events[2], unicode_characters)
        # Utf-8 characters saved events correctness
        self.assertEqual(saved_events[3], unicode_latin_characters)
        self.assertEqual(saved_events[4], unicode_latin_characters)
        self.assertEqual(saved_events[5], encoded_latin_characters_string)
        # Mix utf-8 and latin1 characters saved events correctness
        self.assertEqual(saved_events[6], latin_and_unicode_characters)
        self.assertEqual(saved_events[7], latin_and_unicode_characters)
        self.assertEqual(saved_events[8], encoded_latin_and_unicode_characters)


class MockLoggingHandler(logging.Handler):
    """
    Mock logging handler.

    Stores records in a dictionry of lists by level.

    """

    def __init__(self, *args, **kwargs):
        super(MockLoggingHandler, self).__init__(*args, **kwargs)
        self.messages = None
        self.reset()

    def emit(self, record):
        level = record.levelname.lower()
        message = record.getMessage()
        self.messages[level].append(message)

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

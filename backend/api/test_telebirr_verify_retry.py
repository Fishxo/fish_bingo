"""Telebirr verify retries on gateway errors (no DB required)."""
from unittest.mock import patch

from django.test import SimpleTestCase

from api.telebirr_verify import _is_transient_telebirr_verify_error, verify_telebirr_receipt


class TelebirrVerifyRetryTests(SimpleTestCase):
    def test_bad_gateway_is_transient(self):
        self.assertTrue(_is_transient_telebirr_verify_error('Bad Gateway'))
        self.assertFalse(_is_transient_telebirr_verify_error('Verification failed'))

    @patch('api.telebirr_verify.time.sleep', return_value=None)
    @patch('api.telebirr_verify._verify_telebirr_receipt_once')
    def test_retries_then_succeeds(self, once, _sleep):
        once.side_effect = [
            {'success': False, 'data': None, 'error': 'Bad Gateway'},
            {
                'success': True,
                'data': {'receiptNo': 'DHQ36J0TTF', 'creditedPartyName': 'Hermela'},
                'error': None,
            },
        ]
        result = verify_telebirr_receipt('DHQ36J0TTF', 'key')
        self.assertTrue(result['success'])
        self.assertEqual(once.call_count, 2)

    @patch('api.telebirr_verify.time.sleep', return_value=None)
    @patch('api.telebirr_verify._verify_telebirr_receipt_once')
    def test_does_not_retry_permanent_errors(self, once, _sleep):
        once.return_value = {'success': False, 'data': None, 'error': 'Verification failed'}
        result = verify_telebirr_receipt('DHQ36J0TTF', 'key')
        self.assertFalse(result['success'])
        self.assertEqual(once.call_count, 1)

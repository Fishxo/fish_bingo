"""Registration gift amount is independent of bid amount (no DB required)."""
from decimal import Decimal

from django.test import SimpleTestCase

from api.models import GameSettings


class RegistrationGiftAmountIndependenceTests(SimpleTestCase):
    def test_gift_amount_does_not_follow_bid_amount(self):
        settings = GameSettings(
            bid_amount=Decimal('10.00'),
            registration_gift_amount=Decimal('20.00'),
            give_register_reward=True,
        )
        self.assertEqual(settings.get_registration_gift_amount(), Decimal('20.00'))

        settings.bid_amount = Decimal('15.00')
        self.assertEqual(settings.get_registration_gift_amount(), Decimal('20.00'))
        self.assertEqual(settings.bid_amount, Decimal('15.00'))

        settings.registration_gift_amount = Decimal('5.00')
        self.assertEqual(settings.get_registration_gift_amount(), Decimal('5.00'))
        self.assertEqual(settings.bid_amount, Decimal('15.00'))

import unittest

from immo_rechner.core.hypothetical_positions import HypotheticalAppreciation
from immo_rechner.core.tax_contexts import UsageContext


class TestHypotheticalAppreciation(unittest.TestCase):

    def setUp(self):
        self.appreciation_rate = 0.05  # 5%
        self.initial_price = 100000
        self.usage_context = UsageContext.OWN_USE  # placeholder, could be any object

        self.position = HypotheticalAppreciation(
            appreciation_rate=self.appreciation_rate,
            initial_price=self.initial_price,
            usage=self.usage_context,
        )

    def test_evaluate_once(self):
        appreciation = self.position.evaluate()
        expected_appreciation = self.initial_price * self.appreciation_rate
        self.assertAlmostEqual(appreciation, expected_appreciation)
        self.assertAlmostEqual(
            self.position.current_price, self.initial_price + expected_appreciation
        )

    def test_evaluate_multiple_times(self):
        # First evaluation
        appreciation1 = self.position.evaluate()
        expected_price1 = self.initial_price + appreciation1

        # Second evaluation
        appreciation2 = self.position.evaluate()
        expected_price2 = expected_price1 + appreciation2

        self.assertAlmostEqual(self.position.current_price, expected_price2)
        self.assertAlmostEqual(
            appreciation1, self.initial_price * self.appreciation_rate
        )
        self.assertAlmostEqual(appreciation2, expected_price1 * self.appreciation_rate)

    def test_reset(self):
        self.position.evaluate()  # Increase current price
        self.position.reset()  # Should reset to initial price
        self.assertEqual(self.position.current_price, self.initial_price)

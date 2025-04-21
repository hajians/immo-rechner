from unittest import TestCase

from parameterized import parameterized

from immo_rechner.core.cost import (
    InterestRate,
    PurchaseSideCost,
    InstantSideCostWriteOff,
)
from immo_rechner.core.tax_contexts import UsageContext


class TestCosts(TestCase):

    def test_interest_rate_evaluate(self):
        # Given
        ir = InterestRate(
            usage=UsageContext.RENTING,
            yearly_rate=0.017,
            repayment_amount=84.10,
            initial_debt=1000,
        )

        # When
        total_cost = ir.evaluate()

        # Then
        self.assertAlmostEqual(total_cost, -9.23, places=2)
        self.assertAlmostEqual(ir.remaining_debt, 0, places=1)

    def test_evaluate_accusation_costs(self):
        # Given
        ac = PurchaseSideCost(
            usage=UsageContext.RENTING,
            purchase_price=100.0,
            land_value=0.0,
            approximate_land_value=False,
            depreciation_rate=0.01,
        )

        # When
        total_costs = ac.evaluate()

        # Then
        self.assertAlmostEqual(total_costs, -11.07 * ac.depreciation_rate)


class TestInstantSideCostWriteOff(TestCase):

    def setUp(self):
        self.purchase_price = 200000
        self.makler = 0.0375
        self.notar = 0.015
        self.transfer_tax = 0.06
        self.usage = UsageContext.OWN_USE

        self.cost_write_off = InstantSideCostWriteOff(
            usage=self.usage,
            purchase_price=self.purchase_price,
            makler=self.makler,
            notar=self.notar,
            transfer_tax=self.transfer_tax,
        )

    @parameterized.expand(
        [
            (
                "first_year",
                1,
                lambda self: -self.purchase_price
                * (self.makler + self.notar + self.transfer_tax),
            ),
            ("second_year", 2, lambda self: 0.0),
            ("third_year", 3, lambda self: 0.0),
        ]
    )
    def test_evaluate_parameterized(self, name, years_to_call, expected_func):
        for _ in range(years_to_call):
            result = self.cost_write_off.evaluate()

        expected = expected_func(self)
        self.assertAlmostEqual(result, expected)
        self.assertEqual(self.cost_write_off.year_counter, years_to_call)

    def test_reset(self):
        self.cost_write_off.evaluate()
        self.cost_write_off.reset()
        self.assertEqual(self.cost_write_off.year_counter, 0)

        expected_cost_after_reset = -self.purchase_price * (
            self.makler + self.notar + self.transfer_tax
        )
        result_after_reset = self.cost_write_off.evaluate()
        self.assertAlmostEqual(result_after_reset, expected_cost_after_reset)
        self.assertEqual(self.cost_write_off.year_counter, 1)

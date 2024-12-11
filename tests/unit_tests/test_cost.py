from unittest import TestCase

from immo_rechner.core.cost import InterestRate, PurchaseSideCost
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

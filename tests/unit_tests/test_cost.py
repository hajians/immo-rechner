from unittest import TestCase

from immo_rechner.core.cost import InterestRate, PurchaseSideCost


class TestCosts(TestCase):

    def test_interest_rate_evaluate(self):
        # Given
        ir = InterestRate(yearly_rate=0.017, repayment_amount=84.10, initial_debt=1000)

        # When
        total_cost = ir.evaluate()

        # Then
        self.assertAlmostEquals(total_cost, 9.23, places=2)
        self.assertAlmostEquals(ir.remaining_debt, 0, places=1)

    def test_evaluate_accusation_costs(self):
        # Given
        ac = PurchaseSideCost(purchase_price=100)

        # When
        total_costs = ac.evaluate()

        # Then
        self.assertAlmostEquals(total_costs, 11.07 * ac.depreciation_rate)

from unittest import TestCase, mock

from parameterized import parameterized

from immo_rechner.core.cost import PurchaseCost, BuildingMaintenance, InterestRate
from immo_rechner.core.profit_calculator import (
    ProfitCalculator,
    YearlySummary,
    InputParameters,
)
from immo_rechner.core.revenue import RentIncome
from immo_rechner.core.tax_contexts import UsageContext


def get_positions(
    usage=UsageContext.RENTING,
    monthly_rent=500.0,
    owner_share=0.5,
    facility_monthly_cost=200.0,
    yearly_interest_rate=0.01,
    repayment_amount=600.0,
    initial_debt=100_000,
    purchase_price=120_000,
    depreciation_rate=0.02,
):
    return [
        RentIncome(monthly_rent=monthly_rent),
        BuildingMaintenance(
            usage=usage, owner_share=owner_share, monthly_cost=facility_monthly_cost
        ),
        InterestRate(
            usage=usage,
            yearly_rate=yearly_interest_rate,
            repayment_amount=repayment_amount,
            initial_debt=initial_debt,
        ),
        PurchaseCost(
            usage=usage,
            purchase_price=purchase_price,
            approximate_land_value=True,
            depreciation_rate=depreciation_rate,
        ),
    ]


class TestProfitCalculator(TestCase):

    @staticmethod
    def get_profit_calculator():
        return ProfitCalculator.from_input_params(
            InputParameters(
                usage=UsageContext.RENTING,
                yearly_income=100_000,
                monthly_rent=416.6666,
                facility_monthly_cost=200.0,
                owner_share=0.0,
                repayment_amount=416.6666,
                yearly_interest_rate=0.05,
                initial_debt=100_000,
                depreciation_rate=0.01,
                purchase_price=200_000,
            )
        )

    def test_get_yearly_income_tax(self):
        # When
        income_tax = ProfitCalculator.get_yearly_income_tax(100_000)

        # Then
        self.assertAlmostEqual(income_tax, 31397.87)

    @parameterized.expand(
        [
            (
                "no_cost",
                get_positions(
                    monthly_rent=500,
                    owner_share=0.0,
                    yearly_interest_rate=0.0,
                    depreciation_rate=0.0,
                ),
                YearlySummary(profit_before_taxes=6000, income_tax=1200, cashflow=4800),
            ),
            (
                "with_hausgeld_cost",
                get_positions(
                    monthly_rent=500,
                    owner_share=0.5,
                    facility_monthly_cost=200,
                    yearly_interest_rate=0.0,
                    depreciation_rate=0.0,
                ),
                YearlySummary(profit_before_taxes=4800, income_tax=960, cashflow=3840),
            ),
            (
                "with_interest_rate",
                get_positions(
                    monthly_rent=500,
                    owner_share=0.0,
                    repayment_amount=500,
                    yearly_interest_rate=0.01,
                    initial_debt=100_000,
                    depreciation_rate=0.0,
                ),
                YearlySummary(
                    profit_before_taxes=6000 - 977.01,
                    income_tax=1004.59,
                    cashflow=4018.38,
                ),
            ),
            (
                """
                    Side note:
                    In order to compute the change in mortgage after one year we have the following closed form (n=12):
                            delta = ((1+p/n)^n - 1)*initial_debt - ((1+p)^n - 1)*x/p,
                    where p is interest rate per year, x is the amount we pay towards mortgage.                             
                    For no profit scenario we would like to have delta == 0.0, i.e., all we paid per month
                    went for interest rate, aka no profit.
                """
                "with_interest_rate_no_profit",
                get_positions(
                    monthly_rent=416.6666,
                    owner_share=0.0,
                    repayment_amount=416.6666,
                    yearly_interest_rate=0.05,
                    initial_debt=100_000,
                    depreciation_rate=0.0,
                ),
                YearlySummary(profit_before_taxes=0.0, income_tax=0.0, cashflow=0.0),
            ),
            (
                "with_interest_rate_profit_depreciation",
                get_positions(
                    monthly_rent=416.6666,
                    owner_share=0.0,
                    repayment_amount=416.6666,
                    yearly_interest_rate=0.05,
                    initial_debt=100_000,
                    depreciation_rate=0.01,
                    purchase_price=200_000,
                ),
                YearlySummary(
                    profit_before_taxes=-1600.0, income_tax=-320.0, cashflow=320.0
                ),
            ),
            (
                "own_usage",  # Tax should be equal to zero since it is own use.
                get_positions(
                    usage=UsageContext.OWN_USE,
                    monthly_rent=0.0,
                ),
                YearlySummary(profit_before_taxes=0.0, income_tax=0.0, cashflow=0.0),
            ),
        ]
    )
    @mock.patch(
        "immo_rechner.core.profit_calculator.ProfitCalculator.get_yearly_income_tax"
    )
    def test_yearly_simulation(
        self, name, positions, expected_output: YearlySummary, mock_tax
    ):
        # Given
        pc = ProfitCalculator(positions=positions, yearly_income=100_000)
        mock_tax.side_effect = lambda x: 0.2 * x

        # When
        output = pc.yearly_simulation()

        # Then
        self.assertAlmostEqual(
            output.profit_before_taxes, expected_output.profit_before_taxes, places=1
        )
        self.assertAlmostEqual(output.income_tax, expected_output.income_tax, places=1)
        self.assertAlmostEqual(output.cashflow, expected_output.cashflow, places=1)

    @mock.patch(
        "immo_rechner.core.profit_calculator.ProfitCalculator.get_yearly_income_tax"
    )
    def test_from_raw_data(self, mock_tax):
        # Given
        pc = self.get_profit_calculator()
        mock_tax.side_effect = lambda x: 0.2 * x

        expected_output = YearlySummary(
            profit_before_taxes=-1777.12, income_tax=-355.424, cashflow=355.424
        )

        # When
        output = pc.yearly_simulation()

        # Then
        self.assertAlmostEqual(
            output.profit_before_taxes, expected_output.profit_before_taxes, places=1
        )
        self.assertAlmostEqual(output.income_tax, expected_output.income_tax, places=1)
        self.assertAlmostEqual(output.cashflow, expected_output.cashflow, places=1)

    def test_simulate(self):
        # Given
        pc = self.get_profit_calculator()

        # When
        output = pc.simulate(n_years=10)
        output_pd = pc.simulate(n_years=10, to_pandas=True)

        # Then
        self.assertEqual(len(output), 10)
        self.assertEqual(output_pd.shape[0], 10)

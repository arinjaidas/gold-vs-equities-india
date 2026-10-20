import unittest
import numpy as np
import pandas as pd
from analysis import inr_assets, performance, portfolio_wealth, calendar_rolling_cagr, synthetic_prices, validate_prices


class InvestmentAnalysisChecks(unittest.TestCase):
    def test_currency_conversion(self):
        p = synthetic_prices().iloc[:5]
        np.testing.assert_allclose(inr_assets(p).SP500_INR, p.SP500_USD * p.USDINR)

    def test_drawdown_includes_initial_capital(self):
        p = pd.Series([1.0, .8, .9], index=pd.date_range('2020-01-01', periods=3))
        self.assertAlmostEqual(performance(p)['max_drawdown'], -.2)

    def test_portfolio_boundary_weights(self):
        assets = inr_assets(synthetic_prices())
        np.testing.assert_allclose(portfolio_wealth(assets, 1), assets.Gold / assets.Gold.iloc[0])
        np.testing.assert_allclose(portfolio_wealth(assets, 0), assets.Nifty / assets.Nifty.iloc[0])

    def test_calendar_window_requires_full_history(self):
        dates = pd.bdate_range('2010-01-01', '2022-01-03')
        elapsed = (dates - dates[0]).days / 365.25
        p = pd.Series(1.1 ** elapsed, index=dates)
        result = calendar_rolling_cagr(p, 10)
        self.assertTrue(result.loc[:'2019-12-31'].isna().all())
        np.testing.assert_allclose(result.dropna(), .1, atol=1e-10)

    def test_duplicate_dates_are_rejected(self):
        frame = synthetic_prices().iloc[:4]
        frame.index = pd.DatetimeIndex([frame.index[0]] * 4)
        with self.assertRaises(ValueError): validate_prices(frame)


if __name__ == '__main__': unittest.main()

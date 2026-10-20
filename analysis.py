"""Public reimplementation of the documented 2025 asset-allocation project.

Run --demo for reproducible synthetic prices, or --prices your_prices.csv.
Synthetic outputs demonstrate the workflow and are not historical returns.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REQUIRED = ['GOLD_INR', 'NIFTY_INR', 'SP500_USD', 'USDINR']


def validate_prices(frame):
    frame = frame.copy()
    frame.index = pd.to_datetime(frame.index, errors='raise')
    if frame.index.has_duplicates:
        raise ValueError('Dates must be unique.')
    if not set(REQUIRED).issubset(frame.columns):
        raise ValueError('Required columns: ' + ', '.join(REQUIRED))
    frame = frame[REQUIRED].sort_index().apply(pd.to_numeric, errors='raise')
    if frame.isna().any().any() or not np.isfinite(frame.to_numpy()).all():
        raise ValueError('Prices must be finite and complete; align calendars explicitly.')
    if (frame <= 0).any().any() or len(frame) < 3:
        raise ValueError('At least three observations of positive prices are required.')
    if frame.index[-1] <= frame.index[0]:
        raise ValueError('Sample must span positive calendar time.')
    return frame


def inr_assets(frame):
    p = validate_prices(frame)
    return pd.DataFrame({'Gold': p.GOLD_INR, 'Nifty': p.NIFTY_INR,
                         'SP500_INR': p.SP500_USD * p.USDINR}, index=p.index)


def performance(wealth, annual_rf=0.0, periods_per_year=252):
    wealth = pd.Series(wealth, dtype=float).dropna()
    if len(wealth) < 3 or (wealth <= 0).any():
        raise ValueError('Wealth must have at least three positive observations.')
    if periods_per_year <= 0 or annual_rf <= -1:
        raise ValueError('Invalid annualisation or risk-free-rate assumption.')
    returns = wealth.pct_change(fill_method=None).dropna()
    years = (wealth.index[-1] - wealth.index[0]).total_seconds() / (365.25 * 86400)
    if years <= 0:
        raise ValueError('Dates must span positive time.')
    daily_rf = (1 + annual_rf) ** (1 / periods_per_year) - 1
    excess = returns - daily_rf
    sd = returns.std(ddof=1)
    downside = np.sqrt(np.mean(np.minimum(excess.to_numpy(), 0.0) ** 2))
    tail = returns[returns <= returns.quantile(0.05)]
    return {
        'total_return': float(wealth.iloc[-1] / wealth.iloc[0] - 1),
        'cagr': float((wealth.iloc[-1] / wealth.iloc[0]) ** (1 / years) - 1),
        'annual_volatility': float(sd * np.sqrt(periods_per_year)),
        'max_drawdown': float((wealth / wealth.cummax() - 1).min()),
        'sharpe': float(excess.mean() / sd * np.sqrt(periods_per_year)) if sd > 1e-14 else None,
        'sortino': float(excess.mean() / downside * np.sqrt(periods_per_year)) if downside > 1e-14 else None,
        'return_percentile_05': float(returns.quantile(0.05)),
        'mean_lower_05_return': float(tail.mean()),
        'observations': int(len(wealth)), 'calendar_years': float(years)
    }


def portfolio_wealth(assets, gold_weight=0.2, rebalance='daily'):
    if not 0 <= gold_weight <= 1:
        raise ValueError('Gold weight must be between zero and one.')
    selected = assets[['Gold', 'Nifty']]
    weights = np.array([gold_weight, 1 - gold_weight])
    if rebalance == 'buy_and_hold':
        return (selected / selected.iloc[0]).mul(weights).sum(axis=1)
    if rebalance != 'daily':
        raise ValueError('Choose daily or buy_and_hold.')
    returns = selected.pct_change(fill_method=None)
    result = (1 + returns.iloc[1:].mul(weights).sum(axis=1)).cumprod()
    return pd.concat([pd.Series([1.0], index=selected.index[:1]), result])


def calendar_rolling_cagr(price, years=5):
    if years < 1:
        raise ValueError('Window must be a positive integer number of years.')
    out = pd.Series(np.nan, index=price.index, name=f'rolling_{years}y_cagr')
    for i, date in enumerate(price.index):
        target = date - pd.DateOffset(years=years)
        j = price.index.searchsorted(target, side='right') - 1
        if j < 0:
            continue
        elapsed = (date - price.index[j]).total_seconds() / (365.25 * 86400)
        out.iloc[i] = (price.iloc[i] / price.iloc[j]) ** (1 / elapsed) - 1
    return out


def synthetic_prices(seed=20261019):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2013-01-01', '2025-12-31')
    common = rng.normal(size=(len(dates) - 1, 1))
    noise = rng.normal(size=(len(dates) - 1, 4))
    shocks = 0.25 * common + np.sqrt(1 - 0.25 ** 2) * noise
    daily = np.array([0.00025, 0.0004, 0.00035, 0.00008]) + shocks * [0.009, 0.012, 0.011, 0.003]
    values = np.vstack([np.ones(4), np.exp(np.cumsum(daily, axis=0))]) * [2000, 100, 1400, 55]
    return pd.DataFrame(values, index=dates, columns=REQUIRED)


def download_prices(start, end):
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError('Install optional yfinance dependency or supply a CSV.') from exc
    tickers = dict(GOLD_INR='GOLDBEES.NS', NIFTY_INR='NIFTYBEES.NS', SP500_USD='^GSPC', USDINR='USDINR=X')
    data = yf.download(list(tickers.values()), start=start, end=end, auto_adjust=True, progress=False)
    closes = data['Close'].rename(columns={v: k for k, v in tickers.items()})
    # Retain only observed common dates. No price filling or fabricated returns.
    return validate_prices(closes[REQUIRED].dropna(how='any'))


def run(frame, output, synthetic=False, annual_rf=0.0, periods=252):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    assets = inr_assets(frame)
    wealth = assets / assets.iloc[0]
    wealth['Nifty80_Gold20_daily'] = portfolio_wealth(assets)
    wealth['Nifty80_Gold20_buy_hold'] = portfolio_wealth(assets, rebalance='buy_and_hold')
    summary = pd.DataFrame({c: performance(wealth[c], annual_rf, periods) for c in wealth}).T
    summary.to_csv(output / 'performance.csv', index_label='asset')
    wealth.to_csv(output / 'wealth.csv', index_label='Date')
    assets.pct_change(fill_method=None).corr().to_csv(output / 'correlations.csv')
    rolling = pd.DataFrame({c: calendar_rolling_cagr(assets[c], 5) for c in assets})
    rolling.to_csv(output / 'rolling_5y_cagr.csv', index_label='Date')
    allocations = []
    for weight in np.linspace(0, 1, 21):
        allocations.append(dict(gold_weight=float(weight), **performance(portfolio_wealth(assets, weight), annual_rf, periods)))
    pd.DataFrame(allocations).to_csv(output / 'allocation_comparison.csv', index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    wealth.plot(ax=ax)
    ax.set(title=('SYNTHETIC DEMONSTRATION: ' if synthetic else '') + 'Growth of one INR', ylabel='Wealth multiple', xlabel='Date')
    ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(output / 'growth.svg'); plt.close(fig)
    (output / 'run_metadata.json').write_text(json.dumps({'synthetic': synthetic, 'annual_risk_free_rate': annual_rf,
        'periods_per_year': periods, 'transaction_costs': 'not modelled', 'currency': 'INR',
        'sample_start': str(frame.index.min().date()), 'sample_end': str(frame.index.max().date()),
        'interpretation': 'Synthetic results are workflow examples, not historical investment performance.' if synthetic else 'Retrospective descriptive analysis.'}, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--demo', action='store_true'); mode.add_argument('--prices', type=Path); mode.add_argument('--download', action='store_true')
    parser.add_argument('--start', default='2015-01-01'); parser.add_argument('--end', default='2025-01-01')
    parser.add_argument('--output', default='demo_output'); parser.add_argument('--annual-rf', type=float, default=0.0)
    parser.add_argument('--periods', type=int, default=252)
    args = parser.parse_args()
    if args.demo: frame = synthetic_prices()
    elif args.prices: frame = validate_prices(pd.read_csv(args.prices, index_col='Date', parse_dates=True))
    else: frame = download_prices(args.start, args.end)
    print(run(frame, args.output, args.demo, args.annual_rf, args.periods).to_string())


if __name__ == '__main__':
    main()

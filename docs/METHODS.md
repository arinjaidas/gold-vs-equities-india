# Methods

## Currency and return conventions

The international benchmark is converted as `SP500_INR = SP500_USD × USDINR`. USDINR is INR per USD. Returns are then calculated from the converted level; adding two percentage returns would omit their interaction.

For wealth W and elapsed calendar years T, CAGR is `(W_end / W_start)^(1/T) - 1`. Volatility uses the sample standard deviation of period returns multiplied by the square root of the assumed observations per year. The default is 252. The risk-free rate is converted from an annual effective rate to its per-observation equivalent.

Drawdown is `W_t / running_max(W_t) - 1`, so the reported maximum drawdown is negative. Sharpe uses mean period excess return divided by period return standard deviation, with annualisation. Sortino uses the root mean squared negative excess returns across **all** observations, rather than the conditional standard deviation of losing days. Undefined zero-denominator ratios remain missing.

## Portfolio construction

Daily rebalancing compounds the fixed-weight sum of asset returns. Buy-and-hold begins with fixed capital shares and allows weights to drift. Their difference is an investment-rule difference, not an implementation error. The allocation grid is descriptive; the public code does not claim an out-of-sample optimal allocation.

Five-year rolling CAGR uses calendar offsets and an observed price at or before the target start date. No estimate is created before a complete history exists. The realised interval length is used in the exponent.

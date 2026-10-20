![Gold versus Equities in India](assets/header.svg)

# Gold versus Equities in India

INR-based asset comparison, drawdowns, rolling returns and gold-equity allocation analysis with reproducible synthetic examples.

**Research question:** How do growth, volatility, downside risk and diversification change when gold and equities are compared from an Indian investor's currency perspective?

**Public edition:** Reconstructed Python implementation with synthetic demonstration data and outputs.

**5 functional checks passed locally**, plus a complete demonstration run.

## What you can inspect

- Validate positive, finite prices and explicitly align observed common dates.
- Convert the US equity benchmark to INR using the contemporaneous USD/INR level.
- Compute calendar-time CAGR, annualised volatility, drawdowns and excess-return ratios.
- Compare daily rebalancing with buy-and-hold allocations.
- Evaluate a grid of 21 gold weights and complete five-year rolling windows.

## Results preview

All values below are synthetic or illustrative workflow results.

![Gold versus Equities in India results preview](demo_output/growth.svg)

| Series | CAGR (%) | Volatility (%) | Maximum drawdown (%) |
| --- | --- | --- | --- |
| Gold | 0.347797 | 14.5012 | -41.8218 |
| Nifty | 18.629 | 19.3282 | -29.3139 |
| SP500_INR | 5.91025 | 18.4916 | -33.9697 |
| Nifty80_Gold20_daily | 15.2416 | 15.9372 | -26.6112 |
| Nifty80_Gold20_buy_hold | 16.8611 | 17.9996 | -28.3411 |

The daily-rebalanced and buy-and-hold allocations differ because the rebalancing rule changes the wealth path. The example does not identify a historically best investment.

## Run the example

Use Python 3.12. From this project's directory:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -v
python analysis.py --demo --output demo_output
```

For an isolated environment, run `python -m venv .venv` first. Activate it with `source .venv/bin/activate` on Linux/macOS or `.venv\Scripts\activate` on Windows. The standard example runs offline after dependencies are installed.

The [notebook walkthrough](notebooks/01_results_walkthrough.ipynb) explains the saved outputs. Exact command-line options appear in [CLI.txt](docs/CLI.txt).

## Documentation

| Guide | What it covers |
| --- | --- |
| [Methods](docs/METHODS.md) | Formulas, assumptions and interpretation |
| [Data dictionary](docs/DATA_DICTIONARY.md) | Variables, units and validation rules |
| [Results](docs/RESULTS.md) | Actual bundled output and how to read it |
| [Reproducibility](REPRODUCIBILITY.md) | Commands, checks and the recorded environment |
| [Provenance and attribution](docs/PROVENANCE.md) | Historical context, reconstruction and contribution |
| [Roadmap](docs/ROADMAP.md) | Specific extensions, with unfinished work labelled |
| [References](docs/REFERENCES.md) | Method documentation and source links |

## Limits of interpretation

- Bundled results are synthetic, so their asset rankings are not historical evidence.
- Transaction costs, taxes and financing are not modelled.
- ETF proxies and a price index have different fee and distribution characteristics.
- The optional market-data download path was not exercised during release verification.

## Contribution and research context

Documented December 2025 investment-analysis project; public reconstruction prepared in October 2026.

Arinjai Das developed the documented investment-analysis scope. The public implementation was reconstructed with ChatGPT assistance after the original local scripts could not be recovered.

**Skills demonstrated:** Python, asset allocation, financial data, risk metrics, currency conversion, reproducible analysis.

[Portfolio](https://github.com/arinjaidas/My-Projects) · [GitHub profile](https://github.com/arinjaidas)

For the optional market-data downloader, install `requirements-download.txt`. That retrieval path is separate from the verified offline example.

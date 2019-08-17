
# Forex signals framework

Forex signals generation framework based on [backtrader](https://www.backtrader.com/docu/)
and [fxcmpy](https://fxcmpy.tpq.io/00_quick_start.html).

This framework can be used also to
- download forex data to local server
- backtest and evaluate different strategies

There is also implemented [algorithms description](./algorithm.md).

## Development
Local build
> python setup.py install
Testing
> python scripts/algo.py
Collect forex data to ./data directory using fxcmpy API
> python .\scripts\collect.py

# Contributing

Issues and pull requests are more than welcome.

We recommand using [`uv`](https://docs.astral.sh/uv) as project manager for development.

See https://docs.astral.sh/uv/getting-started/installation/ for installation 

### dev install

```bash
git clone https://github.com/vincentsarago/vsifile.git
cd vsifile

uv sync
```

You can then run the tests with the following command:

```sh
uv run pytest --cov vsifile --cov-report term-missing -s -vv
```

##### Performance tests

```sh
uv run --group benchmark pytest tests/benchmarks.py --benchmark-only --benchmark-columns 'min, max, mean, median' --benchmark-sort 'min'
```


### pre-commit

This repo is set to use `pre-commit` to run *isort*, *mypy* and *ruff* when committing new code.

```bash
uv run pre-commit install
uv run pre-commit run --all-files 
```

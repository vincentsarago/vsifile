# Contributing

Issues and pull requests are more than welcome.

### dev install

```bash
$ git clone https://github.com/vincentsarago/vsifile.git
$ cd vsifile
$ python -m pip install -e .["dev"]
```

You can then run the tests with the following command:

```sh
python -m pytest --cov vsifile --cov-report term-missing -s -vv
```

##### Performance tests

```sh
python -m pip install -e ".[benchmark]"
python -m pytest tests/benchmarks.py --benchmark-only --benchmark-columns 'min, max, mean, median' --benchmark-sort 'min'
```


### pre-commit

This repo is set to use `pre-commit` to run *isort*, *mypy* and *ruff* when committing new code.

```bash
$ pre-commit install
```

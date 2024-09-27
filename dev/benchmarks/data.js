window.BENCHMARK_DATA = {
  "lastUpdate": 1727442738290,
  "repoUrl": "https://github.com/vincentsarago/vsifile",
  "entries": {
    "vsifile Benchmarks": [
      {
        "commit": {
          "author": {
            "email": "vincent.sarago@gmail.com",
            "name": "vincentsarago",
            "username": "vincentsarago"
          },
          "committer": {
            "email": "vincent.sarago@gmail.com",
            "name": "vincentsarago",
            "username": "vincentsarago"
          },
          "distinct": true,
          "id": "5ec890a87fa0916be1478a736dd437edc87a3c5b",
          "message": "add benchmark",
          "timestamp": "2024-09-27T15:08:44+02:00",
          "tree_id": "7366524f0496ec63465b2b53508082443b1676c5",
          "url": "https://github.com/vincentsarago/vsifile/commit/5ec890a87fa0916be1478a736dd437edc87a3c5b"
        },
        "date": 1727442737431,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks.py::test_preview[None]",
            "value": 100.05668611494244,
            "unit": "iter/sec",
            "range": "stddev: 0.0034849754106474865",
            "extra": "mean: 9.994334600000911 msec\nrounds: 50"
          },
          {
            "name": "tests/benchmarks.py::test_preview[op1]",
            "value": 16.21769030082256,
            "unit": "iter/sec",
            "range": "stddev: 0.0068610304655547915",
            "extra": "mean: 61.66106155999785 msec\nrounds: 50"
          }
        ]
      }
    ]
  }
}
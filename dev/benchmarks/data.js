window.BENCHMARK_DATA = {
  "lastUpdate": 1727443040012,
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
      },
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
          "id": "732a2b7d7a2a2f32b464f24fc5d8a1dc5b700c5f",
          "message": "add benchmark in docs",
          "timestamp": "2024-09-27T15:15:37+02:00",
          "tree_id": "0bb83474f33b85edb5f1065d04db781c5c83f306",
          "url": "https://github.com/vincentsarago/vsifile/commit/732a2b7d7a2a2f32b464f24fc5d8a1dc5b700c5f"
        },
        "date": 1727443039716,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks.py::test_preview[None]",
            "value": 104.5597811650908,
            "unit": "iter/sec",
            "range": "stddev: 0.0034476008188711895",
            "extra": "mean: 9.563906779998774 msec\nrounds: 50"
          },
          {
            "name": "tests/benchmarks.py::test_preview[op1]",
            "value": 18.093606828375982,
            "unit": "iter/sec",
            "range": "stddev: 0.009766131886912754",
            "extra": "mean: 55.268140260001246 msec\nrounds: 50"
          }
        ]
      }
    ]
  }
}
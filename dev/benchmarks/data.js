window.BENCHMARK_DATA = {
  "lastUpdate": 1727443300445,
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
            "name": "With VSIFILE Opener: False",
            "value": 100.05668611494244,
            "unit": "iter/sec",
            "range": "stddev: 0.0034849754106474865",
            "extra": "mean: 9.994334600000911 msec\nrounds: 50"
          },
          {
            "name": "With VSIFILE Opener: True",
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
            "name": "With VSIFILE Opener: False",
            "value": 104.5597811650908,
            "unit": "iter/sec",
            "range": "stddev: 0.0034476008188711895",
            "extra": "mean: 9.563906779998774 msec\nrounds: 50"
          },
          {
            "name": "With VSIFILE Opener: True",
            "value": 18.093606828375982,
            "unit": "iter/sec",
            "range": "stddev: 0.009766131886912754",
            "extra": "mean: 55.268140260001246 msec\nrounds: 50"
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
          "id": "78721b766d819352ee9d8307af6978de334a80a9",
          "message": "fix name",
          "timestamp": "2024-09-27T15:19:55+02:00",
          "tree_id": "010a5b03e50c22f1c8911584286c5cfa6ede702a",
          "url": "https://github.com/vincentsarago/vsifile/commit/78721b766d819352ee9d8307af6978de334a80a9"
        },
        "date": 1727443300138,
        "tool": "pytest",
        "benches": [
          {
            "name": "With VSIFILE Opener: False",
            "value": 108.34518376838638,
            "unit": "iter/sec",
            "range": "stddev: 0.0034504117075387247",
            "extra": "mean: 9.229759599999738 msec\nrounds: 50"
          },
          {
            "name": "With VSIFILE Opener: True",
            "value": 17.703460482390756,
            "unit": "iter/sec",
            "range": "stddev: 0.004927897560326268",
            "extra": "mean: 56.48613167999997 msec\nrounds: 50"
          }
        ]
      }
    ]
  }
}
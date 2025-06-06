
```
=== Performance Report ===
CTXVarManager.use:
  Avg: 0.00ms
  Median: 0.00ms
  P95: 0.00ms
  Samples: 115797

ExceptionPlugin.dispatch:
  Avg: 97.49ms
  Median: 93.89ms
  P95: 171.51ms
  Samples: 38598

HeaderPlugin.dispatch:
  Avg: 148.58ms
  Median: 144.27ms
  P95: 230.08ms
  Samples: 38598

LogPlugin.dispatch:
  Avg: 123.28ms
  Median: 119.19ms
  P95: 201.79ms
  Samples: 38598

Middleware.dispatch:
  Avg: 123.15ms
  Median: 119.56ms
  P95: 211.59ms
  Samples: 115794

RequestAdapter.init:
  Avg: 0.00ms
  Median: 0.00ms
  P95: 0.00ms
  Samples: 115797

ResponseAdapter.init:
  Avg: 0.00ms
  Median: 0.00ms
  P95: 0.00ms
  Samples: 115794
```

```
{"stats":{"RequestAdapter.init":{"avg":0.0007832260503348891,"median":0.0005820038495585322,"p95":0.001586995495017618,"samples":115797},"CTXVarManager.use":{"avg":0.004702018928321254,"median":0.0012549935490824282,"p95":0.0026160974812228233,"samples":115797},"ResponseAdapter.init":{"avg":0.0008191471960358891,"median":0.0005859983502887189,"p95":0.0017799975466914475,"samples":115794},"ExceptionPlugin.dispatch":{"avg":97.48825301404477,"median":93.89427650239668,"p95":171.50904090049153,"samples":38598},"Middleware.dispatch":{"avg":123.14810828957144,"median":119.5600060018478,"p95":211.58971174736507,"samples":115794},"LogPlugin.dispatch":{"avg":123.2813731764304,"median":119.19057900013286,"p95":201.7850692031061,"samples":38598},"HeaderPlugin.dispatch":{"avg":148.583784310299,"median":144.2666785005713,"p95":230.08327100142196,"samples":38598}}}%
```
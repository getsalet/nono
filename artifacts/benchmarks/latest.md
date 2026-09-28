# Agnes concurrency benchmark

- Text model: `agnes-3.0-flash`
- Image model: `agnes-image-2.5-flash`
- Text keys detected: **14**
- Image keys detected: **14**
- Safe text concurrency: **72**
- Safe image concurrency: **72**

| Service | Concurrency | Success | Failure | Wall time |
|---|---:|---:|---:|---:|
| text | 40 | 40 | 0 | 10.589s |
| image | 40 | 40 | 0 | 43.446s |
| text | 56 | 56 | 0 | 37.852s |
| image | 56 | 56 | 0 | 71.112s |
| text | 72 | 72 | 0 | 31.455s |
| image | 72 | 72 | 0 | 52.349s |

# Agnes concurrency benchmark

- Text model: `agnes-3.0-flash`
- Image model: `agnes-image-2.5-flash`
- Text keys detected: **8**
- Image keys detected: **8**
- Safe text concurrency: **32**
- Safe image concurrency: **32**

| Service | Concurrency | Success | Failure | Wall time |
|---|---:|---:|---:|---:|
| text | 20 | 20 | 0 | 5.568s |
| image | 20 | 20 | 0 | 19.355s |
| text | 24 | 24 | 0 | 5.092s |
| image | 24 | 24 | 0 | 37.46s |
| text | 32 | 32 | 0 | 5.473s |
| image | 32 | 32 | 0 | 27.067s |

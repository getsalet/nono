# Agnes concurrency benchmark

- Text model: `agnes-3.0-flash`
- Image model: `agnes-image-2.5-flash`
- Text keys detected: **8**
- Image keys detected: **8**
- Safe text concurrency: **16**
- Safe image concurrency: **16**

| Service | Concurrency | Success | Failure | Wall time |
|---|---:|---:|---:|---:|
| text | 8 | 8 | 0 | 5.064s |
| image | 8 | 8 | 0 | 40.073s |
| text | 12 | 12 | 0 | 6.074s |
| image | 12 | 12 | 0 | 34.744s |
| text | 16 | 16 | 0 | 3.809s |
| image | 16 | 16 | 0 | 21.696s |

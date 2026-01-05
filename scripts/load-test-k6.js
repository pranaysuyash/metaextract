import http from 'k6/http';
import { check, sleep } from 'k6';
import { FormData } from 'https://jslib.k6.io/formdata/0.0.2/index.js';

// Configuration
export const options = {
  stages: [
    { duration: '30s', target: 20 }, // Ramp up to 20 users
    { duration: '1m', target: 20 },  // Stay at 20 users
    { duration: '30s', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'], // 95% of requests must complete below 5s
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
  },
};

// Test File (Base64 placeholder - normally load from disk)
const binFile = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 1, 0, 0, 0, 1, 8, 6, 0, 0, 0, 31, 21, 196, 137, 0, 0, 0, 10, 73, 68, 65, 84, 120, 156, 99, 0, 1, 0, 0, 5, 0, 1, 13, 10, 45, 180, 0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130]);

export default function () {
  const url = 'http://localhost:3000/api/images_mvp/extract';
  
  const fd = new FormData();
  fd.append('file', http.file(binFile, 'test-image.png', 'image/png'));

  const params = {
    headers: {
      'Content-Type': 'multipart/form-data; boundary=' + fd.boundary,
      'Accept': 'application/json',
    },
  };

  const res = http.post(url, fd.body(), params);

  check(res, {
    'is status 200': (r) => r.status === 200,
    'has jobId': (r) => r.json('jobId') !== undefined,
  });

  sleep(1);
}

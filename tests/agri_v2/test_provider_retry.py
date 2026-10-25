import io,unittest,urllib.error
from unittest.mock import patch
from automation.agri_v2.provider_retry import retry_seconds
from automation.agri_v2.client import ModelClient,ImageProviderError
class ProviderRetryTests(unittest.TestCase):
 def test_large_503_wait_not_truncated(self):self.assertEqual(retry_seconds('7200'),7200)
 def test_http_date_rounded_up_never_shortened(self):self.assertEqual(retry_seconds('Sun, 25 Oct 2026 03:00:00 GMT',1792897199.5),1)
 def test_invalid_missing_or_negative_value(self):
  for value in ('bad','-5',None):self.assertIsNone(retry_seconds(value))
 def test_client_preserves_503_retry_after(self):
  client=object.__new__(ModelClient);client.keys={'image':[('AGNES_API_KEY','test-secret')]};client.used={'image':0};client.env={'GITHUB_ACTIONS':'false'}
  error=urllib.error.HTTPError('https://apihub.agnes-ai.com/v1/images/generations',503,'error',{'Retry-After':'7200'},io.BytesIO(b'{"error":{"message":"image queue is full"}}'))
  with patch('urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(ImageProviderError) as cm:client.request('image','/images/generations',{'prompt':'test'},1)
   self.assertEqual(cm.exception.retry_after_seconds,7200);self.assertEqual(call.call_count,1)

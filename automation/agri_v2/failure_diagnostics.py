"""Allowlisted diagnostics only: never persist exception text or provider body."""
def failure_details(exc):
 from .client import ImageProviderError,TextProviderError,ModelOutputError,CapabilityError
 from .image_quality import ImageQualityError
 if isinstance(exc,ImageProviderError):kind='image_provider'
 elif isinstance(exc,TextProviderError):kind='text_provider'
 elif isinstance(exc,ModelOutputError):kind='model_output'
 elif isinstance(exc,ImageQualityError):kind='image_quality'
 elif isinstance(exc,CapabilityError):kind='capability_or_protocol'
 elif isinstance(exc,ValueError):kind='validation'
 else:kind='unexpected'
 allowed={'invalid_auth','forbidden','quota_limited','rate_limited','model_unavailable','request_rejected','provider_unavailable','http_error','network_or_timeout','text_empty_or_invalid_content','text_json_invalid','text_model_mismatch','text_content_missing'}
 category=getattr(exc,'category',None)
 row={'kind':kind,'category':category if category in allowed else 'unspecified'}
 status=getattr(exc,'http_status',None)
 if type(status)is int and 100<=status<=599:row['http_status']=status
 return row

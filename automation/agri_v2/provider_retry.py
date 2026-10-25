"""Parse provider Retry-After without truncating its requested wait."""
import email.utils,math,time

def retry_seconds(value,now=None):
 if not isinstance(value,str) or not value.strip():return None
 value=value.strip()
 if value.isdigit():return int(value)
 try:return max(0,math.ceil(email.utils.parsedate_to_datetime(value).timestamp()-(time.time() if now is None else now)))
 except (ValueError,TypeError,OverflowError):return None

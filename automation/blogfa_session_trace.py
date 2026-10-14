"""Read-only native lifecycle audit. Values stay in memory, never in reports."""
import datetime
import time
from email.utils import parsedate_to_datetime
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlsplit
from blogfa_wire_audit import url_shape

NATIVE_PATHS = {
    "/desktop/home.aspx", "/desktop/login.aspx", "/desktop/archive.aspx",
    "/desktop/post.aspx", "/desktop/autosave.aspx", "/desktop/",
}


def cookie_delta(previous, current):
    """Expose change flags and lengths, never values or value hashes."""
    return {
        "added": sorted(current.keys() - previous.keys()),
        "removed": sorted(previous.keys() - current.keys()),
        "changed": sorted(k for k in current.keys() & previous.keys()
                          if current[k] != previous[k]),
        "lengths": {k: len(v) for k, v in sorted(current.items())},
    }


def cookie_response_metadata(headers):
    out = []
    for raw in headers:
        jar = SimpleCookie()
        try:
            jar.load(raw)
            for name, item in jar.items():
                out.append({"name": name, "length": len(item.value),
                            "http_only": bool(item["httponly"]),
                            "secure": bool(item["secure"]),
                            "same_site": item["samesite"],
                            "path": item["path"]})
        except Exception:
            out.append({"parse_failed": True})
    return out


class SessionTrace:
    def __init__(self, page):
        self.page = page
        self.started = time.monotonic()
        self.events = []
        self._cookies = {}
        self._form = {}
        self._route_handler = self._route
        self._response_handler = self._response
        page.route("**/*", self._route_handler)
        page.on("response", self._response_handler)

    def _event(self, kind, **data):
        self.events.append({"at_seconds": round(time.monotonic() - self.started, 3),
                            "kind": kind, **data})

    def _route(self, route):
        request = route.request
        p = urlsplit(request.url)
        if (p.hostname == "www.blogfa.com" and request.method == "POST"
                and p.path.lower() in ("/desktop/post.aspx", "/desktop/autosave.aspx")):
            self._event("blocked_write", path=p.path, method=request.method,
                        forwarded_to_server=False)
            route.abort("aborted")
        else:
            route.continue_()

    def _response(self, response):
        p = urlsplit(response.url)
        if p.hostname != "www.blogfa.com" or p.path.lower() not in NATIVE_PATHS:
            return
        try:
            headers = response.all_headers()
            location = headers.get("location")
            date = headers.get("date")
            skew = None
            if date:
                skew = round((datetime.datetime.now(datetime.timezone.utc)
                              - parsedate_to_datetime(date)).total_seconds(), 1)
            self._event(
                "native_response", method=response.request.method,
                url=url_shape(response.url), status=response.status,
                location=url_shape(location) if location else None,
                set_cookies=cookie_response_metadata(
                    response.header_values("set-cookie")),
                client_minus_server_seconds=skew)
        except Exception as exc:
            # Exception messages can contain URLs/tokens. Only the type is safe.
            self._event("response_audit_unavailable", exception_type=type(exc).__name__)

    def checkpoint(self, label):
        cookies = {x["name"]: x["value"] for x in
                   self.page.context.cookies("https://www.blogfa.com/")}
        fields = self.page.evaluate("""() => {
          const b=document.querySelector('#btnPublish');
          if(!b)return null;
          return {action:b.form.action, hidden:Array.from(b.form.elements)
            .filter(e=>e.type==='hidden').map(e=>[e.name,e.value])};
        }""")
        form = {}
        summary = None
        if fields:
            query = parse_qs(urlsplit(fields["action"]).query)
            form = {**dict(fields["hidden"]),
                    **{"query:" + k: v[0] for k, v in query.items()}}
            summary = {
                "action": url_shape(fields["action"]),
                "changed_since_previous_form": sorted(
                    k for k in form.keys() & self._form.keys()
                    if form[k] != self._form[k]),
                "ten_matches_form_t": bool(cookies.get("ten")) and
                    cookies.get("ten") == query.get("t", [None])[0],
                "hidden_lengths": {k: len(v) for k, v in fields["hidden"]},
            }
            self._form = form
        self._event("checkpoint", label=label, url=url_shape(self.page.url),
                    cookies=cookie_delta(self._cookies, cookies), form=summary)
        self._cookies = cookies

    def report(self):
        return {"read_only_publication_guard": True, "events": self.events}

    def close(self):
        self.page.unroute("**/*", self._route_handler)
        self.page.remove_listener("response", self._response_handler)
        self._cookies.clear()
        self._form.clear()
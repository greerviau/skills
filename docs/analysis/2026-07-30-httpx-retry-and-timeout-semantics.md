# httpx 0.28.1: exception coverage, transport retries, and timeout semantics for `get_json`

**Question:** `skills/research/lit-research/scripts/common.py`'s `get_json()` wraps a plain `httpx.get(url, params=params, headers=hdrs, timeout=30, follow_redirects=True)` in a hand-rolled backoff loop that only retries on `except httpx.HTTPError` or an HTTP 429/5xx status. Three sub-questions follow from that, each researched independently below:

1. Does `httpx.HTTPError` cover every transient network failure the loop intends to retry (connection refused, DNS failure, connect/read/write/pool timeout, protocol errors), or can some of those bypass the `except` clause entirely?
2. Does httpx's default transport do any retrying of its own underneath `common.py`'s loop, which could compound the manual backoff?
3. Does the single scalar `timeout=30` apply uniformly across httpx's four timeout phases (connect/read/write/pool), or does it need per-phase tuning?

**Version checked:** httpx `0.28.1`, httpcore `1.0.9` - the exact versions `uv run` resolves for this script as of 2026-07-30 (`uv run --with httpx python -c "import httpx; print(httpx.__version__)"` from `skills/research/lit-research/scripts/`). Installed source read directly from `~/.cache/uv/archive-v0/J_GtFRWL-p900JG_/lib/python3.14/site-packages/httpx/` (and the co-installed `httpcore/`).

## 1. Does `httpx.HTTPError` cover the intended failure set?

| Claim | Citation | Confidence |
| --- | --- | --- |
| `HTTPError` is the base of the whole hierarchy; the transient-failure classes are `RequestError → TransportError → {TimeoutException, NetworkError, ProtocolError, ProxyError, UnsupportedProtocol}`. | `httpx/_exceptions.py:74,107,123` | high |
| Connect/read/write/pool timeouts (`ConnectTimeout`/`ReadTimeout`/`WriteTimeout`/`PoolTimeout`) are all subclasses of `TimeoutException(TransportError)` → `HTTPError`. | `httpx/_exceptions.py:132-161` | high |
| Connection-refused is `ConnectError(NetworkError)` → `TransportError` → `HTTPError`. | `httpx/_exceptions.py:167-190` | high |
| DNS resolution failures surface as the same `httpx.ConnectError` (httpx has no DNS-specific exception): `socket.gaierror` is an `OSError` subclass, and httpcore's backends map any `OSError` during `connect_tcp`/`start_tls` to `httpcore.ConnectError`, which httpx re-maps to `httpx.ConnectError`. | `httpcore/_backends/sync.py:148-154,202-211`; `httpcore/_exceptions.py:8-15`; `httpx/_transports/default.py:84,249-250` | high |
| Protocol-level errors are `LocalProtocolError`/`RemoteProtocolError` → `ProtocolError(TransportError)` → `HTTPError`. TLS handshake failures are not a distinct class - they map through the same `OSError → ConnectError` path as a plain connect failure. | `httpx/_exceptions.py:216-237`; `httpcore/_backends/sync.py:148-154` | high |
| **Gap:** `InvalidURL`, `CookieConflict`, and `StreamError` (and its subclasses) are real exceptions httpx can raise that are **not** subclasses of `HTTPError` and would bypass the `except httpx.HTTPError` clause. None of the three apply to `get_json`'s well-formed, hardcoded API URLs and single non-streamed `.json()` call, so they don't represent a live gap in this script, but they would matter if the function were reused with caller-supplied URLs. | `httpx/_exceptions.py:271-274,280-288,297-363` | high |
| **Gap (theoretical):** if httpcore raised an exception type absent from httpx's internal `HTTPCORE_EXC_MAP` (e.g. `ConnectionNotAvailable`), it would propagate unwrapped and **not** be an `HTTPError` subclass. Whether this can actually reach the caller in practice (vs. being absorbed by httpcore's own connection-pool scheduling) wasn't traced further. | `httpx/_transports/default.py:77-92,114-115` | moderate |

**Answer:** for this script's actual usage - a single non-streamed GET to a fixed API host - `except httpx.HTTPError` covers all seven transient-failure categories in the question. The exceptions it misses (`InvalidURL`, `CookieConflict`, `StreamError`) are programmer-error/misuse classes, not transient network conditions, so they're out of scope for a retry loop rather than a hole in one.
Citation: rows above (all `high`, read directly from the pinned source). Confidence: **high** - this answer draws only on the `high`-rated rows; the theoretical unmapped-exception gap (the one `moderate` row) doesn't bear on this script's actual call pattern and isn't load-bearing for the answer.

## 2. Does the default transport retry on its own?

| Claim | Citation | Confidence |
| --- | --- | --- |
| `httpx.get()` with no `transport=` builds an `HTTPTransport` via `Client._init_transport` with **no `retries=` argument passed** - so the transport's own default applies. | `httpx/_client.py:718-738`; `httpx/_api.py:174-207` | high |
| `HTTPTransport.__init__`'s `retries` parameter defaults to **`0`** - zero automatic retries unless a caller opts in explicitly (e.g. `httpx.HTTPTransport(retries=1)`). | `httpx/_transports/default.py:147,291` | high |
| That value passes straight through, unmodified, to `httpcore.ConnectionPool(..., retries=retries, ...)` - httpx does no retrying of its own, only forwards the knob. | `httpx/_transports/default.py:165,309` | high |
| Even if `retries` were raised above 0, httpcore's retry loop (`HTTPConnection._connect`) only wraps connection establishment (TCP connect + TLS handshake) and only catches `(ConnectError, ConnectTimeout)`; the actual request/response exchange happens outside that loop with no retry. | `httpcore/_sync/connection.py:105-165`; `httpcore/_sync/connection_pool.py:81-82` | high |
| The pool's own internal retry (`ConnectionNotAvailable`) is a scheduling condition, not a network-I/O retry; any other exception propagates immediately with no retry. | `httpcore/_sync/connection_pool.py:233-254` | high |
| Mid-request read/write failures or timeouts are therefore never retried transparently by the default transport - they surface directly to whatever sits on top. | Inference from the two rows above; no source states the negative explicitly | low |

**Answer:** with `retries=0` (the default `get_json` relies on implicitly), the default transport does no retrying before a connection is established, and even a nonzero `retries` would only cover that initial connect/TLS handshake, never a request already in flight - both read directly from source.
Citation: the four `high` rows above. Confidence: **high** for that much.
Whether *no* layer beneath what was traced here retries a failure that happens mid-request is a different, weaker claim: no source was found stating that negative outright, only the absence of a retry loop around the one call site traced (`ConnectionPool.handle_request`). Treat "httpx/httpcore never retry a mid-request failure" as an inference, not a confirmed absence.
Citation: the `low` row above. Confidence: **low** - this half of the answer inherits that row's confidence rather than the section's high-confidence rows, per the synthesis rule in `tech-research`'s own "Per-claim confidence" section.
What's actually established: `common.py`'s manual backoff is doing all of the retrying this research could verify; whether it's the *only* retry layer for a failure after the connection is already open is not settled here.

## 3. Does a scalar `timeout=30` apply uniformly?

| Claim | Citation | Confidence |
| --- | --- | --- |
| When `connect`/`read`/`write`/`pool` are all left unset, `Timeout.__init__` assigns the single scalar to all four. | `httpx/_config.py:121-130` (fallback branch); docstring example `Timeout(5.0)  # 5s timeout on all operations.` at line 79 | high |
| `get_json`'s actual call (`httpx.get(url, ..., timeout=30, ...)`) reaches exactly this path: `get()` → `request()` → `Client(timeout=30)` → `self._timeout = Timeout(30)`, a single positional value. | `httpx/_api.py:52,102-108,174-205`; `httpx/_client.py:212` | high |
| The four phases remain functionally distinct failure modes (connect/read/write/pool each raise their own exception type) even though one scalar budgets all of them identically here. Corroborated (not required) by the official docs' "fine tuning the configuration" section, though that page carries no version marker. | `httpx/_config.py:76-84` (separately configurable); `httpx/_exceptions.py:132-161` (the distinct exception types, per §1) | high |
| Background: when `timeout` is omitted entirely, the default is `5.0`s across all four phases (`DEFAULT_TIMEOUT_CONFIG = Timeout(timeout=5.0)`) - not this script's case, since it always passes `timeout=30`. | `httpx/_config.py:246`; `httpx/_api.py:52,184` | high |

**Answer:** yes, `timeout=30` in `get_json` applies the same 30-second budget to connect, read, write, and pool-acquisition uniformly. No per-phase tuning is in effect; a slow-to-free pool slot under connection-limit contention would time out on the same 30s budget as a slow connect or a slow response, which is worth knowing but isn't a bug given the script makes one request at a time.
Citation: the rows above (all `high`). Confidence: **high**.

## Net assessment for `common.py`

The retry loop's `except httpx.HTTPError` catches everything it's meant to for this script's usage pattern, and the scalar timeout behaves as the code already assumes - both confirmed at high confidence in §1 and §3. Whether httpx/httpcore add any retrying beneath `common.py`'s own loop for a mid-request failure is not fully confirmed and stays an inference (§2); it doesn't argue for changing the current retry loop, but it's the one part of this analysis that's a documented guess, not a proven absence.
Citation: §1's answer, §2's answer, §3's answer. Confidence: **low** - inherited from §2's weaker half, per the synthesis rule in `tech-research`'s own "Per-claim confidence" section: a synthesis carries the lowest confidence of what it rests on.

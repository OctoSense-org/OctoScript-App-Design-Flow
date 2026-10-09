//! Outgoing HTTP from a component to the app's own hosts, over WASI 0.2's
//! `wasi:http` (OctoSense ADR 0014, phase 3).
//!
//! ```ignore
//! use octosense_component::http;
//!
//! let response = http::get("https://api.example.com/v1/items")?;
//! let items = response.text();
//!
//! let created = http::post(
//!     "https://api.example.com/v1/items",
//!     "application/json",
//!     r#"{"name": "tea"}"#,
//! )?;
//!
//! let me = http::Request::get("https://api.example.com/v1/me")
//!     .header("accept", "application/json")
//!     .timeout(std::time::Duration::from_secs(3))
//!     .send()?;
//! ```
//!
//! A request blocks until the whole response has arrived, and returns it
//! whatever its status: a `404` is an `Ok` [`Response`]. An `Err` is a
//! request that got no response (a URL it cannot send, a host the app may
//! not reach, a connection or TLS failure, a timeout), as a readable string,
//! so `?` passes it on as the call's error.
//!
//! The component imports `wasi:http` only when it calls this module. ADR 0014
//! lets its requests reach only the hosts in the app's `network.hosts`, when
//! the manifest has the `net` capability, and only over HTTPS; never this
//! device or its local network (loopback, private and link-local addresses,
//! `localhost`, single-label and `.local`, `.lan`, `.internal` names), even
//! when listed. The host refuses any other request, and it fails with
//! `the host refused the request to <url>: …` (`HTTP-request-denied`). A call
//! of a component that may reach the network gets 10 s instead of 2 s, and
//! each request's timeouts end with the call.
//!
//! Outside a component, such as in `cargo test` on your machine, every
//! request fails with an error that says so.

use std::time::Duration;

/// A response: its status, its headers and its whole body.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Response {
    /// The status code, such as `200` or `404`.
    pub status: u16,
    /// The headers, in the order they arrived; [`header`](Response::header)
    /// finds one in any case. A value that is not UTF-8 has U+FFFD in place
    /// of its bad bytes.
    pub headers: Vec<(String, String)>,
    /// The body.
    pub body: Vec<u8>,
}

impl Response {
    /// The body as text; bytes that are not UTF-8 become U+FFFD.
    pub fn text(&self) -> String {
        String::from_utf8_lossy(&self.body).into_owned()
    }

    /// The first value of the header `name`, matched in any case.
    pub fn header(&self, name: &str) -> Option<&str> {
        self.headers
            .iter()
            .find(|(n, _)| n.eq_ignore_ascii_case(name))
            .map(|(_, value)| value.as_str())
    }
}

/// A request to build, then [`send`](Request::send).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Request {
    method: String,
    url: String,
    headers: Vec<(String, String)>,
    body: Option<Vec<u8>>,
    timeout: Option<Duration>,
}

impl Request {
    /// A request with `method` (`"GET"`, `"PUT"`, …) to an `https://` URL
    /// (`http://` is accepted here, but the host sends it only in tests and
    /// developers' runs that allow a local server).
    pub fn new(method: &str, url: &str) -> Request {
        Request {
            method: method.to_string(),
            url: url.to_string(),
            headers: Vec::new(),
            body: None,
            timeout: None,
        }
    }

    /// A `GET` request.
    pub fn get(url: &str) -> Request {
        Request::new("GET", url)
    }

    /// A `POST` request; give it a [`body`](Request::body).
    pub fn post(url: &str) -> Request {
        Request::new("POST", url)
    }

    /// Adds a header. The host sets `host`, `connection` and the other
    /// hop-by-hop headers itself, and refuses them here.
    pub fn header(mut self, name: &str, value: &str) -> Request {
        self.headers.push((name.to_string(), value.to_string()));
        self
    }

    /// The body to send, with a `content-length` header unless you set one.
    pub fn body(mut self, body: impl Into<Vec<u8>>) -> Request {
        self.body = Some(body.into());
        self
    }

    /// How long connecting, the first byte of the response, and each gap
    /// between its bytes may take. The call's own deadline still applies.
    pub fn timeout(mut self, timeout: Duration) -> Request {
        self.timeout = Some(timeout);
        self
    }

    /// Sends the request and waits for the whole response.
    pub fn send(&self) -> Result<Response, String> {
        send(self)
    }
}

/// `GET` from `url`.
pub fn get(url: &str) -> Result<Response, String> {
    Request::get(url).send()
}

/// `POST` `body` to `url`, as `content_type` (such as `"application/json"`).
pub fn post(url: &str, content_type: &str, body: impl AsRef<[u8]>) -> Result<Response, String> {
    Request::post(url)
        .header("content-type", content_type)
        .body(body.as_ref())
        .send()
}

/// An `http`/`https` URL's parts, as `wasi:http` takes them.
#[derive(Debug, PartialEq, Eq)]
#[cfg_attr(
    not(all(target_os = "wasi", target_env = "p2")),
    allow(dead_code, reason = "read only by the wasi:http request")
)]
struct Target<'a> {
    https: bool,
    /// The host, with its port if it has one.
    authority: &'a str,
    /// The path and query, at least `/`. The fragment is not sent.
    path_with_query: String,
}

/// Splits `url`; no percent-decoding, no normalising.
fn parse(url: &str) -> Result<Target<'_>, String> {
    let (scheme, rest) = url
        .split_once("://")
        .ok_or_else(|| format!("{url:?} is not a URL such as https://api.example.com/path"))?;
    let https = if scheme.eq_ignore_ascii_case("https") {
        true
    } else if scheme.eq_ignore_ascii_case("http") {
        false
    } else {
        return Err(format!("{url:?} is not an https:// or http:// URL"));
    };
    let rest = rest.split('#').next().unwrap_or_default();
    let (authority, path) = rest.split_at(rest.find(['/', '?']).unwrap_or(rest.len()));
    if authority.is_empty() {
        return Err(format!("{url:?} names no host"));
    }
    if authority.contains('@') {
        return Err(format!(
            "{url:?} carries a user name or password; send credentials in a header"
        ));
    }
    let path_with_query = match path {
        "" => "/".to_string(),
        query if query.starts_with('?') => format!("/{query}"),
        path => path.to_string(),
    };
    Ok(Target {
        https,
        authority,
        path_with_query,
    })
}

#[cfg(not(all(target_os = "wasi", target_env = "p2")))]
fn send(request: &Request) -> Result<Response, String> {
    parse(&request.url)?;
    Err(format!(
        "{} {}: octosense_component::http sends requests only from a component, built for wasm32-wasip2",
        request.method, request.url
    ))
}

#[cfg(all(target_os = "wasi", target_env = "p2"))]
use self::component::send;

/// The requests themselves, through `wasi:http/outgoing-handler`.
#[cfg(all(target_os = "wasi", target_env = "p2"))]
mod component {
    use std::time::Duration;

    use wasi::http::outgoing_handler;
    use wasi::http::types::{
        ErrorCode, Fields, HeaderError, IncomingBody, IncomingResponse, Method, OutgoingBody,
        OutgoingRequest, RequestOptions, Scheme,
    };
    use wasi::io::streams::StreamError;

    use super::{parse, Request, Response};

    /// The most `blocking-write-and-flush` takes at once.
    const WRITE_CHUNK: usize = 4096;
    /// The most one read asks for.
    const READ_CHUNK: u64 = 64 << 10;

    pub(super) fn send(request: &Request) -> Result<Response, String> {
        let url = request.url.as_str();
        let target = parse(url)?;
        let headers = Fields::new();
        for (name, value) in &request.headers {
            append(&headers, name, value)?;
        }
        if let Some(body) = &request.body {
            let declared = request
                .headers
                .iter()
                .any(|(name, _)| name.eq_ignore_ascii_case("content-length"));
            if !declared {
                append(&headers, "content-length", &body.len().to_string())?;
            }
        }
        let outgoing = OutgoingRequest::new(headers);
        outgoing
            .set_method(&method(&request.method))
            .map_err(|()| format!("{:?} is not an HTTP method", request.method))?;
        let scheme = if target.https {
            Scheme::Https
        } else {
            Scheme::Http
        };
        outgoing
            .set_scheme(Some(&scheme))
            .map_err(|()| format!("{url}: the host does not take its scheme"))?;
        outgoing
            .set_authority(Some(target.authority))
            .map_err(|()| format!("{url}: {:?} is not a host", target.authority))?;
        outgoing
            .set_path_with_query(Some(&target.path_with_query))
            .map_err(|()| format!("{url}: {:?} is not a path", target.path_with_query))?;
        let body = match request.body {
            Some(_) => Some(
                outgoing
                    .body()
                    .map_err(|()| format!("{url}: the request has no body to write"))?,
            ),
            None => None,
        };
        let options = request.timeout.map(options).transpose()?;
        // The request starts first, and its body follows (WASI 0.2's order):
        // the host reads the body as it sends it.
        let pending =
            outgoing_handler::handle(outgoing, options).map_err(|code| failure(url, &code))?;
        if let (Some(body), Some(bytes)) = (body, &request.body) {
            write(body, bytes);
        }
        pending.subscribe().block();
        match pending.get() {
            Some(Ok(Ok(response))) => read(url, response),
            Some(Ok(Err(code))) => Err(failure(url, &code)),
            Some(Err(())) | None => Err(format!("{url}: the response never arrived")),
        }
    }

    fn append(headers: &Fields, name: &str, value: &str) -> Result<(), String> {
        headers
            .append(name, value.as_bytes())
            .map_err(|error| match error {
                HeaderError::Forbidden => format!("the host sets the header {name:?} itself"),
                _ => format!("{name:?}: {value:?} is not a valid header"),
            })
    }

    fn method(name: &str) -> Method {
        match name.to_ascii_uppercase().as_str() {
            "GET" => Method::Get,
            "HEAD" => Method::Head,
            "POST" => Method::Post,
            "PUT" => Method::Put,
            "DELETE" => Method::Delete,
            "CONNECT" => Method::Connect,
            "OPTIONS" => Method::Options,
            "TRACE" => Method::Trace,
            "PATCH" => Method::Patch,
            _ => Method::Other(name.to_string()),
        }
    }

    fn options(timeout: Duration) -> Result<RequestOptions, String> {
        let options = RequestOptions::new();
        let nanos = u64::try_from(timeout.as_nanos()).unwrap_or(u64::MAX);
        options
            .set_connect_timeout(Some(nanos))
            .and_then(|()| options.set_first_byte_timeout(Some(nanos)))
            .and_then(|()| options.set_between_bytes_timeout(Some(nanos)))
            .map_err(|()| "the host takes no timeout for a request".to_string())?;
        Ok(options)
    }

    /// Writes the body, at most [`WRITE_CHUNK`] bytes at a time, and
    /// finishes it. It stops at the first error: a body the host or the
    /// server stopped taking ends the request, and its response, or the
    /// error in its place, says why better than the write could.
    fn write(body: OutgoingBody, bytes: &[u8]) {
        let Ok(stream) = body.write() else { return };
        for chunk in bytes.chunks(WRITE_CHUNK) {
            if stream.blocking_write_and_flush(chunk).is_err() {
                return;
            }
        }
        // The stream is the body's child: it goes before `finish`.
        drop(stream);
        let _ = OutgoingBody::finish(body, None);
    }

    fn read(url: &str, response: IncomingResponse) -> Result<Response, String> {
        let status = response.status();
        let headers = response
            .headers()
            .entries()
            .into_iter()
            .map(|(name, value)| (name, String::from_utf8_lossy(&value).into_owned()))
            .collect();
        let body = response
            .consume()
            .map_err(|()| format!("{url}: the response has no body"))?;
        let body = read_body(url, &body)?;
        Ok(Response {
            status,
            headers,
            body,
        })
    }

    fn read_body(url: &str, body: &IncomingBody) -> Result<Vec<u8>, String> {
        let stream = body
            .stream()
            .map_err(|()| format!("{url}: the response body cannot be read"))?;
        let mut bytes = Vec::new();
        loop {
            match stream.blocking_read(READ_CHUNK) {
                Ok(chunk) => bytes.extend_from_slice(&chunk),
                Err(StreamError::Closed) => return Ok(bytes),
                Err(StreamError::LastOperationFailed(error)) => {
                    return Err(match wasi::http::types::http_error_code(&error) {
                        Some(code) => failure(url, &code),
                        None => format!(
                            "the response from {url} broke off: {}",
                            error.to_debug_string()
                        ),
                    })
                }
            }
        }
    }

    /// Why a request got no response, readably, with the WASI error code.
    fn failure(url: &str, code: &ErrorCode) -> String {
        let why = match code {
            ErrorCode::HttpRequestDenied => {
                return format!(
                    "the host refused the request to {url}: its host is not in the app's \
                     network.hosts, is this device or its local network, or the request is \
                     plain HTTP ({code:?})"
                )
            }
            ErrorCode::DnsTimeout | ErrorCode::DnsError(_) | ErrorCode::DestinationNotFound => {
                "its host name was not found"
            }
            ErrorCode::ConnectionRefused => "the connection was refused",
            ErrorCode::ConnectionTimeout => "connecting took too long",
            ErrorCode::ConnectionReadTimeout | ErrorCode::HttpResponseTimeout => {
                "the server did not answer in time"
            }
            ErrorCode::ConnectionTerminated | ErrorCode::HttpResponseIncomplete => {
                "the connection ended before the response did"
            }
            ErrorCode::TlsProtocolError
            | ErrorCode::TlsCertificateError
            | ErrorCode::TlsAlertReceived(_) => "the TLS handshake failed",
            ErrorCode::HttpRequestUriInvalid => "the URL is not valid",
            ErrorCode::HttpRequestMethodInvalid => "the method is not valid",
            ErrorCode::HttpRequestBodySize(_) => "the body is not the size content-length says",
            _ => return format!("the request to {url} failed: {code:?}"),
        };
        format!("the request to {url} failed: {why} ({code:?})")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn target<'a>(https: bool, authority: &'a str, path_with_query: &str) -> Target<'a> {
        Target {
            https,
            authority,
            path_with_query: path_with_query.to_string(),
        }
    }

    #[test]
    fn a_url_splits_into_what_wasi_http_takes() {
        assert_eq!(
            parse("https://api.example.com/v1/items?page=2#top"),
            Ok(target(true, "api.example.com", "/v1/items?page=2"))
        );
        assert_eq!(
            parse("HTTP://127.0.0.1:8080"),
            Ok(target(false, "127.0.0.1:8080", "/"))
        );
        assert_eq!(
            parse("http://[::1]:9000?q=1"),
            Ok(target(false, "[::1]:9000", "/?q=1"))
        );
    }

    #[test]
    fn what_cannot_be_sent_is_an_error() {
        for (url, why) in [
            ("api.example.com/v1", "is not a URL"),
            ("ftp://example.com/x", "is not an https:// or http:// URL"),
            ("https:///path", "names no host"),
            (
                "https://me:secret@api.example.com/",
                "user name or password",
            ),
        ] {
            let error = parse(url).unwrap_err();
            assert!(error.contains(why), "{url}: {error}");
        }
    }

    #[test]
    fn outside_a_component_a_request_says_where_it_runs() {
        let error = get("https://api.example.com/").unwrap_err();
        assert!(error.contains("only from a component"), "{error}");
        // A URL it cannot send is still that error.
        assert!(get("nope").unwrap_err().contains("is not a URL"));
    }

    #[test]
    fn a_response_reads_as_text_and_finds_headers_in_any_case() {
        let response = Response {
            status: 200,
            headers: vec![("content-type".into(), "text/plain".into())],
            body: b"hello \xff".to_vec(),
        };
        assert_eq!(response.text(), "hello \u{fffd}");
        assert_eq!(response.header("Content-Type"), Some("text/plain"));
        assert_eq!(response.header("etag"), None);
    }
}

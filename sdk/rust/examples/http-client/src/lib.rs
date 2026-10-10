//! A component that reaches the network over HTTP with
//! `octosense_component::http` (OctoSense ADR 0014, phase 3). Its app's
//! manifest needs `net`; no host list, since an app's network declarations
//! are shown at install and not enforced while it runs:
//!
//! ```json
//! "capabilities": ["wasm", "net"]
//! ```
//!
//! The script calls `host.request("wasm.fetch", "https://api.example.com/v1/items", fn(r){ … })`.

#[octosense_component::export]
pub mod client {
    use std::time::Duration;

    use octosense_component::http;

    /// A response, as the app's script gets it: an object.
    pub struct Page {
        pub status: u16,
        pub content_type: Option<String>,
        pub body: String,
    }

    /// `GET` `url`. A 404 is a page too; an `Err` is a request that got no
    /// response, such as one to a server that never answers.
    pub fn fetch(url: &str) -> Result<Page, String> {
        http::get(url).map(page)
    }

    /// `POST` JSON text to `url`.
    pub fn post_json(url: &str, json: &str) -> Result<Page, String> {
        http::post(url, "application/json", json).map(page)
    }

    /// `GET` `url` with one more header and a shorter timeout: the request
    /// builder.
    pub fn fetch_with(url: &str, header: &str, value: &str) -> Result<Page, String> {
        http::Request::get(url)
            .header(header, value)
            .timeout(Duration::from_secs(5))
            .send()
            .map(page)
    }

    fn page(response: http::Response) -> Page {
        Page {
            status: response.status,
            content_type: response.header("content-type").map(str::to_string),
            body: response.text(),
        }
    }
}

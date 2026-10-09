//! The app's host services, called from a component through
//! `octosense:host` (OctoSense ADR 0014, phase 3).
//!
//! ```ignore
//! let answer = octosense_component::host::request("notes.get", r#"{"id": 1}"#)?;
//! ```
//!
//! [`request`] calls one of the app's host services as the app's script does
//! with `host.request`: a service named `family.method`, with JSON arguments
//! as text. It returns the service's JSON answer as text, or, as `Err`, why
//! there is none, so `?` passes it on as the call's error. Build the
//! arguments and read the answer with any JSON crate, such as `serde_json`.
//!
//! The component imports `octosense:host/services@0.1.0`
//! (`wit/octosense-host.wit`, OctoSense's own) only when it calls
//! [`request`]. The import needs no grant of its own. ADR 0014 lets it reach
//! only the host-service families the app's manifest grants in
//! `capabilities` (a system app's own namespace too), as the app with no
//! sheet and no prompt, so only the methods a background surface may call,
//! and never `wasm.*`; the call's deadline bounds the wait. A refusal reads,
//! for example, `dev.example.texttools was not granted the mail service,
//! which mail.list needs`.
//!
//! Outside a component, such as in `cargo test` on your machine, every call
//! fails with an error that says so.

/// The bindings of `octosense:host`, made from the WIT file beside this crate.
#[cfg(all(target_os = "wasi", target_env = "p2"))]
mod bindings {
    wit_bindgen::generate!({
        path: "wit/octosense-host.wit",
        world: "component-host",
    });
}

/// Calls the app's host service `service` (`family.method`, such as
/// `"notes.get"`) with `args`, JSON text such as `"{}"`: the service's
/// JSON answer as text, or why there is none.
pub fn request(service: &str, args: &str) -> Result<String, String> {
    call(service, args)
}

#[cfg(all(target_os = "wasi", target_env = "p2"))]
use self::bindings::octosense::host::services::request as call;

#[cfg(not(all(target_os = "wasi", target_env = "p2")))]
fn call(service: &str, _args: &str) -> Result<String, String> {
    Err(format!(
        "{service}: octosense_component::host calls the app's host services only from a component, built for wasm32-wasip2"
    ))
}

#[cfg(test)]
mod tests {
    #[test]
    fn outside_a_component_a_call_says_where_it_runs() {
        let error = super::request("notes.get", "{}").unwrap_err();
        assert!(
            error.starts_with("notes.get: ") && error.contains("only from a component"),
            "{error}"
        );
    }
}

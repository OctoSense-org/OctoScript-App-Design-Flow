//! A component that calls its app's host services with
//! `octosense_component::host` (OctoSense ADR 0014, phase 3). The import
//! needs no grant of its own: it reaches only the services whose family the
//! app's manifest grants in `capabilities`, such as `runtime` for
//! `runtime.list`.

#[octosense_component::export]
pub mod services {
    use octosense_component::host;

    /// Calls `service` (`family.method`) with JSON `args`: its JSON answer,
    /// as text.
    pub fn call(service: &str, args: &str) -> Result<String, String> {
        host::request(service, args)
    }

    /// The host APIs this build implements (`runtime.list`, with the
    /// `runtime` capability).
    pub fn host_apis() -> Result<String, String> {
        host::request("runtime.list", "{}")
    }
}

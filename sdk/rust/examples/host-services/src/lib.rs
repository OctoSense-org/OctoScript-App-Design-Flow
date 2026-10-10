//! A component that calls its app's host services with
//! `octosense_component::host` (OctoSense ADR 0014, phase 3). The import
//! keeps the app's identity and actual authorization. Capability names only
//! disclose usage; they do not grant or deny `runtime.list`.

#[octosense_component::export]
pub mod services {
    use octosense_component::host;

    /// Calls `service` (`family.method`) with JSON `args`: its JSON answer,
    /// as text.
    pub fn call(service: &str, args: &str) -> Result<String, String> {
        host::request(service, args)
    }

    /// The host APIs this build implements (`runtime.list`).
    pub fn host_apis() -> Result<String, String> {
        host::request("runtime.list", "{}")
    }
}

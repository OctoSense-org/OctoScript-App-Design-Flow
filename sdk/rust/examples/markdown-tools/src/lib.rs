//! An app component in ordinary Rust: Markdown tools with the unmodified
//! `pulldown-cmark` crate. `cargo build --target wasm32-wasip2 --release`
//! turns it into a component; an app's script calls, for example,
//! `host.request("wasm.to_html", {markdown: text}, fn(r) { … })`.

#[octosense_component::export]
pub mod markdown {
    use std::time::{SystemTime, UNIX_EPOCH};

    use pulldown_cmark::{html, Event, HeadingLevel, Parser, Tag, TagEnd};

    /// What `analyze` finds: a WIT record.
    pub struct Stats {
        pub words: u32,
        pub lines: u32,
        pub headings: Vec<String>,
    }

    /// A WIT enum.
    pub enum Length {
        Short,
        Medium,
        Long,
    }

    /// Markdown to HTML.
    pub fn to_html(markdown: &str) -> String {
        let mut out = String::new();
        html::push_html(&mut out, Parser::new(markdown));
        out
    }

    /// Word and line counts, and the headings down to level 3.
    pub fn analyze(markdown: &str) -> Stats {
        let mut headings = Vec::new();
        let mut current: Option<String> = None;
        for event in Parser::new(markdown) {
            match event {
                Event::Start(Tag::Heading { level, .. }) if level <= HeadingLevel::H3 => {
                    current = Some(String::new())
                }
                Event::Text(text) => {
                    if let Some(heading) = current.as_mut() {
                        heading.push_str(&text);
                    }
                }
                Event::End(TagEnd::Heading(_)) => headings.extend(current.take()),
                _ => {}
            }
        }
        Stats {
            words: markdown.split_whitespace().count() as u32,
            lines: markdown.lines().count() as u32,
            headings,
        }
    }

    /// How long the text is, as a WIT enum.
    pub fn measure(markdown: &str) -> Length {
        match markdown.split_whitespace().count() {
            0..=100 => Length::Short,
            101..=1000 => Length::Medium,
            _ => Length::Long,
        }
    }

    /// Writes the HTML into the app's storage (`std::fs`, with the app's
    /// `storage` grant). An error reaches the script as the call's error.
    pub fn save_html(markdown: &str, path: &str) -> Result<u64, String> {
        let html = to_html(markdown);
        std::fs::write(path, &html).map_err(|e| e.to_string())?;
        octosense_component::log(&format!("saved {} bytes to {path}", html.len()));
        Ok(html.len() as u64)
    }

    /// Milliseconds since the Unix epoch: the component's clock.
    pub fn now_ms() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0)
    }
}

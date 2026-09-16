//! Runtime data binding for the reviewed image-to-AppCard scene templates.
use crate::network::{hash, text};
use base64::{engine::general_purpose::STANDARD, Engine};
use serde_json::{json, Value};
use std::collections::HashMap;

pub fn visible(state: &Value) -> Vec<Value> {
    let folder = text(state, "folder");
    let query = text(state, "query").trim().to_lowercase();
    state["mailbox"]["messages"]
        .as_array()
        .into_iter()
        .flatten()
        .filter(|m| {
            let sent = m["source"] == "sent";
            (if folder == "sent" {
                sent && m["trashed"] != true
            } else if folder == "trash" {
                m["trashed"] == true
            } else {
                !sent && m["trashed"] != true && (m["archived"] == true) == (folder == "archive")
            }) && (folder != "unread" || m["unread"] == true)
                && (folder != "flagged" || m["flagged"] == true)
                && (query.is_empty() || text(m, "subject").to_lowercase().contains(&query))
        })
        .cloned()
        .collect()
}
pub fn find<'a>(node: &'a mut Value, id: &str) -> Option<&'a mut Value> {
    if node["id"] == id {
        return Some(node);
    }
    for child in node
        .get_mut("c")
        .and_then(Value::as_array_mut)
        .into_iter()
        .flatten()
    {
        if let Some(found) = find(child, id) {
            return Some(found);
        }
    }
    None
}
fn put(tree: &mut Value, id: &str, key: &str, value: Value) {
    if let Some(node) = find(tree, id) {
        node[key] = value;
    }
}
fn label(tree: &mut Value, id: &str, value: impl Into<String>) {
    put(tree, id, "text", value.into().into());
}
fn remove(tree: &mut Value, id: &str) {
    if let Some(children) = tree["c"].as_array_mut() {
        children.retain(|c| c["id"] != id);
        for c in children {
            remove(c, id);
        }
    }
}
fn moved(node: &mut Value, dy: f64) {
    if let Some(y) = node["y"].as_f64() {
        node["y"] = (y + dy).into();
    }
    for c in node["c"].as_array_mut().into_iter().flatten() {
        moved(c, dy);
    }
}
fn rename(node: &mut Value, old: &str, new: &str) {
    if let Some(id) = node["id"].as_str() {
        node["id"] = id.replacen(old, new, 1).into();
    }
    for c in node["c"].as_array_mut().into_iter().flatten() {
        rename(c, old, new);
    }
}
fn short(s: &str, max: usize) -> String {
    let s = s.split_whitespace().collect::<Vec<_>>().join(" ");
    if s.chars().count() > max {
        format!("{}…", s.chars().take(max - 1).collect::<String>())
    } else {
        s
    }
}
fn escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

/// The sanitised body alone (what `document` wraps in a page).
pub fn document_body(message: &Value) -> String {
    sanitized(message, body)
}

fn body(element: scraper::ElementRef<'_>, images: &Value) -> String {
    let name = element.value().name();
    if matches!(
        name,
        "script"
            | "style"
            | "iframe"
            | "object"
            | "embed"
            | "form"
            | "input"
            | "button"
            | "textarea"
            | "select"
            | "template"
            | "head"
            | "meta"
            | "base"
            | "link"
            | "title"
    ) {
        return String::new();
    }
    let allowed = matches!(
        name,
        "p" | "div"
            | "span"
            | "table"
            | "tr"
            | "td"
            | "th"
            | "tbody"
            | "thead"
            | "tfoot"
            | "img"
            | "br"
            | "a"
            | "h1"
            | "h2"
            | "h3"
            | "h4"
            | "h5"
            | "h6"
            | "ul"
            | "ol"
            | "li"
            | "b"
            | "i"
            | "em"
            | "strong"
            | "u"
            | "s"
            | "blockquote"
            | "pre"
            | "code"
            | "hr"
            | "center"
            | "font"
    );
    let mut out = String::new();
    if allowed {
        out.push_str(&format!("<{name}"));
        for (key, value) in element.value().attrs() {
            if !matches!(
                key,
                "href"
                    | "src"
                    | "style"
                    | "width"
                    | "height"
                    | "align"
                    | "bgcolor"
                    | "color"
                    | "face"
                    | "size"
                    | "colspan"
                    | "rowspan"
                    | "alt"
                    | "title"
            ) {
                continue;
            }
            let mut value = value.trim().to_owned();
            if matches!(key, "src" | "href") {
                if let Some(cid) = value.strip_prefix("cid:") {
                    value = images[cid.trim_matches(['<', '>'])]
                        .as_str()
                        .unwrap_or("")
                        .into();
                }
                let lower = value.to_lowercase();
                if !(lower.starts_with("https://")
                    || lower.starts_with("http://")
                    || lower.starts_with("mailto:")
                    || lower.starts_with('#')
                    || ["png", "jpeg", "gif", "webp"]
                        .iter()
                        .any(|mime| lower.starts_with(&format!("data:image/{mime};base64,"))))
                {
                    continue;
                }
            }
            out.push_str(&format!(" {key}=\"{}\"", escape(&value)));
        }
        out.push('>');
    }
    for child in element.children() {
        if let scraper::node::Node::Text(value) = child.value() {
            out.push_str(&escape(value));
        } else if let Some(child) = scraper::ElementRef::wrap(child) {
            out.push_str(&body(child, images));
        }
    }
    if allowed && !matches!(name, "img" | "br" | "hr") {
        out.push_str(&format!("</{name}>"));
    }
    out
}

pub fn document(message: &Value, address: &str) -> String {
    let html = sanitized(message, body);
    let images = if message["load_remote_images"] == true {
        "data: https: http:"
    } else {
        "data:"
    };
    let source = format!(
        r#"<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src {images}; style-src 'unsafe-inline'; font-src data:; base-uri 'none'; form-action 'none'; frame-src 'none'; script-src 'none'"><title>{}</title><style>html,body{{margin:0;padding:0;background:white;color:#1c1c1e;font-family:-apple-system,BlinkMacSystemFont,sans-serif;font-size:16px;overflow-wrap:anywhere}}header{{padding:8px 22px 18px;border-bottom:1px solid #e2e2e7;margin-bottom:18px}}h1{{font-size:27px;line-height:1.25;margin:0 0 24px}}.sender{{font-size:17px;font-weight:600}}.muted{{font-size:12px;color:#8e8e93}}main{{padding:0 22px 28px;line-height:1.55}}img,table{{max-width:100%!important}}img{{height:auto}}pre{{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere}}</style></head><body><header><h1>{}</h1><div class="sender">{}</div><div class="muted">To: {} · {}</div></header><main>{html}</main></body></html>"#,
        escape(text(message, "subject")),
        escape(text(message, "subject")),
        escape(text(message, "sender")),
        escape(address),
        escape(text(message, "time"))
    );
    format!(
        "data:text/html;charset=utf-8;base64,{}",
        STANDARD.encode(source)
    )
}

/// The message body as safe markup: the HTML part through the sanitiser, or
/// the plain part as preformatted text.
fn sanitized(message: &Value, body: fn(scraper::ElementRef<'_>, &Value) -> String) -> String {
    if text(message, "html").is_empty() {
        format!("<pre>{}</pre>", escape(text(message, "body")))
    } else {
        body(
            scraper::Html::parse_fragment(text(message, "html")).root_element(),
            &message["inline_images"],
        )
    }
}

/// The reader's document for the native Makepad HTML viewer: a small header
/// and the sanitised body, without a stylesheet or a CSP (there is no browser
/// to enforce them; the viewer keeps images out until asked). Same data-URL
/// shape as `document`, which is what the scene lowering requires.
pub fn native_document(message: &Value, address: &str) -> String {
    let html = document_body(message);
    let source = format!(
        "<h2>{}</h2><p><b>{}</b></p><p>To: {} · {}</p><hr>{html}",
        escape(text(message, "subject")),
        escape(text(message, "sender")),
        escape(address),
        escape(text(message, "time"))
    );
    format!("data:text/html;charset=utf-8;base64,{}", STANDARD.encode(source))
}

/// Flag categories: one colour each, the way iOS Mail flags work.
pub const FLAGS: [(&str, &str, u32); 6] = [
    ("red", "Urgent", 0xffff3b30u32),
    ("orange", "Follow up", 0xffff9500u32),
    ("yellow", "Waiting", 0xffffcc00u32),
    ("green", "Done", 0xff34c759u32),
    ("blue", "Work", 0xff0a84ffu32),
    ("purple", "Personal", 0xffaf52deu32),
];
pub fn flag_color(name: &str) -> Option<u32> {
    FLAGS.iter().find(|(id, _, _)| *id == name).map(|(_, _, c)| *c)
}
fn flag_hex(name: &str) -> String {
    format!("#{:06X}", flag_color(name).unwrap_or(0xff8e8e93u32) & 0xffffff)
}
fn stack(id: &str, x: f64, y: f64, w: f64, h: f64, bg: Option<u32>, radius: f64) -> Value {
    let mut n = json!({"t":"stack","id":id,"x":x,"y":y,"w":w,"h":h,"c":[]});
    if let Some(bg) = bg { n["variant"] = json!("surface"); n["bg"] = json!(bg); n["radius"] = json!(radius); }
    n
}
/// A single line of text centred in the box `y..y+h`: the label keeps the font's
/// natural line height (the template's 1.32×) and is offset to the box's middle,
/// since a taller line box would seat the glyphs at its top.
fn caption(id: &str, text: &str, x: f64, y: f64, w: f64, h: f64, size: f64, weight: u32, color: u32, alignx: f64) -> Value {
    let line = (size * 1.32 * 100.).round() / 100.;
    let top = ((y + (h - line) / 2.) * 100.).round() / 100.;
    json!({"t":"text","id":id,"text":text,"x":x,"y":top,"w":w,"h":line,"size":size,"line_height":line,"weight":weight,"color":color,
           "font_src":format!("self:resources/ux/Inter-{weight}.ttf"),"variant":"single_line","alignx":alignx})
}
/// A tappable pill: the stack is the Kit component, the button its hit area, the label its text.
fn pill(id: &str, text: &str, x: f64, y: f64, w: f64, h: f64, bg: u32, ink: u32, controls: &mut Value, event: &str, payload: Value) -> Value {
    // The Kit wrapper is a plain group; its surface, hit area and label are children.
    let mut n = stack(id, x, y, w, h, None, 0.0);
    n["kit"] = json!(json!({"widget":"KitButton","bindings":{"control":[1],"label":[2]}}).to_string());
    n["c"] = json!([
        stack(&format!("{id}_surface"), x, y, w, h, Some(bg), 10.0),
        {"t":"button","id":format!("{id}_control"),"x":x,"y":y,"w":w,"h":h,"enabled":true},
        caption(&format!("{id}_label"), text, x, y, w, h, 13.0, 600, ink, 0.5)
    ]);
    controls[id] = json!({"event":event,"payload":payload,"enabled":true});
    n
}
/// Swipe actions for one message: Delete (or Restore in Trash), Archive, Flag — and the colour
/// picker when it is open. `y` is the top of the 88-point band they sit in.
fn swipe_bar(prefix: &str, m: &Value, folder: &str, picker: bool, y: f64, controls: &mut Value) -> Vec<Value> {
    let id = m["id"].clone();
    let mut out = vec![stack(&format!("{prefix}_swipe_bg"), 150.0, y + 1.0, 256.0, 86.0, Some(0xfff2f2f7u32), 0.0)];
    let (del_text, del_event) = if folder == "trash" { ("Restore", "row_restore") } else { ("Delete", "row_delete") };
    let archive_text = if m["archived"] == true { "Unarchive" } else { "Archive" };
    out.push(pill(&format!("{prefix}_delete"), del_text, 158.0, y + 10.0, 76.0, 34.0, 0xffff3b30u32, 0xffffffffu32, controls, del_event, json!({"id":id})));
    out.push(pill(&format!("{prefix}_archive"), archive_text, 240.0, y + 10.0, 76.0, 34.0, 0xff0a84ffu32, 0xffffffffu32, controls, "row_archive", json!({"id":id})));
    let flag = text(m, "flag");
    out.push(pill(&format!("{prefix}_flag"), if flag.is_empty() { "Flag" } else { "Flagged" }, 322.0, y + 10.0, 76.0, 34.0, flag_color(flag).unwrap_or(0xffff9500u32), 0xffffffffu32, controls, "row_flag", json!({"id":id})));
    if picker {
        for (i, (name, _, color)) in FLAGS.iter().enumerate() {
            let x = 158.0 + i as f64 * 30.0;
            let mut dot = pill(&format!("{prefix}_flag_{name}"), "", x, y + 52.0, 26.0, 26.0, *color, 0xffffffffu32, controls, "set_flag", json!({"id":id,"flag":name}));
            dot["c"][0]["radius"] = json!(13.0);
            if flag == *name { dot["c"][0]["border"] = json!(2.0); dot["c"][0]["bordercolor"] = json!(0xff1c1c1eu32); }
            out.push(dot);
        }
        out.push(pill(&format!("{prefix}_flag_none"), "Clear", 340.0, y + 52.0, 58.0, 26.0, 0xffe5e5eau32, 0xff1c1c1eu32, controls, "set_flag", json!({"id":id,"flag":""})));
    }
    out
}

pub struct SceneFrame {
    pub value: Value,
    pub actions: HashMap<String, Value>,
    pub assets: HashMap<String, String>,
    pub mapping: HashMap<String, String>,
}
pub fn render(state: &Value, endpoint: &str, nonce: &str) -> SceneFrame {
    let templates: Value =
        serde_json::from_str(include_str!("../resources/mobile-templates.json")).unwrap();
    let screen = text(state, "screen");
    let key = if screen == "search" { "inbox" } else { screen };
    let mut scene = templates.get(key).unwrap_or(&templates["inbox"]).clone();
    let mut assets = HashMap::new();
    for (id, svg) in scene["assets"].as_object().unwrap() {
        assets.insert(format!("{key}/{id}.svg"), svg.as_str().unwrap().to_owned());
    }
    fn asset_urls(node: &mut Value, key: &str, endpoint: &str) {
        if node["t"] == "svg" {
            node["src"] = format!("{endpoint}/assets/{key}/{}.svg", text(node, "id")).into();
        }
        for c in node["c"].as_array_mut().into_iter().flatten() {
            asset_urls(c, key, endpoint);
        }
    }
    asset_urls(&mut scene["tree"], key, endpoint);
    let mut controls = scene["controls"].clone();
    let tree = &mut scene["tree"];
    if matches!(screen, "inbox" | "search") {
        label(tree, "top_action_label", "Refresh");
        controls["top_action"] = json!({"event":"sync","enabled":true});
        let rows = visible(state);
        let start =
            (state["list_start"].as_u64().unwrap_or(0) as usize).min(rows.len().saturating_sub(1));
        let row = find(tree, "message_0").unwrap().clone();
        let footer=find(tree,"list_footer").cloned().unwrap_or(json!({"t":"text","id":"list_footer","x":22,"y":0,"w":362,"h":30,"size":13,"weight":400,"color":4287532691u32,"text":"","font_src":"self:resources/ux/Inter-400.ttf","variant":"single_line"}));
        controls
            .as_object_mut()
            .unwrap()
            .retain(|id, _| !id.starts_with("message_"));
        let mut children = Vec::new();
        for (i, m) in rows.iter().enumerate().skip(start).take(60) {
            let id = format!("message_{i}");
            let mut item = row.clone();
            rename(&mut item, "message_0", &id);
            moved(&mut item, 88. * i as f64);
            for (suffix, value) in [
                ("sender", short(text(m, "sender"), 24)),
                ("subject", short(text(m, "subject"), 43)),
                ("preview", short(text(m, "preview"), 49)),
                ("time", text(m, "time").into()),
            ] {
                label(&mut item, &format!("{id}_{suffix}"), value);
            }
            if m["unread"] != true {
                remove(&mut item, &format!("{id}_unread"));
            }
            controls[format!("{id}_open")] =
                json!({"event":"open","payload":{"id":m["id"]},"enabled":true});
            let top = 242. + 88. * i as f64;
            if let Some(color) = flag_color(text(m, "flag")) {
                // The category colour, beside the time.
                item["c"].as_array_mut().unwrap().push(stack(&format!("{id}_flagdot"), 256.0, top + 16.0, 10.0, 10.0, Some(color), 5.0));
            }
            children.push(item);
            if state["swiped"] == m["id"] {
                let folder = text(state, "folder").to_owned();
                let picker = state["flag_picker"] == true;
                children.extend(swipe_bar(&id, m, &folder, picker, top, &mut controls));
            }
        }
        let more = state["mailbox"]["has_more"] == true
            && text(state, "folder") == "inbox"
            && text(state, "query").is_empty();
        let mut footer = footer;
        footer["y"] = (250. + 88. * rows.len() as f64).into();
        footer["text"] = if state["busy"] == true {
            "Loading mail…"
        } else if more {
            "Scroll for older messages"
        } else {
            "All messages loaded"
        }
        .into();
        children.push(footer);
        let content = find(tree, "list_content").unwrap();
        content["c"] = children.into();
        content["h"] = (462f64.max(rows.len() as f64 * 88. + 54.)).into();
        label(tree, "search_field_input", text(state, "query"));
        put(
            tree,
            "search_field_input",
            "focused",
            json!(i32::from(state["search_focused"] == true)),
        );
        label(
            tree,
            "heading",
            match text(state, "folder") {
                "unread" => "Unread",
                "flagged" => "Flagged",
                "archive" => "Archive",
                "sent" => "Sent",
                "trash" => "Trash",
                _ => "Inbox",
            },
        );
        label(tree, "message_count", format!("{} messages", rows.len()));
        label(
            tree,
            "sync_status",
            if state["busy"] == true {
                "Checking for mail…"
            } else if !text(state, "notice").is_empty() {
                text(state, "notice")
            } else if state["demo"] == true {
                "Demo mailbox · on device"
            } else {
                "Gmail · on device"
            },
        );
        if !text(state, "query").is_empty() {
            let mut clear = find(tree, "all_mail").unwrap().clone();
            rename(&mut clear, "all_mail", "clear_search");
            moved(&mut clear, -51.);
            clear["x"] = json!(340);
            clear["w"] = json!(42);
            if let Some(c) = clear["c"].as_array_mut() {
                c.retain(|n| n["t"] == "button" || n["t"] == "text");
                for n in c {
                    n["x"] = json!(340);
                    n["w"] = json!(42);
                    if n["t"] == "text" {
                        n["text"] = json!("×");
                    }
                }
            }
            tree["c"].as_array_mut().unwrap().push(clear);
            controls["clear_search"] = json!({"event":"clear_search","enabled":true});
        }
    } else if screen == "read" {
        remove(tree, "tool_move");
        if let Some(m) = state["mailbox"]["messages"]
            .as_array()
            .and_then(|a| a.iter().find(|m| m["id"] == state["selected"]))
        {
            put(
                tree,
                "message_html",
                "src",
                native_document(m, text(&state["mailbox"], "address")).into(),
            );
            // The toolbar flag shows the message's category colour.
            let flag = text(m, "flag");
            if let Some(svg) = assets.get_mut("read/tool_flag_icon.svg") {
                *svg = svg.replace("#FF9500", &flag_hex(if flag.is_empty() { "orange" } else { flag }));
            }
            controls["tool_flag"] = json!({"event":"row_flag","payload":{"id":m["id"]},"enabled":true});
            controls["tool_archive"] = json!({"event":"row_archive","payload":{"id":m["id"]},"enabled":true});
            // A swipe on the message reveals the same actions above it.
            controls["message_html"] = json!({"event":"reader_swipe","payload":{"id":m["id"]},"enabled":true});
            if state["reader_actions"] == true {
                let picker = state["flag_picker"] == true;
                let band = if picker { 88.0 } else { 56.0 };
                if let Some(html) = find(tree, "message_html") {
                    html["y"] = json!(88.0 + band);
                    html["h"] = json!(616.0 - band);
                }
                // The band starts at the message top (88): pills at 96, colour dots at 138, all shifted to the left edge.
                let mut bar = swipe_bar("reader", m, text(state, "folder"), picker, 86.0, &mut controls);
                bar[0]["x"] = json!(0.0); bar[0]["w"] = json!(406.0); bar[0]["y"] = json!(88.0); bar[0]["h"] = json!(band);
                fn shift_x(n: &mut Value, dx: f64) { if let Some(x) = n["x"].as_f64() { n["x"] = json!(x + dx); } for c in n["c"].as_array_mut().into_iter().flatten() { shift_x(c, dx); } }
                for node in bar.iter_mut().skip(1) {
                    shift_x(node, -142.0);
                }
                tree["c"].as_array_mut().unwrap().extend(bar);
            }
        }
    } else if screen == "mailboxes" {
        label(tree, "account_address", text(&state["mailbox"], "address"));
        label(
            tree,
            "account_status",
            if state["demo"] == true {
                "Demo"
            } else {
                "On device"
            },
        );
        // A seventh folder, Trash, cloned from the Archive row; everything below moves down.
        // The row, its count, its chevron and the divider above it are siblings in the template.
        let mut extra = Vec::new();
        for (source, target) in [("folder_5", "folder_6"), ("folder_count_5", "folder_count_6"), ("folder_arrow_5", "folder_arrow_6"), ("folder_line_5", "folder_line_6")] {
            if let Some(mut node) = find(tree, source).cloned() {
                rename(&mut node, source, target);
                moved(&mut node, 53.);
                extra.push(node);
            }
        }
        if !extra.is_empty() {
            label(&mut extra[0], "folder_6_label", "Trash");
            controls["folder_6"] = json!({"event":"folder","payload":{"folder":"trash"},"enabled":true});
            if let Some(children) = tree["c"].as_array_mut() {
                for node in children.iter_mut() {
                    if node["y"].as_f64().unwrap_or(0.) >= 477. && node["id"] != "home_indicator" {
                        moved(node, 53.);
                    }
                }
                let at = children.iter().position(|n| n["id"] == "folder_line_5").map(|i| i + 1).unwrap_or(children.len());
                for (k, node) in extra.into_iter().enumerate() {
                    children.insert(at + k, node);
                }
            }
        }
        for (i, folder) in ["sent", "inbox", "unread", "flagged", "drafts", "archive", "trash"]
            .iter()
            .enumerate()
        {
            let mut s = state.clone();
            s["folder"] = json!(folder);
            s["query"] = json!("");
            let count = if *folder == "drafts" {
                state["drafts"].as_array().map(Vec::len).unwrap_or(0)
            } else {
                visible(&s).len()
            };
            label(tree, &format!("folder_count_{i}"), count.to_string());
        }
        remove(tree, "gmail_folders");
        remove(tree, "new_mail_card");
    } else if matches!(screen, "settings" | "services") {
        for key in [
            "address",
            "username",
            "host",
            "port",
            "smtp_host",
            "smtp_port",
        ] {
            label(
                tree,
                &format!("server_{key}_input"),
                text(&state["account_form"], key),
            );
            put(
                tree,
                &format!("server_{key}_input"),
                "focused",
                json!(i32::from(
                    state["settings_focus"] == format!("server_{key}")
                )),
            );
        }
        label(
            tree,
            "server_password_label",
            if state["password_saved"] == true {
                "Saved · Change"
            } else {
                "Set Password"
            },
        );
        label(
            tree,
            "recent_toggle_label",
            if state["account_form"]["recent"] == true {
                "On"
            } else {
                "Off"
            },
        );
        label(tree, "outgoing_settings_label", "Outgoing mail settings");
        label(tree, "server_status_0", text(state, "notice"));
        label(tree, "use_sample_label", "Demo mailbox");
        label(tree, "use_gmail_label", "Open inbox");
        for mode in ["tls", "starttls"] {
            let id = format!("security_{mode}");
            let active = state["account_form"]["security"] == mode;
            if let Some(button) = find(tree, &id) {
                if find(button, &format!("{id}_surface")).is_none() {
                    let surface = json!({"t":"stack","id":format!("{id}_surface"),"x":button["x"],"y":button["y"],"w":button["w"],"h":button["h"],"variant":"surface","radius":12,"bg":4294967295u32,"c":[]});
                    button["c"].as_array_mut().unwrap().insert(1, surface);
                }
                put(
                    button,
                    &format!("{id}_surface"),
                    "bg",
                    json!(if active { 0xffffffffu32 } else { 0xffe4e4eau32 }),
                );
            }
        }
        if state["password_entry"] == true && screen == "settings" {
            remove(tree, "server_password");
            tree["c"]
                .as_array_mut()
                .unwrap()
                .push(templates["password_field"].clone());
            controls["password"] = json!({"event":"password","input":true,"enabled":true});
        }
        if screen == "services" {
            label(tree, "services_status_0", text(state, "notice"));
            remove(tree, "gmail_sync_toggle");
            label(tree, "gmail_sync_heading", "LOCAL MAIL ORGANIZATION");
            label(tree, "gmail_sync_label", "Flags and archive are local");
            label(tree, "gmail_sync_help", "Changes are saved on this phone");
            label(
                tree,
                "gmail_sync_server",
                "POP3 does not synchronize Gmail labels",
            );
            remove(tree, "test_services");
        }
    } else if screen == "compose" {
        for key in ["to", "subject", "body"] {
            label(tree, &format!("{key}_input"), text(&state["draft"], key));
        }
        label(
            tree,
            "send_status_0",
            if !text(state, "notice").is_empty() {
                text(state, "notice")
            } else if state["demo"] == true {
                "Demo mailbox · sending disabled"
            } else {
                "Sends directly from this device via TLS"
            },
        );
        label(
            tree,
            "top_action_label",
            if state["busy"] == true {
                "Sending…"
            } else {
                "Send"
            },
        );
        put(
            tree,
            "top_action_control",
            "enabled",
            json!(
                state["busy"] != true && state["send_uncertain"] != true && state["demo"] != true
            ),
        );
    } else if screen == "drafts" {
        let rows = state["drafts"].as_array().cloned().unwrap_or_default();
        if !rows.is_empty() {
            remove(tree, "no_drafts");
        }
        for (i, draft) in rows.iter().enumerate().rev().take(7) {
            let y = 160. + (rows.len() - 1 - i) as f64 * 70.;
            let id = format!("draft_{i}");
            let title = if text(draft, "subject").is_empty() {
                "(No subject)"
            } else {
                text(draft, "subject")
            };
            tree["c"].as_array_mut().unwrap().push(json!({"t":"stack","id":id,"x":20,"y":y,"w":366,"h":62,
                "kit":"{\"widget\":\"KitButton\",\"bindings\":{\"control\":[0]}}","c":[
                    {"t":"button","id":format!("{id}_control"),"x":20,"y":y,"w":366,"h":62,"enabled":true},
                    {"t":"text","id":format!("{id}_label"),"text":short(title,32),"x":30,"y":y+18.,"w":346,"h":24,"size":17,"line_height":22.44,"weight":400,"color":4278221567u32,"font_src":"self:resources/ux/Inter-400.ttf","variant":"single_line"}
                ]}));
            controls[id] = json!({"event":"open_draft","payload":{"index":i},"enabled":true});
        }
    } else if screen == "attachments" {
        let items = state["mailbox"]["messages"]
            .as_array()
            .and_then(|rows| rows.iter().find(|m| m["id"] == state["selected"]))
            .and_then(|m| m["attachment_items"].as_array())
            .cloned()
            .unwrap_or_default();
        if !items.is_empty() {
            remove(tree, "no_attachments");
        }
        if let Some(content) = find(tree, "attachment_content") {
            content["h"] = json!(478f64.max(items.len() as f64 * 86.));
            content["c"] = json!(items.iter().enumerate().map(|(i,item)|json!({"t":"text","id":format!("attachment_info_{i}"),"text":format!("{} · {} bytes",short(text(item,"filename"),28),item["size"]),"x":24,"y":175.+i as f64*86.,"w":358,"h":28,"size":15,"line_height":20,"weight":400,"color":4280032286u32,"font_src":"self:resources/ux/Inter-400.ttf","variant":"single_line"})).collect::<Vec<_>>());
        }
    }
    compile(tree, &controls, assets, endpoint, nonce, state)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn device_scenes_pass_the_same_l0_kit_and_native_lowering() {
        let mut state = json!({"mailbox":crate::device::demo_box(),"folder":"inbox","query":"","list_start":0,"list_scroll":0,"selected":"demo-0","account_form":crate::network::defaults(),"draft":{"to":"","subject":"","body":""},"drafts":[],"demo":true});
        state["mailbox"]["messages"][0]["subject"] =
            json!("News: \"quoted\" text { stays data } 中文");
        for screen in [
            "inbox",
            "read",
            "mailboxes",
            "settings",
            "services",
            "compose",
            "drafts",
            "attachments",
        ] {
            state["screen"] = json!(screen);
            let frame = render(&state, "http://127.0.0.1:8187/test", "unit");
            let report = octoscript_ui_l0::realize(
                frame.value["card"].as_str().unwrap(),
                &frame.value["data"],
                Default::default(),
            );
            let root = report
                .complete_root()
                .unwrap_or_else(|error| panic!("{screen}: {error}"));
            let source =
                octoscript_ui_l0::kit_pack::lower(root, &frame.value["pack"], &frame.value["data"])
                    .unwrap();
            let mut tree = octoscript_makepad::design::prepare(&source).unwrap();
            octoscript_makepad::l0::inspectable(&mut tree);
            assert!(!octoscript_makepad::design::to_makepad_ui(&tree)
                .unwrap()
                .is_empty());
        }
    }

    #[test]
    fn email_html_stays_inert_and_preserves_tables() {
        let message = json!({"subject":"<untrusted>","sender":"Sender","time":"Today","html":"<script>alert(1)</script><form action='https://example.com'><input></form><table><tr><td onclick='bad()'>Useful text</td></tr></table><img src='https://example.com/track'><iframe src='https://example.com'></iframe>","inline_images":{}});
        let url = document(&message, "reader@example.com");
        let html =
            String::from_utf8(STANDARD.decode(url.split_once(',').unwrap().1).unwrap()).unwrap();
        assert!(html.contains("<table>") && html.contains("Useful text"));
        assert!(
            !html.contains("<script")
                && !html.contains("onclick")
                && !html.contains("<form")
                && !html.contains("<iframe")
        );
        assert!(
            html.contains("img-src data:;")
                && html.contains("script-src 'none'")
                && html.contains("&lt;untrusted&gt;")
        );
    }
}

fn compile(
    tree: &Value,
    controls: &Value,
    assets: HashMap<String, String>,
    _endpoint: &str,
    nonce: &str,
    state: &Value,
) -> SceneFrame {
    let mut pack = json!({"schema_version":1,"theme":"light","tokens":{},"components":{}});
    let mut placements = json!({});
    let mut declarations = String::new();
    let mut definitions = std::collections::BTreeMap::new();
    let mut actions = HashMap::new();
    let mut mapping = HashMap::new();
    fn emit(
        node: &Value,
        depth: usize,
        path: &str,
        parent_control: Option<&Value>,
        controls: &Value,
        pack: &mut Value,
        placements: &mut Value,
        declarations: &mut String,
        definitions: &mut std::collections::BTreeMap<String, String>,
        actions: &mut HashMap<String, Value>,
        mapping: &mut HashMap<String, String>,
    ) -> String {
        let id = text(node, "id");
        mapping.insert(id.into(), path.into());
        let control = controls.get(id).or(parent_control);
        if let Some(control) = control {
            actions.insert(path.into(), control.clone());
        }
        let mut style = node.clone();
        let obj = style.as_object_mut().unwrap();
        for key in [
            "id",
            "c",
            "x",
            "y",
            "w",
            "h",
            "src",
            "text",
            "placeholder",
            "enabled",
            "selected",
        ] {
            obj.remove(key);
        }
        let mut props = json!({});
        let mut params = vec!["instance: text".to_owned()];
        let mut args = vec!["instance: instance".to_owned()];
        let mut call = vec![format!("instance: {}", json!(id))];
        for key in ["text", "placeholder", "enabled", "selected"] {
            if let Some(value) = node.get(key) {
                props[key] = json!(key);
                let boolean = matches!(key, "enabled" | "selected");
                params.push(format!("{key}: {}", if boolean { "bool" } else { "text" }));
                args.push(format!("{key}: {key}"));
                let name = format!("{id}_{key}");
                if boolean {
                    declarations.push_str(&format!(
                        "state {name} {{ shape: bool, initial: {} }}\n",
                        value == true || value == 1
                    ));
                    call.push(format!("{key}: {name}"));
                } else {
                    declarations.push_str(&format!(
                        "copy {name} {{ class: user-copy, en: {value} }}\n"
                    ));
                    call.push(format!("{key}: copy.{name}"));
                }
            }
        }
        let slot = node.get("c").is_some();
        let component = format!("Mail{}", &hash(&format!("{style}{props}{slot}"))[..14]);
        pack["components"][&component] = json!({"style":style,"props":props,"slot":slot});
        let mut layout = json!({});
        for key in ["x", "y", "w", "h", "src"] {
            if let Some(v) = node.get(key) {
                layout[key] = v.clone();
            }
        }
        placements[id] = json!({"component":component,"layout":layout});
        definitions.insert(
            component.clone(),
            format!(
                "component {component}({}) {{\n view Kit(component: {}, {}){}\n}}\n",
                params.join(", "),
                json!(component),
                args.join(", "),
                if slot { " { slot }" } else { "" }
            ),
        );
        let mut out = format!("{}{component}({})", "  ".repeat(depth), call.join(", "));
        if let Some(children) = node["c"].as_array() {
            out.push_str(" {\n");
            for (i, child) in children.iter().enumerate() {
                out.push_str(&emit(
                    child,
                    depth + 1,
                    &format!("{path}_{i}"),
                    control,
                    controls,
                    pack,
                    placements,
                    declarations,
                    definitions,
                    actions,
                    mapping,
                ));
                out.push('\n');
            }
            out.push_str(&format!("{}}}", "  ".repeat(depth)));
        }
        out
    }
    let body = emit(
        tree,
        0,
        "beauty_0",
        None,
        controls,
        &mut pack,
        &mut placements,
        &mut declarations,
        &mut definitions,
        &mut actions,
        &mut mapping,
    );
    let card=format!("# ledger mail-device@1.0.0\n# level: L0\n# profile: ui/l0\ntheme light\n{declarations}{}\nview root {body}\n",definitions.values().cloned().collect::<String>());
    let mut value = json!({"nonce":nonce,"card":card,"data":{"$kit":{"theme":"light","placements":placements}},"pack":pack,"preserve_input_selection":true});
    if matches!(text(state, "screen"), "inbox" | "search") {
        value["scroll_watch"] =
            json!([{"id":mapping["list_scroll"],"content":mapping["list_content"]}]);
        value["scroll_restore"] = json!([{"id":mapping["list_scroll"],"y":state["list_scroll"]}]);
    }
    SceneFrame {
        value,
        actions,
        assets,
        mapping,
    }
}

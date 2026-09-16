//! Native AppCard Mail module. The USB companion owns the existing Python mail service.
use makepad_app_module::{
    makepad_ai_services::wire::{ServiceCall, ServiceManifest, ToolResult},
    AppModule, ExecOutcome, InstanceHandles, InstanceParts, OpenArgKind, OpenSchema,
    ServiceExecutor, ValidatedOpen,
};
pub use makepad_widgets;
use makepad_widgets::makepad_platform::event::TouchState;
use makepad_widgets::*;
use serde_json::{json, Value};
mod device;
mod network;
mod scenes;

script_mod! {
    use mod.prelude.widgets.*
    mod.widgets.MailView = set_type_default() do #(MailView::register_widget(vm)) {
        width: Fill height: Fill flow: Overlay
        show_bg: true draw_bg.color: #fff
        host := Splash {
            width: Fill height: Fill
            padding: 24
            Label { width: Fill draw_text.wrap: Words text: "Opening Mail…" }
        }
    }
}

#[derive(Script, ScriptHook, Widget)]
pub struct MailView {
    #[deref]
    view: View,
    #[rust]
    endpoint: String,
    #[rust]
    device: Option<device::DeviceRuntime>,
    #[rust]
    timer: Timer,
    #[rust]
    started: bool,
    #[rust]
    pending_request: Option<LiveId>,
    #[rust]
    nonce: String,
    #[rust]
    sequence: u64,
    #[rust]
    request_sequence: u64,
    #[rust]
    actions: Vec<Value>,
    #[rust]
    elements: Vec<Value>,
    #[rust]
    frame: Value,
    #[rust]
    viewport: DVec2,
    #[rust]
    origin: DVec2,
    #[rust]
    scale: f64,
    #[rust]
    retired: Option<View>,
    #[rust]
    pending_layout: bool,
    #[rust]
    pending_selection: Option<makepad_draw::text::selection::Selection>,
    #[rust]
    list_drag: Option<(u64, f64, f64, String)>,
    #[rust]
    suppress_activation: bool,
}

fn retire(cx: &mut Cx, widget: &WidgetRef) {
    octoscript_widgets::kit::retire_overlay(cx, widget);
    let mut children = Vec::new();
    widget.children(&mut |_, child| children.push(child));
    for child in children {
        retire(cx, &child);
    }
}

impl MailView {
    fn exchange(&mut self, cx: &mut Cx) {
        if self.endpoint.is_empty() || self.pending_request.is_some() {
            return;
        }
        let mut scroll = Vec::new();
        if !self.pending_layout {
            if let Some(watches) = self.frame["scroll_watch"].as_array() {
                for watch in watches {
                    let (Some(id), Some(content)) =
                        (watch["id"].as_str(), watch["content"].as_str())
                    else {
                        continue;
                    };
                    let viewport = self.view.widget(cx, &[LiveId::from_str(id)]).area();
                    let content = self.view.widget(cx, &[LiveId::from_str(content)]).area();
                    if viewport.is_valid(cx) && content.is_valid(cx) {
                        let v = viewport.rect(cx);
                        let c = content.rect(cx);
                        scroll.push(json!({"id":id,"y":(v.pos.y-c.pos.y).max(0.)/self.scale,
                            "max_y":(c.size.y-v.size.y).max(0.)/self.scale,"viewport_height":v.size.y/self.scale}));
                    }
                }
            }
        }
        self.request_sequence += 1;
        let id = LiveId(self.widget_uid().0 ^ 0x4D41_494C_0000_0000 ^ self.request_sequence);
        let mut request = HttpRequest::new(format!("{}/exchange", self.endpoint), HttpMethod::POST);
        request.set_header("Content-Type".into(), "application/json".into());
        let layout: Vec<_> = self
            .elements
            .iter()
            .filter_map(|e| {
                let id = e["id"].as_str()?;
                let area = self.view.widget(cx, &[LiveId::from_str(id)]).area();
                if !area.is_valid(cx) {
                    return None;
                }
                let r = area.rect(cx);
                Some(json!({"id":id,"bounds":[r.pos.x,r.pos.y,r.size.x,r.size.y]}))
            })
            .collect();
        if std::env::var("MAIL_TRACE").is_ok() && !self.actions.is_empty() {
            log!("mail: exchange sends {} action(s): {}", self.actions.len(), json!(self.actions));
        }
        request.set_string_body(json!({"nonce":self.nonce,"sequence":self.sequence,"actions":self.actions,"scroll":scroll,"layout":layout}).to_string());
        self.pending_request = Some(id);
        cx.http_request(id, request);
    }

    fn mount(&mut self, cx: &mut Cx, frame: Value) -> Result<(), String> {
        let card = frame["card"].as_str().ok_or("missing card")?;
        let report = octoscript_ui_l0::realize(card, &frame["data"], Default::default());
        let source = octoscript_ui_l0::kit_pack::lower(
            report.complete_root()?,
            &frame["pack"],
            &frame["data"],
        )?;
        let mut tree = octoscript_makepad::design::prepare(&source)?;
        self.elements = octoscript_makepad::l0::inspectable(&mut tree);
        // The launcher supplies status/navigation chrome; preserve stable pipeline IDs
        // while hiding the standalone drawing of those same elements.
        let scale = (self.viewport.x / 406.).clamp(0.5, 2.0);
        let vertical = (self.viewport.y / 716.).clamp(0.4, 2.0);
        self.scale = vertical;
        fn fit(node: &mut octoscript_node::UiNode, scale: f64, vertical: f64, origin: DVec2) {
            let a = &mut node.attrs;
            if let Some(v) = &mut a.x {
                *v = *v * scale + origin.x;
            }
            if let Some(v) = &mut a.y {
                *v = (*v - 36.) * vertical + origin.y;
            }
            for value in [&mut a.h, &mut a.line_height] {
                if let Some(v) = value {
                    *v *= vertical as f32;
                }
            }
            for value in [&mut a.w, &mut a.size, &mut a.radius] {
                if let Some(v) = value {
                    *v *= scale as f32;
                }
            }
            for child in &mut node.children {
                fit(child, scale, vertical, origin);
            }
        }
        fit(&mut tree, scale, vertical, self.origin);
        tree.attrs.y = Some(self.origin.y);
        tree.attrs.h = Some(self.viewport.y as f32);
        for item in &self.elements {
            if matches!(
                item["original_id"].as_str(),
                Some("clock" | "signal" | "battery" | "battery_tip" | "home_indicator")
            ) {
                fn hide(node: &mut octoscript_node::UiNode, id: &str) {
                    if node.attrs.id.as_deref() == Some(id) {
                        node.attrs.w = Some(0.);
                        node.attrs.h = Some(0.);
                        node.attrs.text = Some(String::new());
                    }
                    for child in &mut node.children {
                        hide(child, id);
                    }
                }
                if let Some(id) = item["id"].as_str() {
                    hide(&mut tree, id);
                }
            }
        }
        let ui = octoscript_makepad::design::to_makepad_ui(&tree)?;
        // The reader is the native Makepad HTML viewer, not a platform WebView.
        let ui = ui.replace("Browser {", "MailHtml {").replace("backend: BrowserBackend.Native ", "");
        let sm = ScriptMod {
            cargo_manifest_path: env!("CARGO_MANIFEST_DIR").into(), module_path: module_path!().into(),
            file: file!().into(), line: 1, column: 0, values: Vec::new(),
            code: format!("use mod.prelude.widgets.*\nreturn View{{width:Fill height:Fill flow:Overlay {ui}}}"),
        };
        self.pending_selection = if frame["preserve_input_selection"].as_bool() == Some(true) {
            self.elements
                .iter()
                .find(|e| e["focused"] == 1)
                .and_then(|e| {
                    let id = e["id"].as_str()?;
                    let widget = self.view.widget(cx, &[LiveId::from_str(id)]);
                    let input = widget.borrow::<TextInput>()?;
                    cx.has_key_focus(input.area()).then(|| input.selection())
                })
        } else {
            None
        };
        cx.set_key_focus(Area::Empty);
        let view = cx.with_vm(|vm| {
            vm.eval_checked(sm, 2_000_000)
                .map(|value| View::script_from_value(vm, value))
                .ok_or_else(|| format!("Mail widget tree rejected: {:?}", vm.bx.captured_errors))
        })?;
        let host = self.view.widget(cx, ids!(host));
        let mut host = host.borrow_mut::<Splash>().ok_or("Mail host missing")?;
        self.retired = Some(std::mem::replace(&mut host.view, view));
        if let Some(old) = &self.retired {
            for (_, child) in &old.children {
                retire(cx, child);
            }
        }
        let uid = host.widget_uid();
        let mut children = Vec::new();
        host.children(&mut |id, child| children.push((id, child)));
        drop(host);
        for (id, child) in children {
            cx.widget_tree_insert_child_deep(uid, id, child);
        }
        cx.widget_tree_mark_dirty(uid);
        for element in &self.elements {
            if let (Some(id), Some(enabled)) = (element["id"].as_str(), element["enabled"].as_i64())
            {
                self.view
                    .widget(cx, &[LiveId::from_str(id)])
                    .set_disabled(cx, enabled == 0);
            }
        }
        self.nonce = frame["nonce"].as_str().ok_or("missing nonce")?.into();
        self.frame = frame;
        self.actions.clear();
        self.pending_layout = true;
        self.list_drag = None;
        self.suppress_activation = true;
        self.view.redraw(cx);
        log!(
            "mail: mounted AppCard native frame ({} elements)",
            self.elements.len()
        );
        Ok(())
    }

    fn shutdown(&mut self, cx: &mut Cx) {
        if let Some(device) = self.device.take() {
            device.shutdown();
        }
        cx.stop_timer(self.timer);
        if let Some(id) = self.pending_request.take() {
            cx.cancel_http_request(id);
        }
        for (_, child) in &self.view.children {
            retire(cx, child);
        }
    }
}

impl Widget for MailView {
    fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
        let result = self.view.draw_walk(cx, scope, walk);
        let rect = self.view.area().rect(cx);
        let size = rect.size;
        self.origin = rect.pos;
        if size.x > 100. && size.y > 100. {
            self.viewport = size;
        }
        result
    }

    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        if !self.started {
            self.started = true;
            let local = self.endpoint.is_empty();
            self.timer = cx.start_interval(if local { 0.12 } else { 0.35 });
            if local {
                match device::DeviceRuntime::start(cx) {
                    Ok(device) => self.device = Some(device),
                    Err(error) => log!("mail: {error}"),
                }
            }
        }
        // Row buttons own taps. A vertical touch drag scrolls the surrounding
        // list and cancels their activation, even when it started on a row.
        let mut drag_scroll = None;
        // A pointer press on a desktop counts like a touch start: it ends the
        // post-mount suppression, otherwise mouse taps never activate anything.
        if let Event::MouseDown(_) = event {
            self.suppress_activation = false;
            self.list_drag = None;
        }
        if let Event::TouchUpdate(update) = event {
            // A freshly replaced view has not restored its scroll geometry yet.
            // Starting a drag against that zero origin would reset the list.
            if self.pending_layout {
                return;
            }
            for touch in &update.touches {
                if touch.state == TouchState::Start {
                    self.suppress_activation = false;
                    self.list_drag = None;
                    if let Some(watches) = self.frame["scroll_watch"].as_array() {
                        for watch in watches {
                            let (Some(id), Some(content)) =
                                (watch["id"].as_str(), watch["content"].as_str())
                            else {
                                continue;
                            };
                            let viewport = self.view.widget(cx, &[LiveId::from_str(id)]).area();
                            let content = self.view.widget(cx, &[LiveId::from_str(content)]).area();
                            let rect = viewport.clipped_rect(cx);
                            if rect.contains(touch.abs)
                                && touch.abs.x < rect.pos.x + rect.size.x - 14.
                            {
                                self.list_drag = Some((
                                    touch.uid,
                                    touch.abs.y,
                                    (viewport.rect(cx).pos.y - content.rect(cx).pos.y).max(0.),
                                    id.to_owned(),
                                ));
                            }
                        }
                    }
                } else if let Some((uid, start, scroll, id)) = &self.list_drag {
                    if *uid == touch.uid {
                        let delta = touch.abs.y - start;
                        if delta.abs() > 6. {
                            self.suppress_activation = true;
                        }
                        if self.suppress_activation {
                            drag_scroll = Some((id.clone(), (scroll - delta).max(0.)));
                        }
                    }
                }
                if touch.state == TouchState::Stop {
                    self.list_drag = None;
                }
            }
        }
        self.view.handle_event(cx, event, scope);
        if let Some((id, y)) = drag_scroll {
            self.view
                .widget(cx, &[LiveId::from_str(&id)])
                .set_scroll_pos(cx, dvec2(0., y));
        }
        if let Event::Actions(actions) = event {
            for action in actions {
                let Some(action) = action.downcast_ref::<WidgetAction>() else {
                    continue;
                };
                let kit = action.cast::<octoscript_widgets::kit::KitAction>();
                if std::env::var("MAIL_TRACE").is_ok() {
                    log!("mail: widget action {:?} {:?} suppressed={} pending_request={}", action.widget_uid, kit, self.suppress_activation, self.pending_request.is_some());
                }
                let kind = match kit {
                    octoscript_widgets::kit::KitAction::Activated if !self.suppress_activation => {
                        json!({"kind":"activated"})
                    }
                    octoscript_widgets::kit::KitAction::Changed(value) => {
                        json!({"kind":"changed","value":value})
                    }
                    _ => continue,
                };
                let id = self
                    .elements
                    .iter()
                    .filter_map(|e| e["id"].as_str())
                    .find(|id| {
                        self.view.widget(cx, &[LiveId::from_str(id)]).widget_uid()
                            == action.widget_uid
                    });
                if let Some(id) = id {
                    if self.actions.len() < 256 {
                        self.sequence += 1;
                        self.actions
                            .push(json!({"id":id,"action":kind,"sequence":self.sequence}));
                    }
                }
            }
        }
        if let Event::NetworkResponses(responses) = event {
            for response in responses {
                match response {
                    NetworkResponse::HttpResponse {
                        request_id,
                        response,
                    } if Some(*request_id) == self.pending_request => {
                        self.pending_request = None;
                        let body = response.get_string_body().unwrap_or_default();
                        match serde_json::from_str::<Value>(&body) {
                            Ok(mut reply) if response.status_code == 200 => {
                                let ack = reply["ack"].as_u64().unwrap_or(0);
                                if std::env::var("MAIL_TRACE").is_ok() && (ack > 0 || !reply["frame"].is_null()) {
                                    log!("mail: reply ack={ack} frame={}", !reply["frame"].is_null());
                                }
                                self.actions
                                    .retain(|a| a["sequence"].as_u64().unwrap_or(0) > ack);
                                if !reply["frame"].is_null() {
                                    if let Err(error) = self.mount(cx, reply["frame"].take()) {
                                        log!("mail: cannot mount companion frame: {error}");
                                    }
                                }
                            }
                            _ => log!("mail: companion response unavailable"),
                        }
                    }
                    NetworkResponse::HttpError { request_id, .. }
                        if Some(*request_id) == self.pending_request =>
                    {
                        self.pending_request = None;
                        log!("mail: companion connection unavailable");
                    }
                    _ => {}
                }
            }
        }
        if self.timer.is_event(event).is_some() {
            if self.endpoint.is_empty() {
                if let Some(result) = self.device.as_ref().and_then(|device| device.endpoint()) {
                    match result {
                        Ok(endpoint) => self.endpoint = endpoint,
                        Err(error) => log!("mail: {error}"),
                    }
                }
            }
            if self.pending_layout {
                let ready = self.elements.iter().filter(|e| e["focused"] == 1).all(|e| {
                    e["id"]
                        .as_str()
                        .map(|id| {
                            self.view
                                .widget(cx, &[LiveId::from_str(id)])
                                .area()
                                .is_valid(cx)
                        })
                        .unwrap_or(false)
                });
                if ready {
                    for e in &self.elements {
                        if e["focused"] == 1 {
                            if let Some(id) = e["id"].as_str() {
                                let widget = self.view.widget(cx, &[LiveId::from_str(id)]);
                                if let Some(mut input) = widget.borrow_mut::<TextInput>() {
                                    input.set_key_focus(cx);
                                    if let Some(selection) = self.pending_selection.take() {
                                        input.set_selection(cx, selection);
                                    } else {
                                        input.move_cursor_text_end(cx, false);
                                    }
                                    input.reset_blink_timer(cx);
                                };
                            }
                        }
                    }
                    let mut restored = true;
                    if let Some(items) = self.frame["scroll_restore"].as_array() {
                        for item in items {
                            if let (Some(id), Some(y)) = (item["id"].as_str(), item["y"].as_f64()) {
                                let content = self.frame["scroll_watch"]
                                    .as_array()
                                    .and_then(|watches| {
                                        watches.iter().find(|watch| watch["id"] == id)
                                    })
                                    .and_then(|watch| watch["content"].as_str());
                                if let Some(content) = content {
                                    let viewport =
                                        self.view.widget(cx, &[LiveId::from_str(id)]).area();
                                    let content =
                                        self.view.widget(cx, &[LiveId::from_str(content)]).area();
                                    restored &= viewport.is_valid(cx)
                                        && content.is_valid(cx)
                                        && ((viewport.rect(cx).pos.y - content.rect(cx).pos.y)
                                            .max(0.)
                                            - y * self.scale)
                                            .abs()
                                            < 1.;
                                }
                                self.view
                                    .widget(cx, &[LiveId::from_str(id)])
                                    .set_scroll_pos(cx, dvec2(0., y * self.scale));
                            }
                        }
                    }
                    self.pending_layout = !restored;
                    self.view.redraw(cx);
                    // Scroll restoration changes geometry on the next draw.
                    // Reporting the old rectangles now would send y=0 back to
                    // the companion and reset its virtualized row window.
                    return;
                }
            }
            self.exchange(cx);
        }
    }
}

pub struct MailModule;
pub static MAIL_MODULE: MailModule = MailModule;
impl AppModule for MailModule {
    fn id(&self) -> &'static str {
        "mail"
    }
    fn label(&self) -> &'static str {
        "Mail"
    }
    fn capabilities(&self) -> &'static [&'static str] {
        &["net"]
    }
    fn open_schema(&self) -> OpenSchema {
        OpenSchema::new(1).arg("endpoint", OpenArgKind::Text, false)
    }
    fn register(&self, vm: &mut ScriptVm) {
        octoscript_widgets::design::script_mod(vm);
        octoscript_widgets::kit::script_mod(vm);
        viewer::script_mod(vm);
        script_mod(vm);
    }
    fn create(
        &self,
        vm: &mut ScriptVm,
        open: ValidatedOpen,
        handles: InstanceHandles,
    ) -> InstanceParts {
        let value = script_eval!(vm, { use mod.widgets.* MailView {} });
        let root = WidgetRef::script_from_value(vm, value);
        if let Some(mut mail) = root.borrow_mut::<MailView>() {
            // An explicit loopback endpoint retains companion compatibility.
            // Without one, Mail starts its own on-device controller and services.
            mail.endpoint = open
                .text("endpoint")
                .filter(|url| url.starts_with("http://127.0.0.1:"))
                .unwrap_or_default()
                .trim_end_matches('/')
                .into();
            mail.viewport = handles.viewport.size;
        }
        let cleanup = root.clone();
        InstanceParts {
            root,
            executor: Box::new(MailExecutor),
            shutdown: Box::new(move |vm| {
                if let Some(mut mail) = cleanup.borrow_mut::<MailView>() {
                    mail.shutdown(vm.cx_mut());
                }
            }),
        }
    }
}
struct MailExecutor;
impl ServiceExecutor for MailExecutor {
    fn manifest(&self) -> ServiceManifest {
        ServiceManifest::new("mail", "Mail", "Native Mail AppCard preview.")
    }
    fn execute(&mut self, _cx: &mut Cx, call: &ServiceCall) -> ExecOutcome {
        ExecOutcome::Done(ToolResult::unavailable(
            &call.call_id,
            "Use the Mail interface",
        ))
    }
}

mod viewer {
    //! The message reader: Makepad's own HTML widget instead of a platform
    //! WebView. Images stay out of the document until the reader asks for them.
    use super::*;
    use base64::{engine::general_purpose::STANDARD, Engine as _};
    script_mod! {
        use mod.prelude.widgets.*
        mod.widgets.MailHtml = set_type_default() do #(MailHtml::register_widget(vm)) {
            width: Fill height: Fill flow: Down
            show_bg: true draw_bg.color: #fff
            bar := View {
                width: Fill height: Fit flow: Right align: Align{x: 0.0, y: 0.5} spacing: 10
                padding: Inset{left: 22, right: 16, top: 6, bottom: 6}
                note := Label { width: Fill height: Fit text: "" draw_text.color: #8e8e93 }
                load := Button { text: "Load images" }
            }
            scroll := ScrollYView {
                width: Fill height: Fill flow: Down
                padding: Inset{left: 10, right: 10, top: 0, bottom: 28}
                content := Html { width: Fill height: Fit body: "" }
                images := View {
                    width: Fill height: Fit flow: Down spacing: 10 padding: Inset{left: 12, right: 12, top: 8, bottom: 0}
                    img0 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img1 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img2 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img3 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img4 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img5 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img6 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                    img7 := Image { width: Fill height: Fit fit: ImageFit.Horizontal visible: false }
                }
            }
        }
        mod.prelude.widgets.MailHtml = mod.widgets.MailHtml
    }
    pub const SLOTS: usize = 8;

    #[derive(Script, ScriptHook, Widget)]
    pub struct MailHtml {
        #[deref]
        view: View,
        /// The scene's data URL (`data:text/html;charset=utf-8;base64,…`).
        #[live]
        url: String,
        #[rust]
        shown_url: String,
        #[rust]
        images: Vec<String>,
        #[rust]
        loaded: bool,
    }

    /// Split the document into markup without `<img>` tags and the image sources it named.
    pub fn split_images(html: &str) -> (String, Vec<String>) {
        let mut out = String::with_capacity(html.len());
        let mut images = Vec::new();
        let mut rest = html;
        while let Some(start) = rest.find("<img") {
            out.push_str(&rest[..start]);
            let tag_end = rest[start..].find('>').map(|i| start + i + 1).unwrap_or(rest.len());
            let tag = &rest[start..tag_end];
            // Tracking pixels and layout spacers are not pictures.
            let tiny = ["width", "height"].iter().any(|k| attribute(tag, k).and_then(|v| v.trim_end_matches("px").parse::<f64>().ok()).map(|v| v <= 2.0).unwrap_or(false));
            if let Some(src) = attribute(tag, "src").filter(|_| !tiny) {
                images.push(src);
                out.push_str(&format!("<i>[image {}]</i>", images.len()));
            }
            rest = &rest[tag_end..];
        }
        out.push_str(rest);
        (out, images)
    }
    fn attribute(tag: &str, name: &str) -> Option<String> {
        let key = format!(" {name}=\"");
        let start = tag.find(&key)? + key.len();
        let end = tag[start..].find('"')? + start;
        let value = tag[start..end].replace("&amp;", "&").replace("&quot;", "\"").replace("&lt;", "<").replace("&gt;", ">");
        (!value.is_empty()).then_some(value)
    }

    impl MailHtml {
        fn apply(&mut self, cx: &mut Cx) {
            self.shown_url = self.url.clone();
            let encoded = self.url.strip_prefix("data:text/html;charset=utf-8;base64,").unwrap_or("");
            let html = STANDARD.decode(encoded).ok().and_then(|bytes| String::from_utf8(bytes).ok()).unwrap_or_default();
            let (markup, images) = split_images(&html);
            self.view.widget(cx, ids!(scroll.content)).set_text(cx, &markup);
            self.images = images;
            self.loaded = false;
            for i in 0..SLOTS {
                self.slot(cx, i).set_visible(cx, false);
            }
            self.refresh_bar(cx);
            self.view.redraw(cx);
        }
        fn slot(&self, cx: &mut Cx, i: usize) -> WidgetRef {
            self.view.widget(cx, &[live_id!(scroll), live_id!(images), LiveId::from_str(&format!("img{i}"))])
        }
        fn refresh_bar(&mut self, cx: &mut Cx) {
            let n = self.images.len();
            let note = if n == 0 { String::new() } else if self.loaded {
                if n > SLOTS { format!("{} of {n} images shown", SLOTS) } else { format!("{n} image{}", if n == 1 { "" } else { "s" }) }
            } else {
                format!("{n} image{} not loaded", if n == 1 { "" } else { "s" })
            };
            self.view.widget(cx, ids!(bar.note)).set_text(cx, &note);
            self.view.widget(cx, ids!(bar.load)).set_visible(cx, n > 0 && !self.loaded);
            self.view.widget(cx, ids!(bar)).set_visible(cx, n > 0);
        }
        fn load_images(&mut self, cx: &mut Cx) {
            self.loaded = true;
            for (i, src) in self.images.clone().iter().take(SLOTS).enumerate() {
                let slot = self.slot(cx, i);
                slot.set_visible(cx, true);
                if std::env::var("MAIL_TRACE").is_ok() { log!("mail: image {i}: {}", &src[..src.len().min(100)]); }
                let Some(mut image) = slot.borrow_mut::<Image>() else { continue };
                let inline = src.strip_prefix("data:image/").and_then(|rest| rest.split_once(',')).map(|(_, payload)| STANDARD.decode(payload));
                let result = match inline {
                    Some(Ok(bytes)) => image.load_image_from_data_async(cx, std::path::Path::new(&format!("mail-inline-{i}")), std::sync::Arc::new(bytes)),
                    Some(Err(error)) => { log!("mail: inline image {i} is not valid base64: {error}"); slot.set_visible(cx, false); continue; }
                    None => image.load_image_http_by_url_async(cx, src),
                };
                if let Err(error) = result {
                    log!("mail: image {i} not loaded: {error:?}");
                    slot.set_visible(cx, false);
                }
            }
            self.refresh_bar(cx);
            self.view.redraw(cx);
        }
    }

    impl Widget for MailHtml {
        fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
            self.view.handle_event(cx, event, scope);
            if let Event::Actions(actions) = event {
                if self.view.button(cx, ids!(bar.load)).clicked(actions) && !self.loaded {
                    self.load_images(cx);
                }
            }
        }
        fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
            if self.shown_url != self.url {
                self.apply(cx);
            }
            self.view.draw_walk(cx, scope, walk)
        }
    }
}

//! Native AppCard Mail module. The USB companion owns the existing Python mail service.
use makepad_app_module::{
    makepad_ai_services::wire::{ServiceCall, ServiceManifest, ToolResult},
    AppModule, ExecOutcome, InstanceHandles, InstanceParts, OpenArgKind, OpenSchema,
    ServiceExecutor, ValidatedOpen,
};
pub use makepad_widgets;
use makepad_widgets::browser::BrowserBackend;
use makepad_widgets::makepad_platform::event::TouchState;
use makepad_widgets::*;
use serde_json::{json, Value};
mod device;
mod network;
mod scenes;

script_mod! {
    use mod.prelude.widgets.*
    mod.prelude.widgets.Browser = mod.widgets.Browser
    mod.prelude.widgets.BrowserBackend = mod.widgets.BrowserBackend
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
    #[rust(true)]
    foreground: bool,
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
    if let Some(mut web) = widget.borrow_mut::<MailWebView>() {
        web.close(cx);
    }
    if widget
        .borrow::<makepad_widgets::browser::Browser>()
        .is_some()
    {
        cx.system_browser(LiveId(widget.widget_uid().0)).close();
    }
    octoscript_widgets::kit::retire_overlay(cx, widget);
    let mut children = Vec::new();
    widget.children(&mut |_, child| children.push(child));
    for child in children {
        retire(cx, &child);
    }
}

impl MailView {
    /// Native layers follow the launcher's foreground app, including Home/Recents.
    pub fn set_foreground(&mut self, cx: &mut Cx, foreground: bool) {
        if self.foreground == foreground {
            return;
        }
        self.foreground = foreground;
        fn visit(cx: &mut Cx, widget: &WidgetRef, foreground: bool) {
            if let Some(mut web) = widget.borrow_mut::<MailWebView>() {
                web.presented = foreground;
                if !foreground {
                    web.close(cx);
                }
            }
            let mut children = Vec::new();
            widget.children(&mut |_, child| children.push(child));
            for child in children {
                visit(cx, &child, foreground);
            }
        }
        for (_, child) in &self.view.children {
            visit(cx, child, foreground);
        }
    }

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
        #[cfg(target_os = "android")]
        let ui = ui.replace("Browser {", "MailWebView {");
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
                .ok_or_else(|| "Mail widget tree rejected".to_owned())
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
        self.foreground = !self.foreground;
        self.set_foreground(cx, !self.foreground);
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
            if !self.pending_layout {
                self.suppress_activation = false;
                self.list_drag = None;
            }
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
                let kind = match action.cast::<octoscript_widgets::kit::KitAction>() {
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
        makepad_widgets::browser::script_mod(vm);
        octoscript_widgets::design::script_mod(vm);
        octoscript_widgets::kit::script_mod(vm);
        web_script_mod(vm);
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

mod platform_web {
    use super::*;
    script_mod! {
        use mod.prelude.widgets.*
        mod.widgets.MailWebView = set_type_default() do #(MailWebView::register_widget(vm)) {
            width: Fill height: Fill flow: Overlay
            show_bg: true draw_bg.color: #fff
        }
        mod.prelude.widgets.MailWebView = mod.widgets.MailWebView
    }
}
use platform_web::script_mod as web_script_mod;

#[derive(Script, ScriptHook, Widget)]
struct MailWebView {
    #[deref]
    view: View,
    #[live]
    url: String,
    #[live]
    backend: BrowserBackend,
    #[rust]
    spawned: bool,
    #[rust(true)]
    presented: bool,
}
impl MailWebView {
    fn close(&mut self, cx: &mut Cx) {
        if self.spawned {
            cx.system_browser(LiveId(self.widget_uid().0)).close();
            self.spawned = false;
        }
    }
}
impl Widget for MailWebView {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        self.view.handle_event(cx, event, scope);
        if matches!(event, Event::Shutdown | Event::HomeIntent) {
            self.close(cx);
        }
    }
    fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
        let step = self.view.draw_walk(cx, scope, walk);
        if self.presented {
            let id = LiveId(self.widget_uid().0);
            if !self.spawned {
                cx.system_browser(id).spawn(&self.url);
                self.spawned = true;
                log!("mail: Android platform WebView opened");
            }
            cx.system_browser(id).update(self.view.area(), true);
        }
        step
    }
}

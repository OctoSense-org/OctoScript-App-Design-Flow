//! Finance AppModule: the same image-derived L0 scenes on desktop and mobile.
pub use makepad_widgets;
mod plot;
use makepad_widgets::browser::BrowserBackend;
use makepad_widgets::matplot::stock_plot::StockPlot;
use makepad_widgets::*;
use octosense_finance_service::providers::Keys;
use octosense_finance_service::{
    frame,
    model::{Preferences, State},
    providers, scenes,
};
use serde_json::{json, Value};
use std::{
    collections::{HashMap, VecDeque},
    path::PathBuf,
    rc::Rc,
    time::Instant,
};

script_mod! {
 use mod.prelude.widgets.*
 mod.widgets.FinanceView = set_type_default() do #(FinanceView::register_widget(vm)) {
  width:Fill height:Fill flow:Overlay show_bg:true draw_bg.color:#07090c
  host := Splash {width:Fill height:Fill}
 }
 mod.prelude.widgets.BrowserBackend = mod.widgets.BrowserBackend
 mod.widgets.FinanceWebView = set_type_default() do #(FinanceWebView::register_widget(vm)) {width:Fill height:Fill flow:Overlay}
 mod.prelude.widgets.FinanceWebView = mod.widgets.FinanceWebView
}
#[derive(Script, ScriptHook, Widget)]
pub struct FinanceView {
    #[deref]
    view: View,
    #[rust]
    state: State,
    #[rust]
    card_kind: String,
    #[rust]
    keys: Keys,
    #[rust]
    timer: Timer,
    #[rust]
    started: bool,
    #[rust]
    dirty: bool,
    #[rust]
    retired: Option<View>,
    #[rust]
    elements: Vec<Value>,
    #[rust]
    mapping: HashMap<String, String>,
    #[rust]
    actions: HashMap<String, Value>,
    #[rust]
    viewport: DVec2,
    #[rust]
    origin: DVec2,
    #[rust]
    scale: f64,
    #[rust]
    current_screen: String,
    #[rust]
    scrolls: HashMap<String, f64>,
    #[rust]
    restore: Option<f64>,
    #[rust]
    persist: Option<PathBuf>,
    #[rust]
    queue: VecDeque<providers::Request>,
    #[rust]
    pending: Option<(LiveId, providers::Request, Instant)>,
    #[rust]
    last_request: Option<Instant>,
    #[rust]
    sequence: u64,
    #[rust(true)]
    foreground: bool,
    #[rust]
    chart_drag: bool,
    #[rust]
    reset_scroll: bool,
    #[rust]
    list_drag: Option<(u64, f64, f64)>,
    #[rust]
    suppress_activation: bool,
    #[rust]
    input_selection: Option<makepad_draw::text::selection::Selection>,
    #[rust]
    input_id: String,
    #[rust]
    chart_bindings: HashMap<String, (String, String)>,
    #[rust]
    stock_responses: HashMap<String, Rc<Vec<u8>>>,
}
fn close_web(cx: &mut Cx, w: &WidgetRef) {
    if let Some(mut web) = w.borrow_mut::<FinanceWebView>() {
        web.presented = false;
        web.close(cx);
    }
    octoscript_widgets::kit::retire_overlay(cx, w);
    let mut children = vec![];
    w.children(&mut |_, w| children.push(w));
    for w in children {
        close_web(cx, &w);
    }
}
impl FinanceView {
    pub fn set_foreground(&mut self, cx: &mut Cx, on: bool) {
        if self.foreground == on {
            return;
        }
        self.foreground = on;
        if !on {
            self.cancel(cx);
            for (_, w) in &self.view.children {
                close_web(cx, w);
            }
        } else {
            self.dirty = true;
            self.view.redraw(cx);
        }
    }
    fn cancel(&mut self, cx: &mut Cx) {
        if let Some((id, _, _)) = self.pending.take() {
            cx.cancel_http_request(id);
        }
        self.queue.clear();
        self.state.busy.clear();
    }
    fn begin(&mut self, cx: &mut Cx) {
        self.started = true;
        self.timer = cx.start_interval(0.08);
        let base = cx
            .os_type()
            .get_data_dir()
            .map(PathBuf::from)
            .or_else(|| {
                std::env::var_os("HOME")
                    .map(|p| PathBuf::from(p).join("Library/Application Support/OctoSense"))
            })
            .unwrap_or_else(std::env::temp_dir);
        let selected = self.state.selected.clone();
        let screen = self.state.screen.clone();
        self.state = State::new(Preferences {
            preview: false,
            ..Preferences::default()
        });
        self.state.selected = selected;
        self.state.screen = screen;
        let dir = std::env::var_os("OCTOS_FINANCE_DATA_DIR")
            .map(PathBuf::from)
            .unwrap_or(base.join("finance"));
        if std::fs::create_dir_all(&dir).is_ok() {
            self.persist = Some(dir.join("preferences.json"));
            if let Ok(bytes) = std::fs::read(dir.join("preferences.json")) {
                if let Ok(p) = serde_json::from_slice::<Preferences>(&bytes) {
                    let selected = self.state.selected.clone();
                    let screen = self.state.screen.clone();
                    self.state = State::new(p);
                    self.state.selected = selected;
                    self.state.screen = screen;
                }
            }
        }
        if let Ok(value) = std::env::var("OCTOS_FINANCE_PREVIEW") {
            let preview = value == "1";
            if preview != self.state.prefs.preview {
                self.state.act("preview", &json!({}));
            }
        }
        if !self.state.prefs.preview {
            if let Some(p) = &self.persist {
                if let Ok(bytes) = std::fs::read(p.with_file_name("cache.json")) {
                    if let Ok(v) = serde_json::from_slice::<Value>(&bytes) {
                        self.state.quotes =
                            serde_json::from_value(v["quotes"].clone()).unwrap_or_default();
                        self.state.history =
                            serde_json::from_value(v["history"].clone()).unwrap_or_default();
                        self.state.news =
                            serde_json::from_value(v["news"].clone()).unwrap_or_default();
                        self.state.errors.insert(
                            "quotes".into(),
                            "Cached data · refresh to verify freshness.".into(),
                        );
                    }
                }
            }
        }
        self.dirty = true;
    }
    fn cache(&mut self) {
        if self.state.prefs.preview {
            return;
        }
        if let Some(p) = &self.persist {
            let path = p.with_file_name("cache.json");
            let temp = path.with_extension("tmp");
            let data = json!({"quotes":self.state.quotes,"history":self.state.history,"news":self.state.news});
            if std::fs::write(&temp, data.to_string()).is_ok() {
                let _ = std::fs::rename(temp, path);
            }
        }
    }
    fn save(&mut self) {
        if let Some(p) = &self.persist {
            let result = (|| -> Result<(), Box<dyn std::error::Error>> {
                let temp = p.with_extension("tmp");
                std::fs::write(&temp, serde_json::to_vec(&self.state.prefs)?)?;
                std::fs::rename(temp, p)?;
                Ok(())
            })();
            if result.is_err() {
                self.state
                    .errors
                    .insert("storage".into(), "Preferences could not be saved.".into());
            }
        }
    }
    fn id(&self, id: &str) -> Option<LiveId> {
        self.mapping.get(id).map(|id| LiveId::from_str(id))
    }
    fn scroll(&self, cx: &Cx) -> f64 {
        let Some(v) = self.id("body_scroll") else {
            return 0.;
        };
        let Some(c) = self.id("body_content") else {
            return 0.;
        };
        let v = self.view.child_by_path(&[v]).area();
        let c = self.view.child_by_path(&[c]).area();
        if v.is_valid(cx) && c.is_valid(cx) {
            (v.rect(cx).pos.y - c.rect(cx).pos.y).max(0.) / self.scale.max(0.1)
        } else {
            0.
        }
    }
    fn mount(&mut self, cx: &mut Cx) -> Result<(), String> {
        if self.viewport.x < 100. {
            return Ok(());
        }
        let old_scroll = if self.reset_scroll {
            0.
        } else {
            self.scroll(cx)
        };
        self.reset_scroll = false;
        if !self.current_screen.is_empty() {
            self.scrolls.insert(self.current_screen.clone(), old_scroll);
        }
        self.input_selection = None;
        self.input_id.clear();
        for (source, native) in &self.mapping {
            if !source.ends_with("_input") {
                continue;
            }
            let w = self.view.widget(cx, &[LiveId::from_str(native)]);
            if let Some(input) = w.borrow::<TextInput>() {
                if cx.has_key_focus(input.area()) {
                    self.input_id = source.clone();
                    self.input_selection = Some(input.selection());
                }
            };
        }
        let mut scene = if self.card_kind.is_empty() {
            scenes::build(&self.state)
        } else {
            octosense_finance_service::cards::scene(&self.state, &self.card_kind)?
        };
        if self.card_kind.is_empty() {
            scene.fit_height(self.viewport.y * 406. / self.viewport.x);
        }
        let frame = frame::compile(&scene.tree, &scene.controls);
        let report = octoscript_ui_l0::realize(
            frame.value["card"].as_str().unwrap(),
            &frame.value["data"],
            Default::default(),
        );
        let source = octoscript_ui_l0::kit_pack::lower(
            report.complete_root()?,
            &frame.value["pack"],
            &frame.value["data"],
        )?;
        let mut tree = octoscript_makepad::design::prepare(&source)?;
        self.elements = octoscript_makepad::l0::inspectable(&mut tree);
        self.scale = (self.viewport.x / scene.tree["w"].as_f64().unwrap_or(406.))
            .min(self.viewport.y / scene.tree["h"].as_f64().unwrap_or(776.));
        let origin = self.origin;
        let scale = self.scale;
        fn fit(n: &mut octoscript_node::UiNode, scale: f64, origin: DVec2) {
            let a = &mut n.attrs;
            if let Some(v) = &mut a.x {
                *v = *v * scale + origin.x;
            }
            if let Some(v) = &mut a.y {
                *v = *v * scale + origin.y;
            }
            for v in [
                &mut a.w,
                &mut a.h,
                &mut a.size,
                &mut a.line_height,
                &mut a.radius,
            ] {
                if let Some(v) = v {
                    *v *= scale as f32;
                }
            }
            for c in &mut n.children {
                fit(c, scale, origin);
            }
        }
        fit(&mut tree, scale, origin);
        let mut ui = octoscript_makepad::design::to_makepad_ui(&tree)?;
        ui = ui.replace("Browser {", "FinanceWebView {");
        ui = ui
            .replace("mod.plot.LinePlot {", "mod.widgets.StockPlot {")
            .replace("demo_data: false clip_plot: false ", "")
            .replace(" data_padding: 0 show_points: false", "")
            .replace("draw_vector.draw_depth: 0", "draw_vector.draw_depth: 2");
        ui = ui.replace("symbols := FontMember", "cjk := FontMember{res: crate_resource(\"self:resources/ux/NotoSansSC-Regular.ttf\") asc: 0 desc: 0 weight: 400 lazy: 1} symbols := FontMember");
        let sm=ScriptMod{cargo_manifest_path:env!("CARGO_MANIFEST_DIR").into(),module_path:module_path!().into(),file:file!().into(),line:1,column:0,values:vec![],code:format!("use mod.prelude.widgets.*\nreturn View {{ width:Fill height:Fill flow:Overlay {ui} }}")};
        let v = cx.with_vm(|vm| {
            vm.eval_checked(sm, 2_000_000)
                .map(|v| View::script_from_value(vm, v))
                .ok_or_else(|| "Finance widget tree rejected".to_owned())
        })?;
        let host = self.view.widget(cx, ids!(host));
        let mut host = host.borrow_mut::<Splash>().ok_or("Finance host missing")?;
        self.retired = Some(std::mem::replace(&mut host.view, v));
        if let Some(old) = &self.retired {
            for (_, w) in &old.children {
                close_web(cx, w);
            }
        }
        let uid = host.widget_uid();
        let mut children = vec![];
        host.children(&mut |id, w| children.push((id, w)));
        drop(host);
        for (id, w) in children {
            cx.widget_tree_insert_child_deep(uid, id, w);
        }
        cx.widget_tree_mark_dirty(uid);
        self.mapping = frame.mapping;
        self.actions = frame.actions;
        self.chart_bindings.clear();
        for (name, binding) in scene.plots.as_object().unwrap() {
            let id = self
                .id(name)
                .ok_or_else(|| format!("Missing stock chart {name}"))?;
            let w = self.view.widget(cx, &[id]);
            let mut chart = w
                .borrow_mut::<StockPlot>()
                .ok_or_else(|| format!("Chart {name} is not a StockPlot"))?;
            plot::configure(
                &mut chart,
                cx,
                binding,
                &self.state,
                name == "price_chart",
                self.automatic_stocks(),
            );
            self.chart_bindings.insert(
                name.clone(),
                (
                    binding["security"].as_str().unwrap_or_default().into(),
                    binding["range"].as_str().unwrap_or("1D").into(),
                ),
            );
        }
        if let Some(id) = self.id("article_web") {
            let w = self.view.widget(cx, &[id]);
            if let Some(mut web) = w.borrow_mut::<FinanceWebView>() {
                if let Some(url) = scene.web_url {
                    web.url = url;
                }
            };
        }
        self.restore = Some(*self.scrolls.get(&self.state.screen).unwrap_or(&0.));
        self.current_screen = self.state.screen.clone();
        self.dirty = false;
        self.view.redraw(cx);
        self.evidence();
        Ok(())
    }
    fn update_detail(&mut self, cx: &mut Cx, bind_chart: bool) {
        let scene = scenes::build(&self.state);
        fn labels(view: &View, cx: &mut Cx, mapping: &HashMap<String, String>, n: &Value) {
            if n["t"] == "text" {
                if let (Some(id), Some(text)) = (
                    n["id"].as_str().and_then(|id| mapping.get(id)),
                    n["text"].as_str(),
                ) {
                    let widget = view.widget(cx, &[LiveId::from_str(id)]);
                    widget.set_text(cx, text);
                    if let Some(c) = n["color"].as_u64() {
                        if let Some(mut label) = widget.borrow_mut::<Label>() {
                            label.set_text_color(
                                cx,
                                vec4(
                                    ((c >> 16) & 255) as f32 / 255.,
                                    ((c >> 8) & 255) as f32 / 255.,
                                    (c & 255) as f32 / 255.,
                                    1.,
                                ),
                            );
                        };
                    }
                }
            }
            for c in n["c"].as_array().into_iter().flatten() {
                labels(view, cx, mapping, c);
            }
        }
        labels(&self.view, cx, &self.mapping, &scene.tree);
        for (i, range) in ["1D", "1W", "1M", "6M", "1Y"].iter().enumerate() {
            if let Some(id) = self.id(&format!("range_{i}_bg")) {
                let mut widget = self.view.widget(cx, &[id]);
                let color = if self.state.range == *range {
                    vec4(0.039, 0.518, 1., 1.)
                } else if !self.state.prefs.light {
                    vec4(0.078, 0.094, 0.122, 1.)
                } else {
                    vec4(0.94, 0.95, 0.96, 1.)
                };
                script_apply_eval!(cx,widget,{draw_bg +: {color:#(color)}});
            }
        }
        if bind_chart {
            if let Some(id) = self.id("price_chart") {
                let w = self.view.widget(cx, &[id]);
                if let Some(mut chart) = w.borrow_mut::<StockPlot>() {
                    plot::configure(
                        &mut chart,
                        cx,
                        &scene.plots["price_chart"],
                        &self.state,
                        true,
                        self.automatic_stocks(),
                    );
                };
                self.chart_bindings.insert(
                    "price_chart".into(),
                    (self.state.selected.clone(), self.state.range.clone()),
                );
            }
        }
        self.view.redraw(cx);
        self.evidence();
    }
    fn evidence(&self) {
        if let Some(dir) = std::env::var_os("OCTOS_FINANCE_EVIDENCE_DIR") {
            let dir = PathBuf::from(dir);
            let _ = std::fs::create_dir_all(&dir);
            let mut v = self.state.evidence();
            v["mapping"] = json!(self.mapping);
            if let Some(id) = self.id("price_chart") {
                let widget = self.view.child_by_path(&[id]);
                v["chart_widget_uid"] = json!(widget.widget_uid().0);
                if let Some(plot) = widget.borrow::<StockPlot>() {
                    let r = plot.plot_rect();
                    v["chart_data_rect"] = json!([r.pos.x, r.pos.y, r.size.x, r.size.y]);
                    v["chart_engine"] = json!("makepad_widgets::matplot::stock_plot::StockPlot");
                    v["chart_binding"] = json!({"symbol":plot.symbol,"range":plot.range,"automatic":self.automatic_stocks()});
                    v["quote"] = json!(self.state.quotes.get(&self.state.selected));
                };
            }
            let _ = std::fs::write(dir.join("state.json"), v.to_string());
        }
    }
    fn automatic_stocks(&self) -> bool {
        !self.state.prefs.preview && self.keys.alltick.is_empty()
    }

    fn stock_jobs(&self) -> Vec<(String, String, String)> {
        let mut bindings: Vec<_> = self.chart_bindings.values().cloned().collect();
        // Daily quote statistics always come from the daily response, even
        // while the chart shows a longer range.
        bindings.extend(
            self.chart_bindings
                .values()
                .map(|(id, _)| (id.clone(), "1D".into())),
        );
        bindings.sort();
        bindings.dedup();
        bindings
            .into_iter()
            .filter_map(|(id, range)| {
                let symbol = self
                    .state
                    .catalog
                    .iter()
                    .find(|s| s.id == id)?
                    .yahoo_symbol()?;
                let url = StockPlot::chart_url(&symbol, &range);
                Some((id, range, url))
            })
            .collect()
    }

    fn sync_stock_data(&mut self, cx: &mut Cx) {
        if !self.automatic_stocks() {
            return;
        }
        let mut changed = false;
        for (security, range, url) in self.stock_jobs() {
            let key = format!("market:{security}:{range}");
            if let Some(bytes) = cx.script_data_fetch(&url) {
                if self
                    .stock_responses
                    .get(&url)
                    .is_some_and(|previous| Rc::ptr_eq(previous, &bytes))
                {
                    continue;
                }
                match providers::apply_stockplot(&mut self.state, &security, &range, &bytes) {
                    Ok(()) => {
                        self.state.errors.remove(&key);
                        self.state.errors.remove("quotes");
                    }
                    Err(error) => {
                        self.state.errors.insert(key, error);
                    }
                }
                self.stock_responses.insert(url, bytes);
                changed = true;
            } else if cx.script_data.resources.data_fetch_failed_terminally(&url) {
                let message = "Market data unavailable. Refresh to retry.";
                if self.state.errors.get(&key).map(String::as_str) != Some(message) {
                    self.state.errors.insert(key, message.into());
                    changed = true;
                }
            }
        }
        if changed {
            self.cache();
            if self.state.screen == "detail" && !self.dirty {
                self.update_detail(cx, false);
            } else {
                self.dirty = true;
            }
        }
    }

    fn refresh(&mut self, cx: &mut Cx) {
        self.cancel(cx);
        if self.state.prefs.preview {
            self.state.load_preview();
            self.dirty = true;
            return;
        }
        if self.automatic_stocks() {
            use makepad_widgets::makepad_platform::script::res::DataFetch;
            let mut urls: Vec<_> = self.stock_responses.keys().cloned().collect();
            urls.extend(self.stock_jobs().into_iter().map(|(_, _, url)| url));
            urls.sort();
            urls.dedup();
            for url in urls {
                let resources = &cx.script_data.resources;
                if matches!(
                    resources.get_data_fetch(&url),
                    Some(DataFetch::Loaded(_) | DataFetch::Error)
                ) {
                    resources.data_fetches.borrow_mut().remove(&url);
                    resources.data_fetch_retries.borrow_mut().remove(&url);
                }
            }
            self.stock_responses.clear();
        }
        if matches!(
            self.state.screen.as_str(),
            "news" | "company_news" | "settings"
        ) {
            for (kind, key) in [
                ("finnhub", &self.keys.finnhub),
                ("tushare", &self.keys.tushare),
            ] {
                if key.is_empty() {
                    self.state
                        .errors
                        .insert(kind.into(), "API key required in Settings.".into());
                }
            }
        }
        self.queue = providers::requests(&self.state, &self.keys).into();
        for r in &self.queue {
            self.state.busy.insert(r.kind.clone());
        }
        self.dirty = true;
    }
    fn action(&mut self, cx: &mut Cx, event: &str, payload: Value) {
        if event == "credential" {
            let automatic_before = self.automatic_stocks();
            let key = payload["value"].as_str().unwrap_or("");
            let secret = payload["text"].as_str().unwrap_or("").trim();
            match key {
                "alltick" => self.keys.alltick = secret.into(),
                "finnhub" => self.keys.finnhub = secret.into(),
                "tushare" => self.keys.tushare = secret.into(),
                _ => {}
            }
            if automatic_before != self.automatic_stocks() {
                self.state.quotes.clear();
                self.state.history.clear();
                self.stock_responses.clear();
                self.dirty = true;
            }
            return;
        }
        if event == "refresh" {
            self.refresh(cx);
            return;
        }
        if event == "share" {
            if let Some(n) = self
                .state
                .news
                .iter()
                .find(|n| n.id == self.state.article)
                .or_else(|| self.state.prefs.saved.get(&self.state.article))
            {
                if let Some(url) = &n.url {
                    cx.copy_to_clipboard(url);
                } else {
                    cx.copy_to_clipboard(&n.title);
                }
            }
            return;
        }
        if matches!(event, "navigate" | "open") {
            self.card_kind.clear();
        }
        if matches!(event, "navigate" | "region" | "search" | "open") {
            self.state.list_start = 0;
            self.reset_scroll = true;
        }
        if event == "preview" {
            self.cancel(cx);
            self.stock_responses.clear();
        }
        if event == "range" && self.state.screen == "detail" && self.id("price_chart").is_some() {
            self.state.act(event, &payload);
            self.update_detail(cx, true);
            return;
        }
        if self.state.act(event, &payload) {
            self.save();
        }
        self.dirty = true;
        if ["range", "open"].contains(&event)
            && !self.state.prefs.preview
            && !self.automatic_stocks()
        {
            self.refresh(cx);
        }
    }
    fn inspect(&mut self, cx: &mut Cx, abs: DVec2) {
        let Some(id) = self.id("price_chart") else {
            return;
        };
        let w = self.view.widget(cx, &[id]);
        let r = w
            .borrow::<StockPlot>()
            .map(|p| *p.plot_rect())
            .unwrap_or_else(|| w.area().rect(cx));
        let points = self.state.points();
        if points.len() < 2 {
            return;
        }
        let x = ((abs.x - r.pos.x) / r.size.x).clamp(0., 1.);
        // StockPlot places samples at equal intervals, including across
        // exchange closures. Inspection uses that same index coordinate.
        let i = (x * (points.len() - 1) as f64).round() as usize;
        self.state.inspection = Some(i);
        if let Some(mut plot) = w.borrow_mut::<StockPlot>() {
            plot.set_selected_point(cx, Some(i));
        }
        let p = &self.state.points()[i];
        let text = format!(
            "{} · {:.2} {}",
            octosense_finance_service::model::timestamp_text(p.time),
            p.price,
            self.state.security().currency
        );
        if let Some(id) = self.id("inspection") {
            self.view.widget(cx, &[id]).set_text(cx, &text);
        }
        self.evidence();
    }
}
impl Widget for FinanceView {
    fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
        let step = self.view.draw_walk(cx, scope, walk);
        let r = self.view.area().rect(cx);
        if r.size.x > 100. && (self.viewport != r.size || self.origin != r.pos) {
            self.viewport = r.size;
            self.origin = r.pos;
            self.dirty = true;
        }
        self.evidence();
        step
    }
    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        if !self.started {
            self.begin(cx);
        }
        if matches!(event, Event::Shutdown) {
            self.set_foreground(cx, false);
            cx.stop_timer(self.timer);
            return;
        }
        if self.state.screen != "watchlist"
            && (matches!(event, Event::KeyDown(e) if e.key_code == KeyCode::Escape)
                || event.back_pressed())
        {
            let page = if self.state.screen == "reader" {
                "news"
            } else {
                "watchlist"
            };
            self.action(cx, "navigate", json!({"value":page}));
        }
        if let Some(id) = self.id("price_chart") {
            let w = self.view.widget(cx, &[id]);
            match event.hits(cx, w.area()) {
                Hit::FingerDown(e) => {
                    self.chart_drag = true;
                    self.inspect(cx, e.abs);
                }
                Hit::FingerMove(e) if self.chart_drag => self.inspect(cx, e.abs),
                Hit::FingerUp(_) => self.chart_drag = false,
                _ => {}
            }
        }
        // Touch rows own taps; a vertical drag scrolls and suppresses activation.
        if let Event::TouchUpdate(update) = event {
            use makepad_widgets::makepad_platform::event::TouchState;
            for touch in &update.touches {
                if touch.state == TouchState::Start {
                    self.suppress_activation = false;
                    self.list_drag = None;
                    if !self.chart_drag && self.restore.is_none() {
                        if let Some(id) = self.id("body_scroll") {
                            if self
                                .view
                                .widget(cx, &[id])
                                .area()
                                .clipped_rect(cx)
                                .contains(touch.abs)
                            {
                                self.list_drag =
                                    Some((touch.uid, touch.abs.y, self.scroll(cx) * self.scale));
                            }
                        }
                    }
                } else if let Some((uid, start, y)) = self.list_drag {
                    if uid == touch.uid {
                        let delta = touch.abs.y - start;
                        if delta.abs() > 6. {
                            self.suppress_activation = true;
                        }
                        if self.suppress_activation {
                            if let Some(id) = self.id("body_scroll") {
                                self.view
                                    .widget(cx, &[id])
                                    .set_scroll_pos(cx, dvec2(0., (y - delta).max(0.)));
                            }
                        }
                    }
                }
                if touch.state == TouchState::Stop {
                    self.list_drag = None;
                }
            }
        }
        self.view.handle_event(cx, event, scope);
        #[cfg(target_os = "macos")]
        if let Event::Custom(text) = event {
            if let Ok(value) = serde_json::from_str::<Value>(text) {
                if value["action"] == "finance.inspect_web" {
                    if let (Some(dir), Some(id)) = (
                        std::env::var_os("OCTOS_FINANCE_EVIDENCE_DIR"),
                        self.id("article_web"),
                    ) {
                        let dir = PathBuf::from(dir);
                        let w = self.view.widget(cx, &[id]);
                        cx.system_browser(LiveId(w.widget_uid().0)).inspect(
                            dir.join("web.json").to_string_lossy().into(),
                            Some(dir.join("web.png").to_string_lossy().into()),
                            value["scroll_y"].as_f64(),
                        );
                    }
                }
            }
        }
        if let Event::Actions(actions) = event {
            let mut pending = vec![];
            for item in actions {
                let Some(w) = item.downcast_ref::<WidgetAction>() else {
                    continue;
                };
                let value = match w.cast::<octoscript_widgets::kit::KitAction>() {
                    octoscript_widgets::kit::KitAction::Activated if !self.suppress_activation => {
                        None
                    }
                    octoscript_widgets::kit::KitAction::Changed(v) => Some(v),
                    _ => continue,
                };
                let id = self.actions.keys().find(|id| {
                    self.view.widget(cx, &[LiveId::from_str(id)]).widget_uid() == w.widget_uid
                });
                if let Some(id) = id {
                    let mut p = self.actions[id].clone();
                    let e = p["event"].as_str().unwrap_or("").to_owned();
                    if let Some(v) = value {
                        if e == "credential" {
                            p["text"] = v.into();
                        } else {
                            p["value"] = v.into();
                        }
                    }
                    pending.push((e, p));
                }
            }
            for (e, p) in pending {
                self.action(cx, &e, p);
            }
        }
        if let Event::NetworkResponses(responses) = event {
            for r in responses {
                let matched = match r {
                    NetworkResponse::HttpResponse { request_id, .. }
                    | NetworkResponse::HttpError { request_id, .. } => {
                        self.pending.as_ref().is_some_and(|p| p.0 == *request_id)
                    }
                    _ => false,
                };
                if !matched {
                    continue;
                }
                let (_, request, _) = self.pending.take().unwrap();
                let result = match r {
                    NetworkResponse::HttpResponse { response, .. } => providers::apply(
                        &mut self.state,
                        &request,
                        response.status_code,
                        &response.get_string_body().unwrap_or_default(),
                    ),
                    _ => Err("Network unavailable. Cached values retained.".into()),
                };
                self.state.busy.remove(&request.kind);
                match result {
                    Ok(()) => {
                        self.state.errors.remove(&request.kind);
                        self.cache();
                    }
                    Err(e) => {
                        if e.contains("Rate limit") {
                            self.queue.clear();
                            self.state.busy.clear();
                        }
                        self.state.errors.insert(request.kind, e);
                    }
                }
                self.dirty = true;
            }
        }
        if self.timer.is_event(event).is_some() && self.foreground {
            self.sync_stock_data(cx);
            if !self.dirty
                && self.restore.is_none()
                && matches!(
                    self.state.screen.as_str(),
                    "watchlist" | "search" | "edit" | "news" | "saved" | "company_news"
                )
            {
                let y = self.scroll(cx);
                let row = if matches!(
                    self.state.screen.as_str(),
                    "news" | "saved" | "company_news"
                ) {
                    108.
                } else {
                    62.
                };
                let start = (((y - 100.).max(0.) / row) as usize).saturating_sub(3);
                if start.abs_diff(self.state.list_start) >= 5 {
                    self.state.list_start = start;
                    self.dirty = true;
                }
            }
            if self
                .pending
                .as_ref()
                .is_some_and(|p| p.2.elapsed().as_secs() > 20)
            {
                let (id, r, _) = self.pending.take().unwrap();
                cx.cancel_http_request(id);
                self.state.busy.remove(&r.kind);
                self.state
                    .errors
                    .insert(r.kind, "Request timed out. Retry available.".into());
                self.dirty = true;
            }
            if self.pending.is_none()
                && self
                    .last_request
                    .is_none_or(|t| t.elapsed().as_secs() >= 10)
            {
                if let Some(r) = self.queue.pop_front() {
                    self.sequence += 1;
                    let id = LiveId(0x46494e000000 + self.sequence);
                    let mut req = HttpRequest::new(
                        r.url.clone(),
                        if r.body.is_some() {
                            HttpMethod::POST
                        } else {
                            HttpMethod::GET
                        },
                    );
                    for (k, v) in &r.headers {
                        req.set_header(k.clone(), v.clone());
                    }
                    if let Some(b) = &r.body {
                        req.set_string_body(b.clone());
                    }
                    cx.http_request(id, req);
                    self.pending = Some((id, r, Instant::now()));
                    self.last_request = Some(Instant::now());
                }
            }
            if self.dirty {
                if let Err(e) = self.mount(cx) {
                    log!("Finance mount: {e}");
                    self.dirty = false;
                }
            } else if let Some(y) = self.restore.take() {
                if let Some(selection) = self.input_selection.take() {
                    if let Some(id) = self.id(&self.input_id) {
                        let w = self.view.widget(cx, &[id]);
                        if let Some(mut input) = w.borrow_mut::<TextInput>() {
                            input.set_key_focus(cx);
                            input.set_selection(cx, selection);
                            input.reset_blink_timer(cx);
                        };
                    }
                }
                if let Some(id) = self.id("body_scroll") {
                    self.view
                        .widget(cx, &[id])
                        .set_scroll_pos(cx, dvec2(0., y * self.scale));
                    self.view.redraw(cx);
                }
            }
        }
    }
}
#[derive(Script, ScriptHook, Widget)]
struct FinanceWebView {
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
impl FinanceWebView {
    fn close(&mut self, cx: &mut Cx) {
        if self.spawned {
            cx.system_browser(LiveId(self.widget_uid().0)).close();
            self.spawned = false;
        }
    }
}
impl Widget for FinanceWebView {
    fn handle_event(&mut self, cx: &mut Cx, e: &Event, s: &mut Scope) {
        self.view.handle_event(cx, e, s);
        if matches!(e, Event::Shutdown | Event::HomeIntent) {
            self.close(cx);
        }
    }
    fn draw_walk(&mut self, cx: &mut Cx2d, s: &mut Scope, w: Walk) -> DrawStep {
        let step = self.view.draw_walk(cx, s, w);
        let id = LiveId(self.widget_uid().0);
        if !self.presented {
            return step;
        }
        if !self.spawned {
            cx.system_browser(id).spawn(&self.url);
            self.spawned = true;
        }
        cx.system_browser(id).update(self.view.area(), true);
        step
    }
}
pub fn register(vm: &mut ScriptVm) {
    makepad_widgets::browser::script_mod(vm);
    octoscript_widgets::design::script_mod(vm);
    octoscript_widgets::kit::script_mod(vm);
    script_mod(vm);
}
pub mod module;
pub use module::FINANCE_MODULE;
#[cfg(feature = "standalone")]
pub mod standalone {
    use super::*;
    app_main!(App);
    script_mod! {use mod.prelude.widgets.* startup() do #(App::script_component(vm)){ui:Root{main_window:=Window{window.title:"Finance" window.inner_size:vec2(406,776) body +:{flow:Overlay finance:=mod.widgets.FinanceView{}}}}}}
    #[derive(Script, ScriptHook)]
    pub struct App {
        #[live]
        ui: WidgetRef,
    }
    impl AppMain for App {
        fn script_mod(vm: &mut ScriptVm) -> ScriptValue {
            makepad_widgets::script_mod(vm);
            super::register(vm);
            script_mod(vm)
        }
        fn handle_event(&mut self, cx: &mut Cx, event: &Event) {
            self.ui.handle_event(cx, event, &mut Scope::empty());
        }
    }
}

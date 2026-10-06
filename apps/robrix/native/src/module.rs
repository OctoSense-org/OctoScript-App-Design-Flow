//! One Robrix Matrix client shared by the desktop and mobile AppModule hosts.
use makepad_app_module::{
    AppModule, ExecOutcome, InstanceHandles, InstanceParts, OpenArgKind, OpenSchema,
    ServiceExecutor, ValidatedOpen,
    makepad_ai_services::wire::{ServiceCall, ServiceManifest, ToolResult},
};
use makepad_widgets::*;
use std::sync::atomic::{AtomicBool, Ordering};

static INSTANCE_ACTIVE: AtomicBool = AtomicBool::new(false);

pub fn is_hosted() -> bool { INSTANCE_ACTIVE.load(Ordering::Acquire) }

script_mod! {
    use mod.prelude.widgets.*
    mod.widgets.RobrixModuleView = set_type_default() do #(RobrixModuleView::register_widget(vm)) {
        width: Fill height: Fill flow: Overlay
    }
}

#[derive(Script, ScriptHook, Widget)]
pub struct RobrixModuleView {
    #[deref] view: View,
    #[rust] app: Option<crate::app::App>,
}

impl RobrixModuleView {
    pub fn set_foreground(&mut self, cx: &mut Cx, foreground: bool) {
        if let Some(app) = self.app.as_mut() { app.set_foreground(cx, foreground); }
    }

    fn close(&mut self, cx: &mut Cx) {
        let handle = crate::sliding_sync::hosted_runtime_handle();
        let _entered = handle.as_ref().map(|handle| handle.enter());
        if let Some(mut app) = self.app.take() {
            app.close_embedded(cx);
            self.view.children.clear();
            INSTANCE_ACTIVE.store(false, Ordering::Release);
        }
    }
}

impl Widget for RobrixModuleView {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        if matches!(event, Event::Shutdown) { self.close(cx); return; }
        if let Some(app) = self.app.as_mut() {
            AppMain::handle_event(app, cx, event);
        } else {
            self.view.handle_event(cx, event, scope);
        }
    }

    fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
        if let Some(app) = self.app.as_mut() {
            app.draw_embedded(cx, &mut self.view, walk)
        } else {
            self.view.draw_walk(cx, scope, walk)
        }
    }
}

pub struct RobrixModule;
pub static ROBRIX_MODULE: RobrixModule = RobrixModule;

impl AppModule for RobrixModule {
    fn id(&self) -> &'static str { "robrix" }
    fn label(&self) -> &'static str { "Robrix" }
    fn capabilities(&self) -> &'static [&'static str] { &["net", "storage", "audio.output", "clipboard"] }
    fn open_schema(&self) -> OpenSchema { OpenSchema::new(1).arg("card_preview", OpenArgKind::Bool, false) }

    fn register(&self, vm: &mut ScriptVm) {
        crate::app::register_widgets(vm);
        script_mod(vm);
    }

    fn create(&self, vm: &mut ScriptVm, open: ValidatedOpen, _handles: InstanceHandles) -> InstanceParts {
        if open.bool("card_preview") == Some(true) {
            let value = script_eval!(vm, {
                use mod.prelude.widgets.*
                SolidView {
                    width: Fill height: Fill flow: Down padding: 20 spacing: 20
                    draw_bg.color: #f4f7fb
                    Label { text: "Robrix · AppCard preview" draw_text.color: #16233b }
                    preview := mod.widgets.RobrixAppCard {}
                }
            });
            let root = WidgetRef::script_from_value(vm, value);
            vm.with_cx_mut(|cx| {
                let card = root.widget(cx, ids!(preview));
                if let Some(mut view) = card.borrow_mut::<crate::appcard::RobrixAppCard>() {
                    let payload = serde_json::from_str(crate::appcard::FIXTURE).expect("installed fixture");
                    if let Err(error) = view.mount(cx, &payload) { error!("Robrix AppCard preview: {error}"); }
                }
            });
            return InstanceParts { root, executor: Box::new(RobrixExecutor), shutdown: Box::new(|_| {}) };
        }
        // Upstream Matrix caches and account switching are process-global.
        // Refuse a second instance even if a host bypasses launch-or-focus.
        let owns_runtime = INSTANCE_ACTIVE.compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire).is_ok();
        let value = script_eval!(vm, { mod.widgets.RobrixModuleView {} });
        let root = WidgetRef::script_from_value(vm, value);
        if let Some(mut view) = root.borrow_mut::<RobrixModuleView>() {
            if owns_runtime {
                let app = crate::app::App::create_embedded(vm);
                let content = app.content();
                view.view.children.push((live_id!(content), content.clone()));
                vm.cx_mut().widget_tree_insert_child_deep(view.widget_uid(), live_id!(content), content);
                vm.cx_mut().widget_tree_mark_dirty(view.widget_uid());
                view.app = Some(app);
            } else {
                let message = script_eval!(vm, {
                    use mod.prelude.widgets.*
                    Label { width: Fill draw_text.wrap: Words text: "Robrix is already open. Return to its existing window." }
                });
                view.view.children.push((live_id!(already_open), WidgetRef::script_from_value(vm, message)));
            }
        }
        let cleanup = root.clone();
        InstanceParts {
            root,
            executor: Box::new(RobrixExecutor),
            shutdown: Box::new(move |vm| {
                if let Some(mut view) = cleanup.borrow_mut::<RobrixModuleView>() { view.close(vm.cx_mut()); }
            }),
        }
    }
}

struct RobrixExecutor;
impl ServiceExecutor for RobrixExecutor {
    fn manifest(&self) -> ServiceManifest {
        ServiceManifest::new("robrix", "Robrix", "Matrix conversations and native AppCards.")
    }
    fn execute(&mut self, _cx: &mut Cx, call: &ServiceCall) -> ExecOutcome {
        ExecOutcome::Done(ToolResult::unavailable(&call.call_id, "Use the Robrix interface"))
    }
}

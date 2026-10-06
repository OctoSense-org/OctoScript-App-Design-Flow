use super::*;
use makepad_app_module::{
    makepad_ai_services::wire::{ServiceCall, ServiceManifest, ToolResult},
    AppModule, ExecOutcome, InstanceHandles, InstanceParts, OpenArgKind, OpenSchema,
    ServiceExecutor, ValidatedOpen,
};
pub struct FinanceModule;
pub static FINANCE_MODULE: FinanceModule = FinanceModule;
impl AppModule for FinanceModule {
    fn id(&self) -> &'static str {
        "finance"
    }
    fn label(&self) -> &'static str {
        "Finance"
    }
    fn capabilities(&self) -> &'static [&'static str] {
        &["net", "storage", "clipboard"]
    }
    fn open_schema(&self) -> OpenSchema {
        OpenSchema::new(1)
            .arg("symbol", OpenArgKind::Text, false)
            .arg("card", OpenArgKind::Text, false)
    }
    fn register(&self, vm: &mut ScriptVm) {
        super::register(vm);
    }
    fn create(&self, vm: &mut ScriptVm, open: ValidatedOpen, _: InstanceHandles) -> InstanceParts {
        let v = script_eval!(vm,{mod.widgets.FinanceView{}});
        let root = WidgetRef::script_from_value(vm, v);
        if let Some(mut finance) = root.borrow_mut::<FinanceView>() {
            if let Some(id) = open.text("symbol") {
                if finance.state.catalog.iter().any(|s| s.id == id) {
                    finance.state.selected = id.into();
                    finance.state.screen = "detail".into();
                }
            }
            if let Some(kind) = open.text("card") {
                if octosense_finance_service::cards::KINDS.contains(&kind) {
                    finance.card_kind = kind.into();
                }
            }
        }
        let cleanup = root.clone();
        InstanceParts {
            root,
            executor: Box::new(FinanceExecutor),
            shutdown: Box::new(move |vm| {
                if let Some(mut app) = cleanup.borrow_mut::<FinanceView>() {
                    app.set_foreground(vm.cx_mut(), false);
                }
            }),
        }
    }
}
struct FinanceExecutor;
impl ServiceExecutor for FinanceExecutor {
    fn manifest(&self) -> ServiceManifest {
        ServiceManifest::new(
            "finance",
            "Finance",
            "Stocks and attributed news across US, HK and mainland China.",
        )
    }
    fn execute(&mut self, _: &mut Cx, c: &ServiceCall) -> ExecOutcome {
        ExecOutcome::Done(ToolResult::unavailable(
            &c.call_id,
            "Use the Finance interface",
        ))
    }
}

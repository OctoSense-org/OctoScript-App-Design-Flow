//! Host-owned L0 recipes carried as Matrix message data.
//! A message selects an installed card; it cannot supply code, a kit or a URL.
use makepad_widgets::*;
use serde_json::{json, Value};

const CARD: &str = include_str!("../../service-cards/message-summary/page.card");
const KIT: &str = include_str!("../../service-cards/message-summary/kit.json");
pub const FIXTURE: &str = include_str!("../../service-cards/message-summary/fixture.json");

script_mod! {
    use mod.prelude.widgets.*
    mod.widgets.RobrixAppCard = set_type_default() do #(RobrixAppCard::register_widget(vm)) {
        width: Fill height: Fit flow: Down
    }
}

/// Data is deliberately separate from the installed, versioned recipe.
fn card_source(payload: &Value) -> Result<String, String> {
    if payload["schema_version"] != 1 || payload["card_id"] != "robrix.message-summary" {
        return Err("unsupported Robrix AppCard version or recipe".into());
    }
    let mut data = json!({});
    for field in ["title", "summary", "status"] {
        let text = payload["data"][field].as_str().ok_or_else(|| format!("missing card field {field}"))?;
        if text.len() > 8192 { return Err(format!("card field {field} is too long")); }
        data[field] = text.into();
    }
    let mut placements = json!({});
    for (id, component) in [("card", "surface"), ("title", "title"), ("summary", "body"), ("status", "caption")] {
        placements[id] = json!({"component":component,"layout":{}});
    }
    data["$kit"] = json!({"placements":placements});
    let kit: Value = serde_json::from_str(KIT).map_err(|error| error.to_string())?;
    let report = octoscript_ui_l0::realize(CARD, &data, Default::default());
    let source = octoscript_ui_l0::kit_pack::lower(report.complete_root()?, &kit, &data)?;
    let tree = octoscript_makepad::design::prepare(&source)?;
    Ok(octoscript_makepad::to_makepad_l0_ui(&tree))
}

#[derive(Script, ScriptHook, Widget)]
pub struct RobrixAppCard {
    #[deref] view: View,
    #[rust] payload: Option<Value>,
    #[rust] retired: Option<WidgetRef>,
}

impl RobrixAppCard {
    pub fn mount(&mut self, cx: &mut Cx, payload: &Value) -> Result<(), String> {
        if self.payload.as_ref() == Some(payload) { return Ok(()); }
        let source = card_source(payload)?;
        let script = ScriptMod {
            cargo_manifest_path: env!("CARGO_MANIFEST_DIR").into(),
            module_path: module_path!().into(), file: file!().into(), line: 1, column: 0,
            values: Vec::new(), code: format!("use mod.prelude.widgets.*\nlet Label = mod.widgets.Label {{ width: Fill draw_text.wrap: Words }}\nreturn View {{ width: Fill height: Fit flow: Down {source} }}"),
        };
        let root = cx.with_vm(|vm| vm.eval_checked(script, 200_000)
            .map(|value| WidgetRef::script_from_value(vm, value)))
            .ok_or("AppCard native tree rejected")?;
        self.retired = self.view.children.pop().map(|(_, child)| child);
        self.view.children.clear();
        self.view.children.push((live_id!(card), root.clone()));
        cx.widget_tree_insert_child_deep(self.widget_uid(), live_id!(card), root);
        cx.widget_tree_mark_dirty(self.widget_uid());
        self.payload = Some(payload.clone());
        self.redraw(cx);
        Ok(())
    }
}

impl Widget for RobrixAppCard {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        self.view.handle_event(cx, event, scope);
    }
    fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
        self.view.draw_walk(cx, scope, walk)
    }
}

pub fn mount_message(cx: &mut Cx, item: &WidgetRef, payload: Option<&Value>) -> bool {
    let card = item.widget(cx, ids!(content.native_appcard));
    let mounted = payload.is_some_and(|payload| card.borrow_mut::<RobrixAppCard>()
        .is_some_and(|mut view| view.mount(cx, payload).is_ok()));
    card.set_visible(cx, mounted);
    mounted
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn installed_recipe_renders_data_and_rejects_unknown_cards() {
        let mut payload: Value = serde_json::from_str(FIXTURE).unwrap();
        let source = card_source(&payload).unwrap();
        assert!(source.contains("OctoSense chat"));
        assert!(source.contains("makepad_widgets:resources/Roboto-Regular.ttf"));
        payload["card_id"] = "uninstalled".into();
        assert!(card_source(&payload).is_err());
        payload["card_id"] = "robrix.message-summary".into();
        payload["schema_version"] = 2.into();
        assert!(card_source(&payload).is_err());
    }

    #[test]
    fn message_text_is_escaped_and_cannot_replace_the_native_recipe() {
        let mut payload: Value = serde_json::from_str(FIXTURE).unwrap();
        payload["data"]["title"] = "\" } sys.shell(\"echo injected\") {".into();
        payload["kit"] = json!({"components": {"surface": {"style": {"t":"web"}}}});
        let source = card_source(&payload).unwrap();
        assert!(source.contains("\\\"echo injected\\\""));
        assert!(!source.contains("Browser {"));
        payload["data"]["title"] = "x".repeat(8193).into();
        assert!(card_source(&payload).is_err());
    }
}

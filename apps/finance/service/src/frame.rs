//! Native L0 kit assembly, adapted from the Mail AppCard compiler.
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
fn text<'a>(v: &'a Value, k: &str) -> &'a str {
    v[k].as_str().unwrap_or("")
}
fn hash(v: &str) -> String {
    format!("{:x}", Sha256::digest(v.as_bytes()))
}
pub struct Frame {
    pub value: Value,
    pub actions: HashMap<String, Value>,
    pub mapping: HashMap<String, String>,
}
pub fn compile(tree: &Value, controls: &Value) -> Frame {
    let nonce = "finance-native";
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
        let component = format!("Finance{}", &hash(&format!("{style}{props}{slot}"))[..14]);
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
    let card=format!("# ledger finance@1.0.0\n# level: L0\n# profile: ui/l0\ntheme light\n{declarations}{}\nview root {body}\n",definitions.values().cloned().collect::<String>());
    let value = json!({"nonce":nonce,"card":card,"data":{"$kit":{"theme":"light","placements":placements}},"pack":pack,"preserve_input_selection":true});
    Frame {
        value,
        actions,
        mapping,
    }
}

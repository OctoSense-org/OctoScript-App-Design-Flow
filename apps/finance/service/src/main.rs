use octosense_finance_service::{model::State, scenes};
use serde_json::json;
fn main() {
    let root = std::env::args().nth(1).expect("output project path");
    let base = State::default();
    for (i, page) in [
        "watchlist",
        "markets",
        "search",
        "edit",
        "detail",
        "detail",
        "company_news",
        "news",
        "reader",
        "saved",
        "settings",
        "watchlist",
    ]
    .iter()
    .enumerate()
    {
        let mut s = base.clone();
        s.screen = page.to_string();
        if i == 5 {
            s.range = "1M".into();
            s.inspection = Some(6);
        }
        if i == 9 {
            let n = s.news[1].clone();
            s.prefs.saved.insert(n.id.clone(), n);
        }
        if i == 11 {
            s.errors.insert(
                "quotes".into(),
                "Offline · cached preview values · retry available".into(),
            );
        }
        let scene = scenes::build(&s);
        let d = std::path::Path::new(&root).join(format!("cards/finance-{:02}", i + 1));
        std::fs::create_dir_all(&d).unwrap();
        let mut graphics = json!({});
        for (id, _) in scene.plots.as_object().unwrap() {
            graphics[id] = json!({"kind":"line"});
        }
        let doc = json!({"schema_version":1,"id":format!("finance-{:02}",i+1),"app":"finance","number":i+1,"title":page,"artboard":[406,776],"graphics":graphics,"tree":scene.tree});
        for (name, value) in [
            ("contract.json", doc),
            (
                "service-actions.json",
                json!({"schema_version":1,"owner":"finance","controls":scene.controls}),
            ),
            ("plots.json", scene.plots),
        ] {
            std::fs::write(
                d.join(name),
                serde_json::to_string_pretty(&value).unwrap() + "\n",
            )
            .unwrap();
        }
    }
}

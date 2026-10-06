//! Reusable Finance cards select actual application subtrees and current data.
use crate::{model::State, scenes};
use serde_json::Value;
pub const KINDS: [&str; 4] = [
    "finance.quote",
    "finance.watchlist",
    "finance.related-news",
    "finance.market-brief",
];
pub fn scene(state: &State, kind: &str) -> Result<scenes::Scene, String> {
    let (page, root) = match kind {
        "finance.quote" => ("detail", "quote_card"),
        "finance.watchlist" => ("watchlist", "watchlist_card"),
        "finance.related-news" => ("company_news", "related_news_card"),
        "finance.market-brief" => ("markets", "market_brief_card"),
        _ => return Err("Unknown Finance card".into()),
    };
    let mut state = state.clone();
    state.screen = page.into();
    state.list_start = 0;
    state.region = "All".into();
    state.query.clear();
    let mut result = scenes::build(&state);
    fn find(v: &Value, id: &str) -> Option<Value> {
        if v["id"] == id {
            return Some(v.clone());
        }
        v["c"].as_array()?.iter().find_map(|c| find(c, id))
    }
    let mut tree =
        find(&result.tree, root).ok_or("Card has insufficient data; show the app's empty state")?;
    let x = tree["x"].as_f64().unwrap();
    let y = tree["y"].as_f64().unwrap();
    let mut ids = std::collections::BTreeSet::new();
    fn translate(n: &mut Value, x: f64, y: f64, ids: &mut std::collections::BTreeSet<String>) {
        ids.insert(n["id"].as_str().unwrap().into());
        n["x"] = (n["x"].as_f64().unwrap() - x).into();
        n["y"] = (n["y"].as_f64().unwrap() - y).into();
        for c in n["c"].as_array_mut().into_iter().flatten() {
            translate(c, x, y, ids);
        }
    }
    translate(&mut tree, x, y, &mut ids);
    result
        .controls
        .as_object_mut()
        .unwrap()
        .retain(|id, _| ids.contains(id));
    result
        .plots
        .as_object_mut()
        .unwrap()
        .retain(|id, _| ids.contains(id));
    result.tree = tree;
    Ok(result)
}

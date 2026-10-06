use octosense_finance_service::{frame, model::*, providers, scenes};
use serde_json::json;
#[test]
fn listing_identity_and_search() {
    let mut s = State::default();
    s.query = "00700".into();
    assert_eq!(s.visible_securities(true)[0].id, "XHKG:00700");
    s.query = "腾讯".into();
    assert_eq!(s.visible_securities(true)[0].currency, "HKD");
    s.query = "000001".into();
    assert_eq!(s.visible_securities(true)[0].exchange, "SZSE");
    s.query = "Alibaba".into();
    assert_eq!(s.visible_securities(true).len(), 2);
}
#[test]
fn watchlist_reorder_remove_persists() {
    let mut s = State::default();
    s.act("move_up", &json!({"value":"XHKG:00700"}));
    assert_eq!(s.prefs.watchlist[1], "XHKG:00700");
    s.act("follow", &json!({"value":"XNAS:AAPL"}));
    let p: Preferences = serde_json::from_str(&serde_json::to_string(&s.prefs).unwrap()).unwrap();
    assert!(!State::new(p)
        .prefs
        .watchlist
        .contains(&"XNAS:AAPL".to_owned()));
}
#[test]
fn bookmark_survives_feed_rotation() {
    let mut s = State::default();
    s.act("save", &json!({"value":"preview-1"}));
    s.news.clear();
    s.screen = "saved".into();
    assert_eq!(s.stories()[0].id, "preview-1");
    s.act("save", &json!({"value":"preview-1"}));
    assert!(s.stories().is_empty());
}
#[test]
fn preview_never_mixes_with_live() {
    let mut s = State::default();
    s.act("preview", &json!({}));
    assert!(s.quotes.is_empty() && s.history.is_empty() && s.news.is_empty());
    assert!(providers::requests(&s, &providers::Keys::default()).is_empty());
}
#[test]
fn daily_return_differs_from_selected_range() {
    let mut s = State::default();
    let today = s.quotes[&s.selected].change_pct().unwrap();
    s.act("range", &json!({"value":"1M"}));
    let p = s.points();
    let ret = (p.last().unwrap().price / p[0].price - 1.) * 100.;
    assert!((today - 1.2).abs() < 1e-8);
    assert!((ret - today).abs() > 10.);
}
#[test]
fn quotes_keep_provider_timestamp_and_missing_stats() {
    let mut s = State::new(Preferences {
        preview: false,
        ..Default::default()
    });
    let req = providers::requests(
        &s,
        &providers::Keys {
            alltick: "fixture-test-key".into(),
            ..Default::default()
        },
    )
    .remove(0);
    let data = json!({"ret":200,"data":{"tick_list":[{"code":"700.HK","price":"400.00","tick_time":"1789574400000"}]}});
    providers::apply(&mut s, &req, 200, &data.to_string()).unwrap();
    assert_eq!(s.quotes["XHKG:00700"].timestamp, 1789574400);
    assert_eq!(s.quotes["XHKG:00700"].change_pct(), None);
    assert!(providers::apply(&mut s, &req, 429, "{}").is_err());
    assert_eq!(s.quotes["XHKG:00700"].price, 400.);
}
#[test]
fn company_alias_boundaries() {
    let c = catalog();
    assert!(providers::related(&c, "Pineapple harvest increases").is_empty());
    assert!(providers::related(&c, "Apple supplier outlook").contains(&"XNAS:AAPL".into()));
    assert!(providers::related(&c, "腾讯控股发布财报").contains(&"XHKG:00700".into()));
}
#[test]
fn all_twelve_states_compile_to_l0_and_have_unique_ids() {
    let mut s = State::default();
    for page in [
        "watchlist",
        "markets",
        "search",
        "edit",
        "detail",
        "company_news",
        "news",
        "reader",
        "saved",
        "settings",
    ] {
        s.screen = page.into();
        let scene = scenes::build(&s);
        let mut ids = std::collections::BTreeSet::new();
        fn visit(v: &serde_json::Value, ids: &mut std::collections::BTreeSet<String>) {
            assert!(ids.insert(v["id"].as_str().unwrap().into()));
            for c in v["c"].as_array().into_iter().flatten() {
                visit(c, ids);
            }
        }
        visit(&scene.tree, &mut ids);
        let f = frame::compile(&scene.tree, &scene.controls);
        assert_eq!(f.mapping.len(), ids.len());
        assert!(f.value["card"].as_str().unwrap().contains("view root"));
    }
}

#[test]
fn extracted_cards_bind_current_application_data() {
    let mut s = State::default();
    s.quotes.get_mut("XNAS:AAPL").unwrap().price = 123.45;
    for kind in octosense_finance_service::cards::KINDS {
        let card = octosense_finance_service::cards::scene(&s, kind).unwrap();
        assert!(card.tree["h"].as_f64().unwrap() < 400.);
        assert_eq!(card.tree["x"], 0.);
        if kind == "finance.quote" {
            assert!(card.tree.to_string().contains("123.45"));
        }
    }
}
#[test]
fn public_directory_is_windowed() {
    let mut s = State::default();
    s.screen = "search".into();
    assert!(s.catalog.len() > 10000);
    s.list_start = 400;
    let scene = scenes::build(&s);
    let f = frame::compile(&scene.tree, &scene.controls);
    assert!(f.mapping.contains_key("stock_400"));
    assert!(!f.mapping.contains_key("stock_399"));
    assert!(f.mapping.len() < 400);
}

#[test]
fn daily_bar_supplies_day_change_without_using_range_start() {
    let mut s = State::new(Preferences {
        preview: false,
        ..Default::default()
    });
    let requests = providers::requests(
        &s,
        &providers::Keys {
            alltick: "test-only".into(),
            ..Default::default()
        },
    );
    let q = requests.iter().find(|r| r.kind == "quotes").unwrap();
    providers::apply(&mut s,q,200,&json!({"ret":200,"data":{"tick_list":[{"code":"700.HK","price":"400","tick_time":"1789574400000"}]}}).to_string()).unwrap();
    let d = requests.iter().find(|r| r.kind == "daily").unwrap();
    let body = json!({"ret":200,"data":{"kline_list":[{"code":"700.HK","kline_data":[{"timestamp":"1789488000","close_price":"390"},{"timestamp":"1789574400","close_price":"400","open_price":"395","high_price":"402","low_price":"393"}]}]}});
    providers::apply(&mut s, d, 200, &body.to_string()).unwrap();
    assert_eq!(s.quotes["XHKG:00700"].previous_close, Some(390.));
    assert!((s.quotes["XHKG:00700"].change_pct().unwrap() - 1000. / 390.).abs() < 1e-9);
}
#[test]
fn empty_cards_remain_renderable() {
    let mut s = State::default();
    s.prefs.watchlist.clear();
    s.news.clear();
    assert!(octosense_finance_service::cards::scene(&s, "finance.watchlist").is_ok());
    assert!(octosense_finance_service::cards::scene(&s, "finance.related-news").is_ok());
}
#[test]
fn chinese_news_keeps_source_and_never_invents_url() {
    let mut s = State::new(Preferences {
        preview: false,
        ..Default::default()
    });
    s.screen = "news".into();
    let req = providers::requests(
        &s,
        &providers::Keys {
            tushare: "test-only".into(),
            ..Default::default()
        },
    )
    .remove(0);
    let body = json!({"code":0,"data":{"fields":["datetime","title","content"],"items":[["2026-09-16 15:00:00","腾讯控股发布财报","Fixture article"]]}});
    providers::apply(&mut s, &req, 200, &body.to_string()).unwrap();
    assert_eq!(s.news[0].url, None);
    assert_eq!(s.news[0].market, "HK");
    assert!(s.news[0].securities.contains(&"XHKG:00700".into()));
}

#[test]
fn stockplot_symbols_preserve_exchange_identity() {
    let s = State::default();
    for (id, expected) in [
        ("XNAS:AAPL", "AAPL"),
        ("XHKG:00700", "0700.HK"),
        ("XHKG:09988", "9988.HK"),
        ("XSHG:600519", "600519.SS"),
        ("XSHE:300750", "300750.SZ"),
    ] {
        assert_eq!(
            s.catalog
                .iter()
                .find(|s| s.id == id)
                .unwrap()
                .yahoo_symbol()
                .as_deref(),
            Some(expected)
        );
    }
}

#[test]
fn stockplot_quote_and_chart_share_response_without_range_day_mixup() {
    let mut s = State::new(Preferences {
        preview: false,
        ..Default::default()
    });
    let body = json!({"chart":{"result":[{"meta":{"symbol":"AAPL","currency":"USD","regularMarketPrice":12.0,"previousClose":11.0,"chartPreviousClose":9.0,"regularMarketTime":300},"timestamp":[100,200,300],"indicators":{"quote":[{"close":[10.0,null,12.0],"open":[9.5,null,11.0]}]}}]}});
    providers::apply_stockplot(
        &mut s,
        "XNAS:AAPL",
        "1D",
        &serde_json::to_vec(&body).unwrap(),
    )
    .unwrap();
    assert_eq!(s.history["XNAS:AAPL:1D"].len(), 2);
    assert_eq!(s.history["XNAS:AAPL:1D"][1].time, 300);
    assert_eq!(s.quotes["XNAS:AAPL"].price, 12.0);
    assert_eq!(s.quotes["XNAS:AAPL"].previous_close, Some(11.0));
    assert_eq!(s.quotes["XNAS:AAPL"].open, Some(9.5));
    let mut month = body;
    month["chart"]["result"][0]["meta"]["previousClose"] = 7.0.into();
    providers::apply_stockplot(
        &mut s,
        "XNAS:AAPL",
        "1M",
        &serde_json::to_vec(&month).unwrap(),
    )
    .unwrap();
    assert_eq!(s.quotes["XNAS:AAPL"].previous_close, Some(11.0));
    assert_eq!(s.history["XNAS:AAPL:1M"].len(), 2);
}

#[test]
fn stockplot_rejects_mismatched_currency_without_populating_data() {
    let mut s = State::new(Preferences {
        preview: false,
        ..Default::default()
    });
    let body = json!({"chart":{"result":[{"meta":{"symbol":"0700.HK","currency":"USD"},"timestamp":[100,200],"indicators":{"quote":[{"close":[10.0,12.0]}]}}]}});
    assert!(providers::apply_stockplot(
        &mut s,
        "XHKG:00700",
        "1D",
        &serde_json::to_vec(&body).unwrap()
    )
    .is_err());
    assert!(s.quotes.is_empty() && s.history.is_empty());
}

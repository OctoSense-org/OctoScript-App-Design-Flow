//! Documented provider payloads; requests never implement Debug to avoid logging keys.
use crate::model::*;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

pub struct Request {
    pub url: String,
    pub body: Option<String>,
    pub headers: Vec<(String, String)>,
    pub kind: String,
    pub security: String,
    pub range: String,
}
#[derive(Default)]
pub struct Keys {
    pub alltick: String,
    pub finnhub: String,
    pub tushare: String,
}
fn encode(s: &str) -> String {
    s.bytes()
        .map(|b| {
            if b.is_ascii_alphanumeric() || b"-_.~".contains(&b) {
                (b as char).to_string()
            } else {
                format!("%{b:02X}")
            }
        })
        .collect()
}
fn num(v: &Value) -> Option<f64> {
    v.as_f64()
        .or_else(|| v.as_str()?.parse().ok())
        .filter(|v| v.is_finite())
}
fn integer(v: &Value) -> Option<i64> {
    v.as_i64().or_else(|| v.as_str()?.parse().ok())
}
fn all(key: &str, method: &str, data: Value, kind: &str, security: &str, range: &str) -> Request {
    let query =
        json!({"trace":format!("finance-{}",chrono::Utc::now().timestamp_micros()),"data":data});
    Request {
        url: format!(
            "https://quote.alltick.co/quote-stock-b-api/{method}?token={}&query={}",
            encode(key),
            encode(&query.to_string())
        ),
        body: None,
        headers: vec![],
        kind: kind.into(),
        security: security.into(),
        range: range.into(),
    }
}
pub fn requests(s: &State, k: &Keys) -> Vec<Request> {
    let mut out = vec![];
    if s.prefs.preview {
        return out;
    }
    if !k.alltick.is_empty() {
        let ids = if s.screen == "detail" {
            vec![s.selected.clone()]
        } else {
            s.prefs.watchlist.clone()
        };
        let secs: Vec<_> = ids
            .iter()
            .filter_map(|id| s.catalog.iter().find(|v| &v.id == id))
            .collect();
        for batch in secs.chunks(5) {
            out.push(all(&k.alltick,"trade-tick",json!({"symbol_list":batch.iter().map(|v|json!({"code":v.provider_code})).collect::<Vec<_>>()}),"quotes","",""));
        }
        for batch in secs.chunks(5) {
            out.push(Request {url:format!("https://quote.alltick.co/quote-stock-b-api/batch-kline?token={}",encode(&k.alltick)),body:Some(json!({"trace":format!("finance-daily-{}",chrono::Utc::now().timestamp_micros()),"data":{"data_list":batch.iter().map(|sec|json!({"code":sec.provider_code,"kline_type":8,"kline_timestamp_end":0,"query_kline_num":2,"adjust_type":0})).collect::<Vec<_>>()}}).to_string()),headers:vec![("Content-Type".into(),"application/json".into())],kind:"daily".into(),security:String::new(),range:String::new()});
        }
        if s.screen == "detail" {
            let range = s.range.as_str();
            let (kind, count) = match range {
                "1D" => (2, 200),
                "1W" => (8, 7),
                "1M" => (8, 24),
                "6M" => (8, 140),
                _ => (8, 270),
            };
            out.push(all(&k.alltick,"kline",json!({"code":s.security().provider_code,"kline_type":kind,"kline_timestamp_end":0,"query_kline_num":count,"adjust_type":0}),"chart",&s.selected,range));
        }
    }
    if ["news", "company_news", "settings", "watchlist"].contains(&s.screen.as_str()) {
        if !k.finnhub.is_empty() {
            let today = chrono::Utc::now().date_naive();
            let company = s.screen == "company_news" && s.security().market == "US";
            let url = if company {
                format!(
                    "https://finnhub.io/api/v1/company-news?symbol={}&from={}&to={}",
                    encode(&s.security().symbol),
                    today - chrono::Duration::days(7),
                    today
                )
            } else {
                "https://finnhub.io/api/v1/news?category=general&minId=0".into()
            };
            out.push(Request {
                url,
                body: None,
                headers: vec![("X-Finnhub-Token".into(), k.finnhub.clone())],
                kind: "finnhub".into(),
                security: if company {
                    s.selected.clone()
                } else {
                    String::new()
                },
                range: String::new(),
            });
        }
        if !k.tushare.is_empty() {
            let now = chrono::Utc::now() + chrono::Duration::hours(8);
            out.push(Request{url:"https://api.tushare.pro".into(),body:Some(json!({"api_name":"news","token":k.tushare,"params":{"src":"sina","start_date":(now-chrono::Duration::days(1)).format("%Y-%m-%d %H:%M:%S").to_string(),"end_date":now.format("%Y-%m-%d %H:%M:%S").to_string()},"fields":"datetime,title,content"}).to_string()),headers:vec![("Content-Type".into(),"application/json".into())],kind:"tushare".into(),security:String::new(),range:String::new()});
        }
    }
    out
}
pub fn apply(s: &mut State, r: &Request, status: u16, body: &str) -> Result<(), String> {
    if status == 429 {
        return Err("Rate limit reached. Wait before retrying.".into());
    }
    if status == 401 || status == 403 {
        return Err("Check API key and data permissions.".into());
    }
    if status != 200 {
        return Err(format!("Provider returned HTTP {status}."));
    }
    let v: Value = serde_json::from_str(body).map_err(|_| "Invalid provider response.")?;
    match r.kind.as_str() {
        "daily" => {
            if v["ret"] != 200 {
                return Err("Daily statistics unavailable for this subscription.".into());
            }
            for item in v["data"]["kline_list"]
                .as_array()
                .ok_or("Missing daily statistics.")?
            {
                let Some(sec) = s
                    .catalog
                    .iter()
                    .find(|sec| item["code"] == sec.provider_code)
                else {
                    continue;
                };
                let Some(q) = s.quotes.get_mut(&sec.id) else {
                    continue;
                };
                let mut bars: Vec<_> = item["kline_data"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter(|b| integer(&b["timestamp"]).is_some())
                    .collect();
                bars.sort_by_key(|b| integer(&b["timestamp"]).unwrap());
                let Some(last) = bars.last() else {
                    continue;
                };
                let bar_day = local_day(integer(&last["timestamp"]).unwrap(), &sec.timezone);
                let quote_day = local_day(q.timestamp, &sec.timezone);
                if bar_day == quote_day {
                    q.previous_close = bars
                        .iter()
                        .rev()
                        .skip(1)
                        .find_map(|b| num(&b["close_price"]));
                    q.open = num(&last["open_price"]);
                    q.high = num(&last["high_price"]);
                    q.low = num(&last["low_price"]);
                } else if bar_day < quote_day {
                    q.previous_close = num(&last["close_price"]);
                }
            }
        }
        "quotes" | "chart" => {
            if v["ret"] != 200 {
                return Err(format!(
                    "AllTick error {}. Check symbol coverage and quota.",
                    v["ret"].as_i64().unwrap_or(0)
                ));
            }
            if r.kind == "quotes" {
                let list = v["data"]["tick_list"]
                    .as_array()
                    .ok_or("Missing quote list.")?;
                if list.is_empty() {
                    return Err("No quotes permitted or available.".into());
                }
                for tick in list {
                    let Some(sec) = s
                        .catalog
                        .iter()
                        .find(|sec| tick["code"] == sec.provider_code)
                    else {
                        continue;
                    };
                    let (price, ms) = (
                        num(&tick["price"])
                            .filter(|p| *p > 0.)
                            .ok_or("Invalid quote price.")?,
                        integer(&tick["tick_time"]).ok_or("Missing observation time.")?,
                    );
                    s.quotes.insert(
                        sec.id.clone(),
                        Quote {
                            price,
                            previous_close: None,
                            open: None,
                            high: None,
                            low: None,
                            timestamp: ms / 1000,
                            source: "AllTick".into(),
                            delay: "Delay not declared by feed".into(),
                        },
                    );
                }
            } else {
                if v["data"]["code"]
                    != s.catalog
                        .iter()
                        .find(|s| s.id == r.security)
                        .map(|s| s.provider_code.as_str())
                        .unwrap_or("")
                {
                    return Err("Chart symbol mismatch.".into());
                }
                let list = v["data"]["kline_list"]
                    .as_array()
                    .ok_or("Missing chart samples.")?;
                let mut points: Vec<_> = list
                    .iter()
                    .filter_map(|p| {
                        Some(Point {
                            time: integer(&p["timestamp"])?,
                            price: num(&p["close_price"]).filter(|p| *p > 0.)?,
                        })
                    })
                    .collect();
                points.sort_by_key(|p| p.time);
                points.dedup_by_key(|p| p.time);
                if points.len() < 2 {
                    return Err("Insufficient history for this range.".into());
                }
                // AllTick's stock timestamp pagination is unsupported. Never fabricate older bars.
                let last = points.last().unwrap().time;
                let window = match r.range.as_str() {
                    "1D" => 86400,
                    "1W" => 7 * 86400,
                    "1M" => 31 * 86400,
                    "6M" => 184 * 86400,
                    _ => 366 * 86400,
                };
                if r.range == "1D" {
                    let tz = s
                        .catalog
                        .iter()
                        .find(|sec| sec.id == r.security)
                        .map(|s| s.timezone.as_str())
                        .unwrap_or("UTC");
                    let day = local_day(last, tz);
                    points.retain(|p| local_day(p.time, tz) == day);
                } else {
                    points.retain(|p| p.time > last - window);
                }
                if points.len() < 2 {
                    return Err("Insufficient history for this trading session.".into());
                }
                s.history
                    .insert(format!("{}:{}", r.security, r.range), points);
            }
        }
        "finnhub" => {
            let list = v.as_array().ok_or("News access unavailable.")?;
            for n in list {
                let Some(title) = n["headline"].as_str().filter(|s| !s.trim().is_empty()) else {
                    continue;
                };
                let url = n["url"]
                    .as_str()
                    .filter(|u| u.starts_with("https://"))
                    .map(str::to_owned);
                let id = format!("finnhub-{}", n["id"]);
                let mut ids = vec![];
                if !r.security.is_empty() {
                    ids.push(r.security.clone());
                } else {
                    let text = format!("{title} {}", n["summary"].as_str().unwrap_or(""));
                    ids = related(&s.catalog, &text);
                }
                let story = Story {
                    id,
                    title: title.into(),
                    summary: n["summary"].as_str().unwrap_or("").into(),
                    source: n["source"].as_str().unwrap_or("Finnhub").into(),
                    url,
                    timestamp: integer(&n["datetime"]).unwrap_or(0),
                    market: "US".into(),
                    language: "en".into(),
                    securities: ids,
                };
                upsert(s, story);
            }
        }
        "tushare" => {
            if v["code"] != 0 {
                return Err("Tushare news requires its own access permission.".into());
            }
            let fields = v["data"]["fields"]
                .as_array()
                .ok_or("Missing news fields.")?;
            let rows = v["data"]["items"].as_array().ok_or("Missing news items.")?;
            for row in rows {
                let get = |key: &str| {
                    fields
                        .iter()
                        .position(|x| x == key)
                        .and_then(|i| row[i].as_str())
                        .unwrap_or("")
                };
                let title = get("title");
                if title.is_empty() {
                    continue;
                }
                let summary = get("content");
                let date = get("datetime");
                let timestamp = chrono::NaiveDateTime::parse_from_str(date, "%Y-%m-%d %H:%M:%S")
                    .map(|d| d.and_utc().timestamp() - 8 * 3600)
                    .unwrap_or(0);
                let id = format!(
                    "tushare-{:x}",
                    Sha256::digest(format!("{date}{title}").as_bytes())
                );
                let ids = related(&s.catalog, &format!("{title} {summary}"));
                let market = if ids.iter().any(|id| id.starts_with("XHKG:")) {
                    "HK"
                } else {
                    "CN"
                };
                upsert(
                    s,
                    Story {
                        id,
                        title: title.into(),
                        summary: summary.into(),
                        source: "Sina via Tushare".into(),
                        url: None,
                        timestamp,
                        market: market.into(),
                        language: "cn".into(),
                        securities: ids,
                    },
                );
            }
        }
        _ => return Err("Unknown provider response.".into()),
    }
    Ok(())
}
fn upsert(s: &mut State, n: Story) {
    if let Some(old) = s.news.iter_mut().find(|old| {
        old.id == n.id
            || n.url
                .as_ref()
                .is_some_and(|url| old.url.as_ref() == Some(url))
    }) {
        *old = n;
    } else {
        s.news.push(n);
    }
    s.news.sort_by_key(|n| std::cmp::Reverse(n.timestamp));
    s.news.truncate(1500);
}
pub fn related(catalog: &[Security], text: &str) -> Vec<String> {
    let lower = text.to_lowercase();
    catalog
        .iter()
        .filter(|s| {
            s.aliases.iter().any(|alias| {
                let alias = alias.to_lowercase();
                if alias.chars().any(|c| !c.is_ascii()) {
                    lower.contains(&alias)
                } else {
                    lower.match_indices(&alias).any(|(at, _)| {
                        let before = lower[..at].chars().next_back();
                        let after = lower[at + alias.len()..].chars().next();
                        !before.is_some_and(|c| c.is_alphanumeric())
                            && !after.is_some_and(|c| c.is_alphanumeric())
                    })
                }
            })
        })
        .map(|s| s.id.clone())
        .collect()
}

fn local_day(time: i64, zone: &str) -> Option<chrono::NaiveDate> {
    let tz: chrono_tz::Tz = zone.parse().ok()?;
    Some(
        chrono::DateTime::from_timestamp(time, 0)?
            .with_timezone(&tz)
            .date_naive(),
    )
}

/// Read the same Yahoo response that the built-in A2App StockPlot consumes.
/// Never combine a range's opening price with the daily previous close.
pub fn apply_stockplot(
    s: &mut State,
    security: &str,
    range: &str,
    bytes: &[u8],
) -> Result<(), String> {
    let sec = s
        .catalog
        .iter()
        .find(|v| v.id == security)
        .ok_or("Unknown listing")?;
    let symbol = sec
        .yahoo_symbol()
        .ok_or("Listing has no StockPlot symbol")?;
    let root: Value = serde_json::from_slice(bytes).map_err(|_| "Invalid market response")?;
    let result = root
        .pointer("/chart/result/0")
        .ok_or("Market series unavailable")?;
    let meta = &result["meta"];
    if meta["symbol"]
        .as_str()
        .map(str::to_ascii_uppercase)
        .as_deref()
        != Some(symbol.as_str())
    {
        return Err("Market response listing mismatch".into());
    }
    if meta["currency"].as_str() != Some(sec.currency.as_str()) {
        return Err("Market response currency mismatch".into());
    }
    let timestamps = result["timestamp"]
        .as_array()
        .ok_or("Market timestamps unavailable")?;
    let bars = &result["indicators"]["quote"][0];
    let closes = bars["close"]
        .as_array()
        .ok_or("Market prices unavailable")?;
    let points: Vec<Point> = timestamps
        .iter()
        .zip(closes)
        .filter_map(|(t, p)| {
            Some(Point {
                time: integer(t)?,
                price: num(p)?,
            })
        })
        .collect();
    if points.len() < 2 {
        return Err("Market series has fewer than two prices".into());
    }
    if range == "1D" {
        let last = points.last().unwrap();
        s.quotes.insert(
            security.into(),
            Quote {
                price: num(&meta["regularMarketPrice"]).unwrap_or(last.price),
                previous_close: num(&meta["previousClose"])
                    .or_else(|| num(&meta["chartPreviousClose"])),
                open: bars["open"].as_array().and_then(|v| v.iter().find_map(num)),
                high: num(&meta["regularMarketDayHigh"]),
                low: num(&meta["regularMarketDayLow"]),
                timestamp: integer(&meta["regularMarketTime"]).unwrap_or(last.time),
                source: "Yahoo Finance · A2App StockPlot".into(),
                delay: integer(&meta["exchangeDataDelayedBy"])
                    .map(|n| format!("Provider-reported delay: {n} minutes"))
                    .unwrap_or_else(|| "Delay not reported".into()),
            },
        );
    }
    s.history.insert(format!("{security}:{range}"), points);
    Ok(())
}

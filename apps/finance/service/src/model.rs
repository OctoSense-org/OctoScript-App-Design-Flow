use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Security {
    pub id: String,
    pub symbol: String,
    pub name: String,
    pub chinese: String,
    pub market: String,
    pub exchange: String,
    pub currency: String,
    pub timezone: String,
    pub provider_code: String,
    pub aliases: Vec<String>,
}
impl Security {
    /// Exchange-qualified symbol for the A2App StockPlot data source.
    pub fn yahoo_symbol(&self) -> Option<String> {
        match self.market.as_str() {
            "US" => Some(self.symbol.replace('.', "-")),
            "HK" => self
                .symbol
                .parse::<u32>()
                .ok()
                .map(|n| format!("{n:04}.HK")),
            "CN" if self.id.starts_with("XSHG:") => Some(format!("{}.SS", self.symbol)),
            "CN" if self.id.starts_with("XSHE:") => Some(format!("{}.SZ", self.symbol)),
            _ => None,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Quote {
    pub price: f64,
    pub previous_close: Option<f64>,
    pub open: Option<f64>,
    pub high: Option<f64>,
    pub low: Option<f64>,
    pub timestamp: i64,
    pub source: String,
    pub delay: String,
}
impl Quote {
    pub fn change_pct(&self) -> Option<f64> {
        self.previous_close
            .filter(|p| *p > 0.)
            .map(|p| (self.price / p - 1.) * 100.)
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Point {
    pub time: i64,
    pub price: f64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Story {
    pub id: String,
    pub title: String,
    pub summary: String,
    pub source: String,
    pub url: Option<String>,
    pub timestamp: i64,
    pub market: String,
    pub language: String,
    pub securities: Vec<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct Preferences {
    pub watchlist: Vec<String>,
    pub saved: BTreeMap<String, Story>,
    pub preview: bool,
    pub language: String,
    pub light: bool,
    pub red_up: bool,
}
impl Default for Preferences {
    fn default() -> Self {
        Self {
            watchlist: [
                "XNAS:AAPL",
                "XNAS:MSFT",
                "XHKG:00700",
                "XHKG:09988",
                "XSHG:600519",
                "XSHE:300750",
            ]
            .iter()
            .map(|s| s.to_string())
            .collect(),
            saved: BTreeMap::new(),
            preview: true,
            language: "en".into(),
            light: false,
            red_up: false,
        }
    }
}
#[derive(Clone, Debug)]
pub struct State {
    pub prefs: Preferences,
    pub catalog: Vec<Security>,
    pub quotes: BTreeMap<String, Quote>,
    pub history: BTreeMap<String, Vec<Point>>,
    pub news: Vec<Story>,
    pub screen: String,
    pub region: String,
    pub query: String,
    pub selected: String,
    pub article: String,
    pub range: String,
    pub errors: BTreeMap<String, String>,
    pub busy: BTreeSet<String>,
    pub inspection: Option<usize>,
    pub news_limit: usize,
    pub list_start: usize,
}
pub fn catalog() -> Vec<Security> {
    let entries = [
        (
            "XNAS:AAPL",
            "AAPL",
            "Apple",
            "苹果",
            "US",
            "NASDAQ",
            "USD",
            "America/New_York",
            "AAPL.US",
        ),
        (
            "XNAS:MSFT",
            "MSFT",
            "Microsoft",
            "微软",
            "US",
            "NASDAQ",
            "USD",
            "America/New_York",
            "MSFT.US",
        ),
        (
            "XHKG:00700",
            "00700",
            "Tencent Holdings",
            "腾讯控股",
            "HK",
            "HKEX",
            "HKD",
            "Asia/Hong_Kong",
            "700.HK",
        ),
        (
            "XHKG:09988",
            "09988",
            "Alibaba Group",
            "阿里巴巴",
            "HK",
            "HKEX",
            "HKD",
            "Asia/Hong_Kong",
            "9988.HK",
        ),
        (
            "XSHG:600519",
            "600519",
            "Kweichow Moutai",
            "贵州茅台",
            "CN",
            "SSE",
            "CNY",
            "Asia/Shanghai",
            "600519.SH",
        ),
        (
            "XSHE:300750",
            "300750",
            "CATL",
            "宁德时代",
            "CN",
            "SZSE",
            "CNY",
            "Asia/Shanghai",
            "300750.SZ",
        ),
        (
            "XNAS:TSLA",
            "TSLA",
            "Tesla",
            "特斯拉",
            "US",
            "NASDAQ",
            "USD",
            "America/New_York",
            "TSLA.US",
        ),
        (
            "XNAS:NVDA",
            "NVDA",
            "NVIDIA",
            "英伟达",
            "US",
            "NASDAQ",
            "USD",
            "America/New_York",
            "NVDA.US",
        ),
        (
            "XNYS:BABA",
            "BABA",
            "Alibaba ADR",
            "阿里巴巴美股",
            "US",
            "NYSE",
            "USD",
            "America/New_York",
            "BABA.US",
        ),
        (
            "XHKG:01810",
            "01810",
            "Xiaomi",
            "小米集团",
            "HK",
            "HKEX",
            "HKD",
            "Asia/Hong_Kong",
            "1810.HK",
        ),
        (
            "XSHG:601318",
            "601318",
            "Ping An Insurance",
            "中国平安",
            "CN",
            "SSE",
            "CNY",
            "Asia/Shanghai",
            "601318.SH",
        ),
        (
            "XSHE:000001",
            "000001",
            "Ping An Bank",
            "平安银行",
            "CN",
            "SZSE",
            "CNY",
            "Asia/Shanghai",
            "000001.SZ",
        ),
    ];
    let mut result: Vec<Security> = entries
        .into_iter()
        .map(
            |(id, symbol, name, cn, market, exchange, currency, tz, code)| Security {
                id: id.into(),
                symbol: symbol.into(),
                name: name.into(),
                chinese: cn.into(),
                market: market.into(),
                exchange: exchange.into(),
                currency: currency.into(),
                timezone: tz.into(),
                provider_code: code.into(),
                aliases: vec![name.into(), cn.into()],
            },
        )
        .collect();
    let rows: Vec<[String; 3]> = serde_json::from_str(include_str!("../data/directory.json"))
        .expect("bundled public directory");
    let mut known: BTreeSet<String> = result.iter().map(|s| s.provider_code.clone()).collect();
    for [code, name, market] in rows {
        if !known.insert(code.clone()) {
            continue;
        }
        let Some((raw, _)) = code.rsplit_once('.') else {
            continue;
        };
        let (prefix, exchange, currency, tz) = match market.as_str() {
            "HK" => ("XHKG", "HKEX", "HKD", "Asia/Hong_Kong"),
            "CN" if code.ends_with(".SH") => ("XSHG", "SSE", "CNY", "Asia/Shanghai"),
            "CN" => ("XSHE", "SZSE", "CNY", "Asia/Shanghai"),
            _ => ("US", "US venue unspecified", "USD", "America/New_York"),
        };
        let symbol = if market == "HK" {
            format!("{raw:0>5}")
        } else {
            raw.to_owned()
        };
        result.push(Security {
            id: format!("{prefix}:{symbol}"),
            symbol,
            name: name.clone(),
            chinese: name.clone(),
            market,
            exchange: exchange.into(),
            currency: currency.into(),
            timezone: tz.into(),
            provider_code: code,
            aliases: vec![name],
        });
    }
    result
}
impl Default for State {
    fn default() -> Self {
        Self::new(Preferences::default())
    }
}
impl State {
    pub fn new(prefs: Preferences) -> Self {
        let mut s = Self {
            prefs,
            catalog: catalog(),
            quotes: BTreeMap::new(),
            history: BTreeMap::new(),
            news: vec![],
            screen: "watchlist".into(),
            region: "All".into(),
            query: String::new(),
            selected: "XNAS:AAPL".into(),
            article: "preview-0".into(),
            range: "1D".into(),
            errors: BTreeMap::new(),
            busy: BTreeSet::new(),
            inspection: None,
            news_limit: 24,
            list_start: 0,
        };
        if s.prefs.preview {
            s.load_preview();
        }
        s
    }
    pub fn load_preview(&mut self) {
        self.quotes.clear();
        self.history.clear();
        self.news.clear();
        self.errors.clear();
        let prices = [
            220., 420., 400., 100., 1400., 250., 230., 120., 100., 25., 50., 10.,
        ];
        let changes = [
            1.2, -0.4, -0.6, 0.9, 0.8, 1.6, -0.2, 0.5, 0.9, 0.8, 0.2, -0.3,
        ];
        for (i, sec) in self.catalog.iter().take(12).enumerate() {
            self.quotes.insert(
                sec.id.clone(),
                Quote {
                    price: prices[i],
                    previous_close: Some(prices[i] / (1. + changes[i] / 100.)),
                    open: Some(prices[i] * 217.4 / 220.),
                    high: Some(prices[i] * 220.5 / 220.),
                    low: Some(prices[i] * 217. / 220.),
                    timestamp: 1789574400,
                    source: "Preview fixture".into(),
                    delay: "Fictional • not market data".into(),
                },
            );
            for (r, step) in [
                ("1D", 1800),
                ("1W", 86400),
                ("1M", 259200),
                ("6M", 1728000),
                ("1Y", 3456000),
            ] {
                let samples = if r == "1D" {
                    vec![
                        217.4, 218., 217.8, 218.9, 218.4, 219.1, 218.7, 219.5, 219.3, 220.,
                    ]
                } else {
                    vec![180., 187., 183., 195., 202., 197., 211., 205., 214., 220.]
                };
                self.history.insert(
                    format!("{}:{r}", sec.id),
                    samples
                        .iter()
                        .enumerate()
                        .map(|(j, p)| Point {
                            time: 1789574400 - (9 - j as i64) * step,
                            price: p * prices[i] / 220.,
                        })
                        .collect(),
                );
            }
        }
        for (i, title) in [
            "Three markets, one watchlist",
            "Apple supplier outlook in focus",
            "What investors are watching this week",
            "A closer look at hardware demand",
            "观察港股科技板块",
            "A股公司动态",
        ]
        .into_iter()
        .enumerate()
        {
            self.news.push(Story{id:format!("preview-{i}"),title:title.into(),summary:format!("{title}. This is a fictional article for reviewing the Finance app. Prices and headlines shown in preview mode are deterministic fixtures.\n\nUS, Hong Kong and mainland China listings keep separate currencies and exchange identities. This article demonstrates continuous reading and bookmarking.\n\n{}", "Scroll to read the complete preview article. The live reader opens the original publisher page, retaining its attribution.\n\n".repeat(12)),source:"Preview Journal".into(),url:None,timestamp:1789574400-i as i64*1800,market:if i==4 {"HK"}else if i==5 {"CN"}else{"US"}.into(),language:if i>=4{"cn"}else{"en"}.into(),securities:vec![self.catalog[if i==4{2}else if i==5{4}else{0}].id.clone()]});
        }
    }
    pub fn security(&self) -> &Security {
        self.catalog
            .iter()
            .find(|s| s.id == self.selected)
            .unwrap_or(&self.catalog[0])
    }
    pub fn points(&self) -> &[Point] {
        self.history
            .get(&format!("{}:{}", self.selected, self.range))
            .map(Vec::as_slice)
            .unwrap_or(&[])
    }
    pub fn visible_securities(&self, search: bool) -> Vec<&Security> {
        let q = self.query.trim().to_lowercase();
        let matches = |s: &&Security| {
            (self.region == "All" || s.market == self.region)
                && (q.is_empty()
                    || [
                        s.symbol.as_str(),
                        s.name.as_str(),
                        s.chinese.as_str(),
                        s.id.as_str(),
                    ]
                    .iter()
                    .any(|v| v.to_lowercase().contains(&q)))
        };
        if search {
            self.catalog.iter().filter(matches).collect()
        } else {
            self.prefs
                .watchlist
                .iter()
                .filter_map(|id| self.catalog.iter().find(|s| &s.id == id))
                .filter(matches)
                .collect()
        }
    }
    pub fn stories(&self) -> Vec<&Story> {
        let mut seen = BTreeSet::new();
        let iter: Vec<&Story> = if self.screen == "saved" {
            self.prefs.saved.values().collect()
        } else {
            self.news.iter().collect()
        };
        let mut out: Vec<_> = iter
            .into_iter()
            .filter(|n| {
                (self.region == "All" || n.market == self.region)
                    && (self.screen != "company_news" || n.securities.contains(&self.selected))
                    && seen.insert(n.url.as_deref().unwrap_or(&n.id))
            })
            .collect();
        out.sort_by_key(|n| std::cmp::Reverse(n.timestamp));
        out
    }
    /// Returns true if persistent user preferences changed. Credentials are never part of this state.
    pub fn act(&mut self, event: &str, payload: &Value) -> bool {
        let v = payload["value"].as_str().unwrap_or("");
        match event {
            "navigate" => {
                self.screen = v.into();
                self.inspection = None;
                self.query.clear();
            }
            "region" => self.region = v.into(),
            "search" => self.query = v.into(),
            "open" => {
                if self.catalog.iter().any(|s| s.id == v) {
                    self.selected = v.into();
                    self.screen = "detail".into();
                    self.range = "1D".into();
                    self.inspection = None;
                }
            }
            "range" => {
                if ["1D", "1W", "1M", "6M", "1Y"].contains(&v) {
                    self.range = v.into();
                    self.inspection = None;
                }
            }
            "follow" => {
                if self.catalog.iter().any(|s| s.id == v) {
                    if self.prefs.watchlist.iter().any(|id| id == v) {
                        self.prefs.watchlist.retain(|id| id != v);
                    } else {
                        self.prefs.watchlist.push(v.into());
                    }
                    return true;
                }
            }
            "move_up" => {
                if let Some(i) = self.prefs.watchlist.iter().position(|id| id == v) {
                    if i > 0 {
                        self.prefs.watchlist.swap(i, i - 1);
                        return true;
                    }
                }
            }
            "article" => {
                self.article = v.into();
                self.screen = "reader".into();
            }
            "save" => {
                if self.prefs.saved.remove(v).is_none() {
                    if let Some(n) = self.news.iter().find(|n| n.id == v) {
                        self.prefs.saved.insert(v.into(), n.clone());
                    }
                }
                return true;
            }
            "preview" => {
                self.prefs.preview = !self.prefs.preview;
                self.quotes.clear();
                self.history.clear();
                self.news.clear();
                self.errors.clear();
                if self.prefs.preview {
                    self.load_preview();
                }
                return true;
            }
            "language" => {
                self.prefs.language = if self.prefs.language == "cn" {
                    "en"
                } else {
                    "cn"
                }
                .into();
                return true;
            }
            "theme" => {
                self.prefs.light = !self.prefs.light;
                return true;
            }
            "colors" => {
                self.prefs.red_up = !self.prefs.red_up;
                return true;
            }
            "load_more" => self.news_limit += 24,
            _ => {}
        }
        false
    }
    pub fn evidence(&self) -> Value {
        json!({"screen":self.screen,"selected":self.selected,"range":self.range,"preview":self.prefs.preview,"point_count":self.points().len(),"points":self.points(),"inspection":self.inspection,"watchlist":self.prefs.watchlist,"saved":self.prefs.saved.keys().collect::<Vec<_>>(),"errors":self.errors})
    }
}

pub fn timestamp_text(time: i64) -> String {
    chrono::DateTime::from_timestamp(time, 0)
        .map(|d| d.format("%Y-%m-%d %H:%M UTC").to_string())
        .unwrap_or_else(|| "Unknown time".into())
}

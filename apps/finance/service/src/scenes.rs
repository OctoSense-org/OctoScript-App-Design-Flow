//! One scene author feeds both the image pipeline and the native runtime.
use crate::model::*;
use base64::{engine::general_purpose::STANDARD, Engine};
use serde_json::{json, Value};

pub struct Scene {
    pub tree: Value,
    pub controls: Value,
    pub plots: Value,
    pub web_url: Option<String>,
}
impl Scene {
    /// Keep the 406-unit typography and row widths while adapting the scrolling
    /// viewport and bottom navigation to the space supplied by a mobile host.
    pub fn fit_height(&mut self, height: f64) {
        fn move_y(node: &mut Value, delta: f64) {
            if let Some(y) = node["y"].as_f64() {
                node["y"] = (y + delta).into();
            }
            if let Some(children) = node["c"].as_array_mut() {
                for child in children {
                    move_y(child, delta);
                }
            }
        }
        let height = height.max(300.);
        let delta = height - 776.;
        self.tree["h"] = height.into();
        self.tree["radius"] = 0.into();
        if let Some(children) = self.tree["c"].as_array_mut() {
            for node in children {
                let id = node["id"].as_str().unwrap_or("").to_owned();
                if id == "body_scroll" {
                    node["h"] = (580. + delta).max(80.).into();
                } else if id == "article_web" {
                    node["h"] = (height - 242.).max(58.).into();
                } else if id == "share" {
                    move_y(node, height - 118. - 695.);
                } else if (id.starts_with("tab_") && id != "tab_settings") || id == "home_indicator"
                {
                    move_y(node, delta);
                }
            }
        }
    }
}
struct Author<'a> {
    s: &'a State,
    n: Vec<Value>,
    controls: Value,
    plots: Value,
    bg: u32,
    surface: u32,
    ink: u32,
    muted: u32,
    blue: u32,
    up: u32,
    down: u32,
}
fn color(s: &str) -> u32 {
    u32::from_str_radix(s, 16).unwrap() | 0xff000000
}
fn stack(id: &str, x: f64, y: f64, w: f64, h: f64, bg: Option<u32>, c: Vec<Value>) -> Value {
    let mut n = json!({"t":"stack","id":id,"x":x,"y":y,"w":w,"h":h,"c":c});
    if let Some(bg) = bg {
        n["bg"] = bg.into();
        n["variant"] = "surface".into();
        n["radius"] = 12.into();
    }
    n
}
impl<'a> Author<'a> {
    fn group(&mut self, id: &str, x: f64, y: f64, w: f64, h: f64, start: usize) {
        let children = self.n.split_off(start);
        self.n.push(stack(id, x, y, w, h, Some(self.bg), children));
    }
    fn label(
        &self,
        id: &str,
        text: impl Into<String>,
        x: f64,
        y: f64,
        w: f64,
        size: f64,
        ink: u32,
    ) -> Value {
        json!({"t":"text","id":id,"text":text.into(),"x":x,"y":y,"w":w,"h":size*1.36,"size":size,"line_height":size*1.36,"weight":400,"font_src":"self:resources/ux/Inter-400.ttf","color":ink,"variant":"single_line"})
    }
    fn text(
        &mut self,
        id: &str,
        text: impl Into<String>,
        x: f64,
        y: f64,
        w: f64,
        size: f64,
        ink: u32,
    ) {
        let n = self.label(id, text, x, y, w, size, ink);
        self.n.push(n);
    }
    fn icon(&mut self, id: &str, glyph: &str, x: f64, y: f64, size: f64, ink: u32) {
        let mut n = self.label(id, glyph, x, y, size + 4., size, ink);
        n["font_src"] = "makepad_widgets:resources/fa-solid-900.ttf".into();
        n["weight"] = 900.into();
        n["alignx"] = 0.5.into();
        self.n.push(n);
    }
    fn button(
        &mut self,
        id: &str,
        label: &str,
        x: f64,
        y: f64,
        w: f64,
        h: f64,
        event: &str,
        value: &str,
        filled: bool,
    ) {
        let is_tab = id.starts_with("tab_") && id != "tab_settings";
        let segment = id.starts_with("region_") || id.starts_with("range_");
        let selected = if id.starts_with("range_") {
            self.s.range == value
        } else {
            filled
        };
        let search = id == "search_open";
        let ink = if search {
            self.muted
        } else if segment {
            if selected {
                self.ink
            } else {
                self.muted
            }
        } else if is_tab && !filled {
            self.muted
        } else {
            self.blue
        };
        let mut children = vec![
            json!({"t":"button","id":format!("{id}_control"),"x":x,"y":y,"w":w,"h":h,"enabled":true}),
        ];
        if !is_tab && (filled || segment) {
            let mut bg = stack(
                &format!("{id}_bg"),
                x,
                y,
                w,
                h,
                Some(if segment && selected {
                    self.blue
                } else {
                    self.surface
                }),
                vec![],
            );
            bg["radius"] = 7.into();
            children.push(bg);
        }
        let mut t = self.label(
            &format!("{id}_label"),
            label.trim_start_matches("• "),
            if search { x + 36. } else { x + 4. },
            if is_tab {
                y + h - 17.
            } else {
                y + (h - 18.) / 2.
            },
            if search { w - 46. } else { w - 8. },
            if is_tab { 9. } else { 13. },
            ink,
        );
        t["alignx"] = if search { 0. } else { 0.5 }.into();
        children.push(t);
        let mut n = stack(id, x, y, w, h, None, children);
        n["kit"] = json!({"widget":"KitButton","bindings":{"control":[0]}})
            .to_string()
            .into();
        self.n.push(n);
        self.controls[id] = json!({"event":event,"value":value});
        if search {
            self.icon("search_glyph", "\u{f002}", x + 12., y + 9., 14., self.muted);
        }
        if is_tab {
            let glyph = match value {
                "watchlist" => "\u{f00a}",
                "markets" => "\u{f080}",
                "news" => "\u{f1ea}",
                _ => "\u{f02e}",
            };
            self.icon(
                &format!("{id}_glyph"),
                glyph,
                x + (w - 23.) / 2.,
                y + 5.,
                19.,
                ink,
            );
        }
    }
    fn field(
        &mut self,
        id: &str,
        value: &str,
        placeholder: &str,
        y: f64,
        event: &str,
        password: bool,
    ) {
        self.n.push(stack(
            &format!("{id}_bg"),
            20.,
            y,
            366.,
            42.,
            Some(self.surface),
            vec![],
        ));
        let mut input = self.label(
            &format!("{id}_input"),
            value,
            34.,
            y + 10.,
            338.,
            16.,
            self.ink,
        );
        input["t"] = "input".into();
        input["placeholder"] = placeholder.into();
        input["password"] = (if password { 1 } else { 0 }).into();
        let mut n = stack(id, 30., y + 2., 346., 38., None, vec![input]);
        n["kit"] = json!({"widget":"KitFormField","bindings":{"input":[0]}})
            .to_string()
            .into();
        self.n.push(n);
        self.controls[id] = json!({"event":event,"value":id});
    }
    fn tr(&self, en: &str, cn: &str) -> String {
        if self.s.prefs.language == "cn" {
            cn
        } else {
            en
        }
        .into()
    }
    fn regions(&mut self, y: f64) {
        for (i, r) in ["All", "US", "HK", "CN"].iter().enumerate() {
            self.button(
                &format!("region_{i}"),
                r,
                20. + i as f64 * 93.,
                y,
                90.,
                28.,
                "region",
                r,
                self.s.region == *r,
            );
        }
    }
    fn row(&mut self, sec: &Security, i: usize, y: f64, editing: bool, search: bool) {
        let id = format!("stock_{i}");
        self.button(&id, "", 20., y, 366., 58., "open", &sec.id, false);
        let mut symbol = self.label(
            &format!("{id}_symbol"),
            &sec.symbol,
            24.,
            y + 7.,
            112.,
            16.,
            self.ink,
        );
        symbol["font_src"] = "self:resources/ux/Inter-600.ttf".into();
        symbol["weight"] = 600.into();
        self.n.push(symbol);
        self.text(
            &format!("{id}_name"),
            if sec.market == "US" && self.s.prefs.language != "cn" {
                &sec.name
            } else {
                &sec.chinese
            },
            24.,
            y + 31.,
            132.,
            11.,
            self.muted,
        );
        let mut badge = stack(
            &format!("{id}_badge"),
            139.,
            y + 18.,
            29.,
            21.,
            Some(self.surface),
            vec![],
        );
        badge["radius"] = 4.into();
        self.n.push(badge);
        let mut market = self.label(
            &format!("{id}_market"),
            &sec.market,
            140.,
            y + 22.,
            27.,
            8.,
            self.muted,
        );
        market["alignx"] = 0.5.into();
        self.n.push(market);
        if editing {
            self.button(
                &format!("remove_{i}"),
                "−",
                278.,
                y + 10.,
                40.,
                36.,
                "follow",
                &sec.id,
                true,
            );
            self.button(
                &format!("up_{i}"),
                "↑",
                332.,
                y + 10.,
                40.,
                36.,
                "move_up",
                &sec.id,
                false,
            );
        } else if search {
            self.button(
                &format!("add_{i}"),
                if self.s.prefs.watchlist.contains(&sec.id) {
                    "−"
                } else {
                    "+"
                },
                334.,
                y + 11.,
                36.,
                36.,
                "follow",
                &sec.id,
                true,
            );
        } else if let Some(q) = self.s.quotes.get(&sec.id) {
            let pct = q.change_pct();
            let ink = if pct.unwrap_or(0.) >= 0. {
                self.up
            } else {
                self.down
            };
            let mut price = self.label(
                &format!("{id}_price"),
                format!("{:.2}", q.price),
                274.,
                y + 7.,
                102.,
                16.,
                self.ink,
            );
            price["alignx"] = 1.into();
            price["font_src"] = "self:resources/ux/Inter-600.ttf".into();
            price["weight"] = 600.into();
            self.n.push(price);
            let mut change = self.label(
                &format!("{id}_change"),
                pct.map(|p| format!("{p:+.2}%")).unwrap_or("—".into()),
                284.,
                y + 31.,
                92.,
                12.,
                ink,
            );
            change["alignx"] = 1.into();
            self.n.push(change);
        } else {
            self.text(
                &format!("{id}_missing"),
                "—",
                335.,
                y + 13.,
                40.,
                20.,
                self.muted,
            );
        }
        if !editing && !search {
            let points = self
                .s
                .history
                .get(&format!("{}:1D", sec.id))
                .map(Vec::as_slice)
                .unwrap_or(&[]);
            self.plot(
                &format!("spark_{i}"),
                181.,
                y + 17.,
                82.,
                25.,
                points,
                self.up,
                sec,
                "1D",
            );
        }
        self.n.push(stack(
            &format!("{id}_rule"),
            24.,
            y + 58.,
            356.,
            0.5,
            Some(self.surface),
            vec![],
        ));
    }
    fn plot(
        &mut self,
        id: &str,
        x: f64,
        y: f64,
        w: f64,
        h: f64,
        p: &[Point],
        ink: u32,
        security: &Security,
        range: &str,
    ) {
        if self.s.prefs.preview && p.len() < 2 {
            return;
        }
        self.n
            .push(json!({"t":"stockplot","id":id,"x":x,"y":y,"w":w,"h":h}));
        self.plots[id] = json!({"points":p,"color":ink,"security":security.id,"symbol":security.yahoo_symbol().unwrap_or_default(),"range":range});
    }
    fn story(&mut self, story: &Story, i: usize, y: f64) {
        let id = format!("story_{i}");
        self.button(&id, "", 20., y, 366., 105., "article", &story.id, false);
        self.text(
            &format!("{id}_source"),
            format!("{} · {}", story.source, story.market),
            24.,
            y + 8.,
            342.,
            11.,
            self.muted,
        );
        for (j, line) in wrap(&story.title, 34).iter().take(2).enumerate() {
            self.text(
                &format!("{id}_title_{j}"),
                line,
                24.,
                y + 31. + j as f64 * 24.,
                300.,
                16.,
                self.ink,
            );
        }
        self.button(
            &format!("save_{i}"),
            if self.s.prefs.saved.contains_key(&story.id) {
                "★"
            } else {
                "☆"
            },
            338.,
            y + 41.,
            42.,
            40.,
            "save",
            &story.id,
            false,
        );
        self.n.push(stack(
            &format!("{id}_rule"),
            24.,
            y + 103.,
            356.,
            0.5,
            Some(self.surface),
            vec![],
        ));
    }
}
pub fn wrap(text: &str, max: usize) -> Vec<String> {
    let mut lines = vec![];
    for p in text.split('\n') {
        let mut line = String::new();
        let mut count = 0;
        for word in p.split_whitespace() {
            let n = word.chars().count();
            if count + n + 1 > max && !line.is_empty() {
                lines.push(std::mem::take(&mut line));
                count = 0;
            }
            if count > 0 {
                line.push(' ');
                count += 1;
            }
            line.push_str(word);
            count += n;
        }
        lines.push(line);
    }
    lines
}
fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}
pub fn build(s: &State) -> Scene {
    let (bg, surface, ink, muted) = if s.prefs.light {
        ("F4F6F9", "E4E8EF", "10141C", "586273")
    } else {
        ("07090C", "14181F", "F4F5F7", "929AA8")
    };
    let mut a = Author {
        s,
        n: vec![],
        controls: json!({}),
        plots: json!({}),
        bg: color(bg),
        surface: color(surface),
        ink: color(ink),
        muted: color(muted),
        blue: color("0A84FF"),
        up: color(if s.prefs.red_up { "FF5965" } else { "28C78A" }),
        down: color(if s.prefs.red_up { "28C78A" } else { "FF5965" }),
    };
    let screen = s.screen.as_str();
    let title = match screen {
        "markets" => a.tr("Markets", "市场"),
        "search" => a.tr("Search", "搜索"),
        "edit" => a.tr("Edit Watchlist", "编辑自选"),
        "detail" | "company_news" => s.security().symbol.clone(),
        "news" => a.tr("Business News", "商业新闻"),
        "saved" => a.tr("Saved News", "收藏新闻"),
        "settings" => a.tr("Settings", "设置"),
        "reader" => a.tr("Article", "文章"),
        _ => a.tr("Stocks", "股票"),
    };
    a.text("heading", title, 20., 30., 316., 30., a.ink);
    if let Some(n) = a.n.last_mut() {
        n["font_src"] = "self:resources/ux/Inter-700.ttf".into();
        n["weight"] = 700.into();
    }
    a.text(
        "data_status",
        if s.prefs.preview {
            a.tr(
                "Preview · Fictional prices & news",
                "预览数据 · 虚构价格和新闻",
            )
        } else {
            a.tr(
                "Market data · Refresh for latest quotes",
                "供应商数据 · 刷新获取最新报价",
            )
        },
        24.,
        75.,
        354.,
        10.,
        a.muted,
    );
    if ["detail", "reader", "company_news", "edit"].contains(&screen) {
        a.button(
            "back",
            "‹",
            8.,
            3.,
            48.,
            36.,
            "navigate",
            if screen == "reader" {
                "news"
            } else {
                "watchlist"
            },
            false,
        );
    }
    if screen == "watchlist" {
        a.button(
            "edit", "···", 310., 27., 40., 40., "navigate", "edit", false,
        );
    }
    if screen == "edit" {
        a.button(
            "done",
            "Done",
            316.,
            40.,
            74.,
            42.,
            "navigate",
            "watchlist",
            false,
        );
    }
    if !["reader", "edit"].contains(&screen) {
        a.button(
            "tab_settings",
            "",
            358.,
            28.,
            36.,
            36.,
            "navigate",
            "settings",
            false,
        );
        a.icon("settings_glyph", "\u{f013}", 365., 36., 18., a.blue);
    }
    let chrome = a.n.len();
    let mut bottom = 640.;
    let mut web_url = None;
    match screen {
        "watchlist" | "search" | "edit" => {
            if screen == "search" {
                a.field(
                    "search",
                    &s.query,
                    &a.tr(
                        "Symbol or company · Apple / 腾讯",
                        "代码或公司 · Apple / 腾讯",
                    ),
                    112.,
                    "search",
                    false,
                );
            } else {
                a.button(
                    "search_open",
                    &a.tr("Search symbols or companies", "搜索代码或公司"),
                    20.,
                    112.,
                    366.,
                    36.,
                    "navigate",
                    "search",
                    true,
                );
            }
            a.regions(158.);
            if screen == "search" {
                a.text(
                    "directory_scope",
                    a.tr(
                        "Public directory · access depends on your plan",
                        "公开股票目录 · 行情权限取决于订阅",
                    ),
                    24.,
                    198.,
                    354.,
                    11.,
                    a.muted,
                );
            }
            let rows = s.visible_securities(screen == "search");
            let start = if screen == "search" { 226. } else { 196. };
            let group_start = a.n.len();
            for (i, sec) in rows.iter().enumerate().skip(s.list_start).take(24) {
                a.row(
                    sec,
                    i,
                    start + i as f64 * 62.,
                    screen == "edit",
                    screen == "search",
                );
                if i == 1 && s.list_start == 0 && screen == "watchlist" {
                    a.group("watchlist_card", 20., start, 366., 124., group_start);
                }
            }
            if screen == "watchlist" && s.list_start == 0 && rows.len() < 2 {
                if rows.is_empty() {
                    a.text(
                        "card_empty_watchlist",
                        "No followed stocks",
                        24.,
                        start + 8.,
                        352.,
                        17.,
                        a.muted,
                    );
                }
                a.group("watchlist_card", 20., start, 366., 124., group_start);
            }
            bottom = start + rows.len() as f64 * 62. + 30.;
            if rows.is_empty() {
                a.text(
                    "empty",
                    a.tr("No matching stocks", "暂无匹配股票"),
                    24.,
                    295.,
                    352.,
                    20.,
                    a.muted,
                );
            }
            if screen == "watchlist" {
                a.text(
                    "home_news_heading",
                    a.tr("Business News", "商业新闻"),
                    24.,
                    bottom - 12.,
                    270.,
                    20.,
                    a.ink,
                );
                a.button(
                    "home_news_all",
                    "See all",
                    306.,
                    bottom - 18.,
                    74.,
                    36.,
                    "navigate",
                    "news",
                    false,
                );
                if let Some(story) = s.news.first() {
                    a.story(story, 0, bottom + 20.);
                }
                bottom += 136.;
                a.button(
                    "refresh",
                    "Refresh quotes",
                    20.,
                    bottom,
                    366.,
                    42.,
                    "refresh",
                    "",
                    true,
                );
                bottom += 60.;
            }
        }
        "markets" => {
            a.regions(123.);
            a.text(
                "market_scope",
                a.tr(
                    "Tracked stocks · not a whole-market ranking",
                    "已关注股票 · 非全市场排行榜",
                ),
                24.,
                172.,
                356.,
                11.,
                a.muted,
            );
            let market_start = a.n.len();
            for (i, (name, sub)) in [
                ("US", "NASDAQ / NYSE · USD · New York"),
                ("Hong Kong", "HKEX · HKD · Hong Kong"),
                ("Mainland China", "SSE / SZSE · CNY · Shanghai"),
            ]
            .iter()
            .enumerate()
            {
                let y = 204. + i as f64 * 108.;
                a.n.push(stack(
                    &format!("market_{i}"),
                    20.,
                    y,
                    366.,
                    92.,
                    Some(a.surface),
                    vec![],
                ));
                a.text(
                    &format!("market_{i}_name"),
                    *name,
                    36.,
                    y + 14.,
                    330.,
                    20.,
                    a.ink,
                );
                a.text(
                    &format!("market_{i}_sub"),
                    *sub,
                    36.,
                    y + 47.,
                    330.,
                    12.,
                    a.muted,
                );
                a.text(
                    &format!("market_{i}_session"),
                    if s.prefs.preview {
                        "Session unavailable in preview"
                    } else {
                        "See quote observation time"
                    },
                    36.,
                    y + 66.,
                    330.,
                    10.,
                    a.muted,
                );
            }
            a.group("market_brief_card", 20., 204., 366., 308., market_start);
            a.text(
                "movers_title",
                "Watchlist movers",
                24.,
                550.,
                354.,
                22.,
                a.ink,
            );
            let mut rows = s.visible_securities(false);
            rows.sort_by(|a, b| {
                let p = |x: &Security| {
                    s.quotes
                        .get(&x.id)
                        .and_then(Quote::change_pct)
                        .unwrap_or(f64::NEG_INFINITY)
                };
                p(b).total_cmp(&p(a))
            });
            for (i, sec) in rows.iter().enumerate().skip(s.list_start).take(24) {
                a.row(sec, i, 590. + i as f64 * 62., false, false);
            }
            bottom = 610. + rows.len() as f64 * 62.;
        }
        "detail" => {
            let quote_start = a.n.len();
            let sec = s.security();
            a.text(
                "company",
                format!(
                    "{} · {} · {}",
                    if s.prefs.language == "cn" {
                        &sec.chinese
                    } else {
                        &sec.name
                    },
                    sec.exchange,
                    sec.currency
                ),
                24.,
                120.,
                352.,
                15.,
                a.muted,
            );
            let q = s.quotes.get(&sec.id);
            a.text(
                "last_price",
                q.map(|q| format!("{:.2}", q.price)).unwrap_or("—".into()),
                24.,
                151.,
                280.,
                34.,
                a.ink,
            );
            a.text(
                "day_change",
                q.and_then(Quote::change_pct)
                    .map(|p| format!("{p:+.2}% today"))
                    .unwrap_or("Day change unavailable".into()),
                26.,
                210.,
                350.,
                17.,
                if q.and_then(Quote::change_pct).unwrap_or(0.) >= 0. {
                    a.up
                } else {
                    a.down
                },
            );
            a.button(
                "follow",
                if s.prefs.watchlist.contains(&sec.id) {
                    "Following"
                } else {
                    "Follow"
                },
                280.,
                161.,
                102.,
                38.,
                "follow",
                &sec.id,
                true,
            );
            a.group("quote_card", 20., 116., 366., 129., quote_start);
            let p = s.points();
            a.plot(
                "price_chart",
                24.,
                281.,
                354.,
                186.,
                p,
                if p.last()
                    .zip(p.first())
                    .is_some_and(|(last, first)| last.price < first.price)
                {
                    a.down
                } else {
                    a.up
                },
                sec,
                &s.range,
            );
            // StockPlot owns every axis, gridline and time label, as in the
            // A2App stock card. Only the range return belongs to this scene.
            let range_return = p
                .first()
                .zip(p.last())
                .filter(|(first, _)| first.price > 0.)
                .map(|(first, last)| {
                    format!(
                        "{}  {:+.2}%",
                        s.range,
                        (last.price / first.price - 1.) * 100.
                    )
                })
                .unwrap_or_else(|| format!("{}  —", s.range));
            a.text("range_return", range_return, 24., 502., 354., 12., a.muted);
            for (i, r) in ["1D", "1W", "1M", "6M", "1Y"].iter().enumerate() {
                a.button(
                    &format!("range_{i}"),
                    &if s.range == *r {
                        format!("• {r}")
                    } else {
                        r.to_string()
                    },
                    20. + i as f64 * 74.,
                    235.,
                    68.,
                    34.,
                    "range",
                    r,
                    true,
                );
            }
            a.text(
                "inspection",
                s.inspection
                    .and_then(|i| p.get(i))
                    .map(|p| {
                        format!(
                            "{} · {:.2} {}",
                            chrono::DateTime::from_timestamp(p.time, 0)
                                .map(|d| d.format("%Y-%m-%d %H:%M UTC").to_string())
                                .unwrap_or_default(),
                            p.price,
                            sec.currency
                        )
                    })
                    .unwrap_or("Drag chart to inspect a price".into()),
                24.,
                543.,
                356.,
                11.,
                a.muted,
            );
            let vals = [
                ("Open", q.and_then(|q| q.open)),
                ("Previous close", q.and_then(|q| q.previous_close)),
                ("High", q.and_then(|q| q.high)),
                ("Low", q.and_then(|q| q.low)),
            ];
            for (i, (label, v)) in vals.iter().enumerate() {
                let x = 24. + (i % 2) as f64 * 186.;
                let y = 580. + (i / 2) as f64 * 66.;
                a.text(&format!("stat_{i}_label"), *label, x, y, 170., 12., a.muted);
                a.text(
                    &format!("stat_{i}_value"),
                    v.map(|v| format!("{v:.2}")).unwrap_or("—".into()),
                    x,
                    y + 22.,
                    170.,
                    18.,
                    a.ink,
                );
            }
            if let Some(q) = q {
                a.text(
                    "quote_source",
                    format!("{} · {}", q.source, q.delay),
                    24.,
                    727.,
                    356.,
                    10.,
                    a.muted,
                );
                a.text(
                    "quote_time",
                    format!(
                        "Observed {} UTC",
                        chrono::DateTime::from_timestamp(q.timestamp, 0)
                            .map(|d| d.format("%Y-%m-%d %H:%M").to_string())
                            .unwrap_or_default()
                    ),
                    24.,
                    745.,
                    356.,
                    10.,
                    a.muted,
                );
            }
            a.button(
                "company_news",
                "Company news  ›",
                20.,
                780.,
                366.,
                44.,
                "navigate",
                "company_news",
                true,
            );
            a.button(
                "detail_refresh",
                "Refresh",
                20.,
                834.,
                366.,
                44.,
                "refresh",
                "",
                true,
            );
            bottom = 899.;
        }
        "news" | "company_news" | "saved" => {
            a.regions(122.);
            let stories = s.stories();
            let news_start = a.n.len();
            for (i, story) in stories.iter().enumerate().skip(s.list_start).take(24) {
                a.story(story, i, 178. + i as f64 * 108.);
                if i == 1 && s.list_start == 0 {
                    a.group("related_news_card", 20., 178., 366., 216., news_start);
                }
            }
            if s.list_start == 0 && stories.len() < 2 {
                if stories.is_empty() {
                    a.text(
                        "card_empty_news",
                        "No related news available",
                        24.,
                        186.,
                        352.,
                        17.,
                        a.muted,
                    );
                }
                a.group("related_news_card", 20., 178., 366., 216., news_start);
            }
            bottom = 190. + stories.len() as f64 * 108.;
            if stories.is_empty() {
                a.text(
                    "empty_news",
                    a.tr("No articles here yet", "暂无文章"),
                    24.,
                    250.,
                    354.,
                    22.,
                    a.muted,
                );
                a.text(
                    "empty_news_hint",
                    a.tr(
                        "Save a story or refresh your news sources.",
                        "收藏文章或刷新新闻来源。",
                    ),
                    24.,
                    290.,
                    354.,
                    13.,
                    a.muted,
                );
            }
            a.button(
                "news_refresh",
                "Refresh news",
                20.,
                bottom.max(370.),
                366.,
                44.,
                "refresh",
                "",
                true,
            );
            bottom = bottom.max(370.) + 65.;
        }
        "reader" => {
            if let Some(n) = s
                .news
                .iter()
                .find(|n| n.id == s.article)
                .or_else(|| s.prefs.saved.get(&s.article))
            {
                a.button(
                    "bookmark",
                    if s.prefs.saved.contains_key(&n.id) {
                        "Saved ★"
                    } else {
                        "Save ☆"
                    },
                    280.,
                    40.,
                    104.,
                    42.,
                    "save",
                    &n.id,
                    false,
                );
                let html=format!("<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{background:#{bg};color:#{ink};font:18px -apple-system,sans-serif;padding:18px;line-height:1.65}}h1{{font-size:29px}}small{{color:#{muted}}}a{{color:#458fff}}</style></head><body><small>{}</small><h1>{}</h1>{}</body></html>",html_escape(&n.source),html_escape(&n.title),n.summary.split("\n\n").map(|p|format!("<p>{}</p>",html_escape(p))).collect::<String>());
                let url = format!(
                    "data:text/html;charset=utf-8;base64,{}",
                    STANDARD.encode(html)
                );
                web_url = n.url.clone().or(Some(url.clone()));
                a.n.push(
                    json!({"t":"web","id":"article_web","x":0,"y":116,"w":406,"h":578,"src":url}),
                );
                a.button(
                    "share",
                    "Copy link",
                    20.,
                    695.,
                    160.,
                    38.,
                    "share",
                    "",
                    true,
                );
            }
        }
        "settings" => {
            let items = [
                (
                    "preview",
                    a.tr("Preview data", "预览数据"),
                    if s.prefs.preview { "On" } else { "Off" }.to_owned(),
                ),
                (
                    "theme",
                    a.tr("Appearance", "外观"),
                    if s.prefs.light { "Light" } else { "Dark" }.into(),
                ),
                (
                    "language",
                    a.tr("Language", "语言"),
                    if s.prefs.language == "cn" {
                        "中文"
                    } else {
                        "English"
                    }
                    .into(),
                ),
                (
                    "colors",
                    a.tr("Rising prices", "上涨颜色"),
                    if s.prefs.red_up { "Red" } else { "Green" }.into(),
                ),
            ];
            for (i, (id, label, value)) in items.iter().enumerate() {
                let y = 125. + i as f64 * 58.;
                a.button(id, "", 20., y, 366., 50., id, "", true);
                a.text(&format!("{id}_name"), label, 36., y + 15., 218., 15., a.ink);
                a.text(
                    &format!("{id}_value"),
                    value,
                    266.,
                    y + 15.,
                    108.,
                    14.,
                    a.blue,
                );
            }
            a.text(
                "providers_title",
                "Data sources",
                24.,
                380.,
                354.,
                23.,
                a.ink,
            );
            a.text(
                "provider_note",
                "Keys stay in memory for this session",
                24.,
                413.,
                354.,
                11.,
                a.muted,
            );
            for (i, (id, title)) in [
                ("alltick", "AllTick · optional market provider"),
                ("finnhub", "Finnhub · English news"),
                ("tushare", "Tushare · Chinese news"),
            ]
            .iter()
            .enumerate()
            {
                let y = 445. + i as f64 * 99.;
                a.text(&format!("{id}_title"), *title, 24., y, 352., 14., a.ink);
                a.field(id, "", "Enter API key", y + 27., "credential", true);
            }
            a.button(
                "provider_refresh",
                "Connect & refresh",
                20.,
                757.,
                366.,
                44.,
                "refresh",
                "",
                true,
            );
            a.text(
                "coverage_note",
                "Access and history depend on your subscription.",
                24.,
                819.,
                356.,
                11.,
                a.muted,
            );
            a.text(
                "sources_note",
                "StockPlot: Yahoo · optional AllTick / news providers",
                24.,
                842.,
                356.,
                10.,
                a.muted,
            );
            bottom = 885.;
        }
        _ => {}
    }
    if screen != "reader" {
        for (i, (kind, error)) in s.errors.iter().enumerate() {
            a.text(
                &format!("error_{i}"),
                format!("{kind}: {error}"),
                24.,
                bottom + i as f64 * 27.,
                355.,
                11.,
                a.down,
            );
        }
        bottom += s.errors.len() as f64 * 27.;
        let body = a.n.split_off(chrome);
        let content = stack(
            "body_content",
            0.,
            112.,
            406.,
            (bottom - 112.).max(570.),
            None,
            body,
        );
        let mut scroll = stack("body_scroll", 0., 112., 406., 580., None, vec![content]);
        scroll["variant"] = "scroll_y".into();
        a.n.push(scroll);
    }
    a.n.push(stack(
        "tab_surface",
        0.,
        704.,
        406.,
        72.,
        Some(a.bg),
        vec![],
    ));
    for (i, (page, en, cn)) in [
        ("watchlist", "Stocks", "自选"),
        ("markets", "Markets", "市场"),
        ("news", "News", "新闻"),
        ("saved", "Saved", "收藏"),
    ]
    .iter()
    .enumerate()
    {
        let label = a.tr(en, cn);
        a.button(
            &format!("tab_{page}"),
            &label,
            2. + i as f64 * 101.,
            707.,
            99.,
            54.,
            "navigate",
            page,
            screen == *page,
        );
    }
    a.n.push(stack(
        "home_indicator",
        145.,
        765.,
        116.,
        4.,
        Some(a.muted),
        vec![],
    ));
    Scene {
        tree: stack("page", 0., 0., 406., 776., Some(a.bg), a.n),
        controls: a.controls,
        plots: a.plots,
        web_url,
    }
}

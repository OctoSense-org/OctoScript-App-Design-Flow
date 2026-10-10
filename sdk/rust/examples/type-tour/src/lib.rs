//! Every type `#[octosense_component::export]` maps, both ways: what the
//! end-to-end tests call. Not an example to copy; see markdown-tools.

#[octosense_component::export]
pub mod tour {
    pub struct Point {
        pub x: i32,
        pub y: i32,
        pub label: Option<String>,
    }

    pub enum Unit {
        Metric,
        Imperial,
    }

    pub enum Shape {
        Circle(f64),
        Rect(Point),
        Nothing,
    }

    // A private static: the instance's state, kept from one call to the next.
    static TOTAL: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

    /// Adds to a running total that lives as long as the instance.
    pub fn tally(n: u64) -> u64 {
        TOTAL.fetch_add(n, std::sync::atomic::Ordering::Relaxed) + n
    }

    /// Random numbers, from WASI through an ordinary crate.
    pub fn random_u64() -> Result<u64, String> {
        getrandom::u64().map_err(|e| e.to_string())
    }

    pub fn mirror(p: Point) -> Point {
        Point {
            x: -p.x,
            y: -p.y,
            label: p.label.map(|l| l.chars().rev().collect()),
        }
    }

    pub fn area(shape: Shape) -> f64 {
        match shape {
            Shape::Circle(r) => std::f64::consts::PI * r * r,
            Shape::Rect(p) => (p.x * p.y).abs() as f64,
            Shape::Nothing => 0.0,
        }
    }

    pub fn grow(shape: Shape) -> Shape {
        match shape {
            Shape::Circle(r) => Shape::Circle(r * 2.0),
            Shape::Rect(p) => Shape::Rect(Point {
                x: p.x * 2,
                y: p.y * 2,
                label: p.label,
            }),
            Shape::Nothing => Shape::Nothing,
        }
    }

    pub fn convert(value: f64, to: Unit) -> f64 {
        match to {
            Unit::Metric => value * 2.54,
            Unit::Imperial => value / 2.54,
        }
    }

    pub fn checksum(data: &[u8]) -> (u32, u64) {
        (data.len() as u32, data.iter().map(|b| *b as u64).sum())
    }

    pub fn reverse_bytes(data: Vec<u8>) -> Vec<u8> {
        data.into_iter().rev().collect()
    }

    pub fn first_word(text: &str) -> Option<String> {
        text.split_whitespace().next().map(str::to_string)
    }

    pub fn check(ok: bool) -> Result<(), String> {
        if ok {
            Ok(())
        } else {
            Err("not ok".into())
        }
    }

    pub fn widen(small: u8, signed: i8, ch: char, flag: bool) -> (u16, i16, u32, bool) {
        (small as u16 * 2, signed as i16 * 2, ch as u32, !flag)
    }

    pub fn labels(points: Vec<Point>) -> Vec<String> {
        points.into_iter().filter_map(|p| p.label).collect()
    }
}

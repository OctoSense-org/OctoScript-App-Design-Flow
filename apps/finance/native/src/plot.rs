//! Use the A2App StockPlot contract: a symbol and range drive the live chart.
//! The widget owns its data fetch, line, area, direction, grid and time ticks.
use makepad_widgets::{matplot::stock_plot::StockPlot, *};
use octosense_finance_service::model::{Point, State};
use serde_json::Value;

pub fn configure(
    plot: &mut StockPlot,
    cx: &mut Cx,
    binding: &Value,
    state: &State,
    detailed: bool,
    automatic: bool,
) {
    plot.symbol = binding["symbol"].as_str().unwrap_or_default().into();
    plot.range = binding["range"].as_str().unwrap_or("1D").into();
    let green = vec4(48. / 255., 209. / 255., 88. / 255., 1.);
    let red = vec4(1., 69. / 255., 58. / 255., 1.);
    plot.up_color = if state.prefs.red_up { red } else { green };
    plot.down_color = if state.prefs.red_up { green } else { red };
    plot.line_width = if detailed { 2.0 } else { 1.2 };
    plot.fill_alpha = if detailed { 0.16 } else { 0.08 };
    plot.show_baseline = detailed;
    plot.show_grid = detailed;
    plot.show_ticks = detailed;
    plot.show_border = false;
    plot.interactive = false;
    let ink = if state.prefs.light { 0.0 } else { 1.0 };
    plot.text_color = vec4(ink, ink, ink, if state.prefs.light { 0.6 } else { 0.35 });
    plot.grid_color = vec4(ink, ink, ink, 0.08);
    plot.baseline_color = vec4(ink, ink, ink, 0.19);
    plot.plot_margin = if detailed {
        Inset {
            left: 6.0,
            top: 8.0,
            right: 46.0,
            bottom: 18.0,
        }
    } else {
        Inset {
            left: 3.0,
            top: 3.0,
            right: 3.0,
            bottom: 3.0,
        }
    };
    if automatic {
        plot.use_symbol_data(cx);
    } else {
        // Explicit preview or an explicitly configured alternative provider.
        let points: Vec<Point> =
            serde_json::from_value(binding["points"].clone()).unwrap_or_default();
        plot.set_series(cx, points.iter().map(|p| (p.time as f64, p.price)), 0.0);
    }
}

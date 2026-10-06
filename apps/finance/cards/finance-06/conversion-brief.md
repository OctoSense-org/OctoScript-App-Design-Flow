# Conversion brief

This is an implementation brief, not a claim that these instructions were used
to generate the existing reference. Keep the submitted image prompt unchanged.

Apply MAPPING-RULES.md and mapping-rules.json. Resolve every needs_review/unknown
region. Prefer a matching native kit component, then built-in Makepad widgets,
then a reusable custom widget for missing behavior. Use SVG or cropped Image
assets only for artwork. Never substitute a chart or control with an asset.

For new image generation, include the exact text, font files/family/weights,
layout hierarchy, dimensions, spacing, colors, chart samples/units/domains and
selected control states. Preserve a separate machine-readable manifest. Request
complex illustrations as separate assets, or clearly bounded artwork-only regions
with no overlaid UI text. Do not invent missing numerical values from a mockup.

After generation, measure the actual reference. Requested layout is not measured
evidence. Inspect through Makepad's built-in HTTP instrument with a standalone
release binary; hidden windows support automated tests. See
`lab/core/NATIVE-INSTRUMENT.md`. Run semantic, geometry and visual checks;
legacy Studio capture/gate adapters require their own evidence schema.

```json
[
  {
    "id": "page",
    "x": 0.0,
    "y": 0.0,
    "w": 406.0,
    "h": 776.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "heading",
    "x": 20.0,
    "y": 30.0,
    "w": 316.0,
    "h": 40.800000000000004,
    "text": "AAPL",
    "font_src": "self:resources/ux/Inter-700.ttf",
    "size": 30.0,
    "weight": 700,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "data_status",
    "x": 24.0,
    "y": 75.0,
    "w": 354.0,
    "h": 13.600000000000001,
    "text": "Preview \u00b7 Fictional prices & news",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 10.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "back",
    "x": 8.0,
    "y": 3.0,
    "w": 48.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "back_control",
    "x": 8.0,
    "y": 3.0,
    "w": 48.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "back_label",
    "x": 12.0,
    "y": 12.0,
    "w": 40.0,
    "h": 17.68,
    "text": "\u2039",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_settings",
    "x": 358.0,
    "y": 28.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_settings_control",
    "x": 358.0,
    "y": 28.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_settings_label",
    "x": 362.0,
    "y": 37.0,
    "w": 28.0,
    "h": 17.68,
    "text": "",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "settings_glyph",
    "x": 365.0,
    "y": 36.0,
    "w": 22.0,
    "h": 24.48,
    "text": "\uf013",
    "font_src": "makepad_widgets:resources/fa-solid-900.ttf",
    "size": 18.0,
    "weight": 900,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "body_scroll",
    "x": 0.0,
    "y": 112.0,
    "w": 406.0,
    "h": 580.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "body_content",
    "x": 0.0,
    "y": 112.0,
    "w": 406.0,
    "h": 787.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "quote_card",
    "x": 20.0,
    "y": 116.0,
    "w": 366.0,
    "h": 129.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "company",
    "x": 24.0,
    "y": 120.0,
    "w": 352.0,
    "h": 20.400000000000002,
    "text": "Apple \u00b7 NASDAQ \u00b7 USD",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 15.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "last_price",
    "x": 24.0,
    "y": 151.0,
    "w": 280.0,
    "h": 46.24,
    "text": "220.00",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 34.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "day_change",
    "x": 26.0,
    "y": 210.0,
    "w": 350.0,
    "h": 23.12,
    "text": "+1.20% today",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 17.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "follow",
    "x": 280.0,
    "y": 161.0,
    "w": 102.0,
    "h": 38.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "follow_control",
    "x": 280.0,
    "y": 161.0,
    "w": 102.0,
    "h": 38.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "follow_bg",
    "x": 280.0,
    "y": 161.0,
    "w": 102.0,
    "h": 38.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "follow_label",
    "x": 284.0,
    "y": 171.0,
    "w": 94.0,
    "h": 17.68,
    "text": "Following",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "price_chart",
    "x": 24.0,
    "y": 281.0,
    "w": 354.0,
    "h": 186.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "range_return",
    "x": 24.0,
    "y": 502.0,
    "w": 354.0,
    "h": 16.32,
    "text": "1M  +22.22%",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 12.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "chart_time",
    "x": 24.0,
    "y": 480.0,
    "w": 354.0,
    "h": 13.600000000000001,
    "text": "08/20 16:00                 09/16 16:00 UTC",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 10.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "range_0",
    "x": 20.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_0_control",
    "x": 20.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_0_bg",
    "x": 20.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "range_0_label",
    "x": 24.0,
    "y": 243.0,
    "w": 60.0,
    "h": 17.68,
    "text": "1D",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "range_1",
    "x": 94.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_1_control",
    "x": 94.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_1_bg",
    "x": 94.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "range_1_label",
    "x": 98.0,
    "y": 243.0,
    "w": 60.0,
    "h": 17.68,
    "text": "1W",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "range_2",
    "x": 168.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_2_control",
    "x": 168.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_2_bg",
    "x": 168.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "range_2_label",
    "x": 172.0,
    "y": 243.0,
    "w": 60.0,
    "h": 17.68,
    "text": "1M",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "range_3",
    "x": 242.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_3_control",
    "x": 242.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_3_bg",
    "x": 242.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "range_3_label",
    "x": 246.0,
    "y": 243.0,
    "w": 60.0,
    "h": 17.68,
    "text": "6M",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "range_4",
    "x": 316.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_4_control",
    "x": 316.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "range_4_bg",
    "x": 316.0,
    "y": 235.0,
    "w": 68.0,
    "h": 34.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "range_4_label",
    "x": 320.0,
    "y": 243.0,
    "w": 60.0,
    "h": 17.68,
    "text": "1Y",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "inspection",
    "x": 24.0,
    "y": 543.0,
    "w": 356.0,
    "h": 14.96,
    "text": "2026-09-07 16:00 UTC \u00b7 211.00 USD",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 11.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_0_label",
    "x": 24.0,
    "y": 580.0,
    "w": 170.0,
    "h": 16.32,
    "text": "Open",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 12.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_0_value",
    "x": 24.0,
    "y": 602.0,
    "w": 170.0,
    "h": 24.48,
    "text": "217.40",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 18.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_1_label",
    "x": 210.0,
    "y": 580.0,
    "w": 170.0,
    "h": 16.32,
    "text": "Previous close",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 12.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_1_value",
    "x": 210.0,
    "y": 602.0,
    "w": 170.0,
    "h": 24.48,
    "text": "217.39",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 18.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_2_label",
    "x": 24.0,
    "y": 646.0,
    "w": 170.0,
    "h": 16.32,
    "text": "High",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 12.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_2_value",
    "x": 24.0,
    "y": 668.0,
    "w": 170.0,
    "h": 24.48,
    "text": "220.50",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 18.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_3_label",
    "x": 210.0,
    "y": 646.0,
    "w": 170.0,
    "h": 16.32,
    "text": "Low",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 12.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stat_3_value",
    "x": 210.0,
    "y": 668.0,
    "w": 170.0,
    "h": 24.48,
    "text": "217.00",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 18.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "quote_source",
    "x": 24.0,
    "y": 727.0,
    "w": 356.0,
    "h": 13.600000000000001,
    "text": "Preview fixture \u00b7 Fictional \u2022 not market data",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 10.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "quote_time",
    "x": 24.0,
    "y": 745.0,
    "w": 356.0,
    "h": 13.600000000000001,
    "text": "Observed 2026-09-16 16:00 UTC",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 10.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "company_news",
    "x": 20.0,
    "y": 780.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "company_news_control",
    "x": 20.0,
    "y": 780.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "company_news_bg",
    "x": 20.0,
    "y": 780.0,
    "w": 366.0,
    "h": 44.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "company_news_label",
    "x": 24.0,
    "y": 793.0,
    "w": 358.0,
    "h": 17.68,
    "text": "Company news  \u203a",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "detail_refresh",
    "x": 20.0,
    "y": 834.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "detail_refresh_control",
    "x": 20.0,
    "y": 834.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "detail_refresh_bg",
    "x": 20.0,
    "y": 834.0,
    "w": 366.0,
    "h": 44.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "detail_refresh_label",
    "x": 24.0,
    "y": 847.0,
    "w": 358.0,
    "h": 17.68,
    "text": "Refresh",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 13.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_surface",
    "x": 0.0,
    "y": 704.0,
    "w": 406.0,
    "h": 72.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "tab_watchlist",
    "x": 2.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_watchlist_control",
    "x": 2.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_watchlist_label",
    "x": 6.0,
    "y": 744.0,
    "w": 91.0,
    "h": 12.24,
    "text": "Stocks",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 9.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_watchlist_glyph",
    "x": 40.0,
    "y": 712.0,
    "w": 23.0,
    "h": 25.840000000000003,
    "text": "\uf00a",
    "font_src": "makepad_widgets:resources/fa-solid-900.ttf",
    "size": 19.0,
    "weight": 900,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_markets",
    "x": 103.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_markets_control",
    "x": 103.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_markets_label",
    "x": 107.0,
    "y": 744.0,
    "w": 91.0,
    "h": 12.24,
    "text": "Markets",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 9.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_markets_glyph",
    "x": 141.0,
    "y": 712.0,
    "w": 23.0,
    "h": 25.840000000000003,
    "text": "\uf080",
    "font_src": "makepad_widgets:resources/fa-solid-900.ttf",
    "size": 19.0,
    "weight": 900,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_news",
    "x": 204.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_news_control",
    "x": 204.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_news_label",
    "x": 208.0,
    "y": 744.0,
    "w": 91.0,
    "h": 12.24,
    "text": "News",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 9.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_news_glyph",
    "x": 242.0,
    "y": 712.0,
    "w": 23.0,
    "h": 25.840000000000003,
    "text": "\uf1ea",
    "font_src": "makepad_widgets:resources/fa-solid-900.ttf",
    "size": 19.0,
    "weight": 900,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_saved",
    "x": 305.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_saved_control",
    "x": 305.0,
    "y": 707.0,
    "w": 99.0,
    "h": 54.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "tab_saved_label",
    "x": 309.0,
    "y": 744.0,
    "w": 91.0,
    "h": 12.24,
    "text": "Saved",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 9.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tab_saved_glyph",
    "x": 343.0,
    "y": 712.0,
    "w": 23.0,
    "h": 25.840000000000003,
    "text": "\uf02e",
    "font_src": "makepad_widgets:resources/fa-solid-900.ttf",
    "size": 19.0,
    "weight": 900,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "home_indicator",
    "x": 145.0,
    "y": 765.0,
    "w": 116.0,
    "h": 4.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  }
]
```

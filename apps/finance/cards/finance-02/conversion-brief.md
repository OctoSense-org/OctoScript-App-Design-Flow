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
    "text": "Markets",
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
    "h": 870.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "region_0",
    "x": 20.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_0_control",
    "x": 20.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_0_bg",
    "x": 20.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "region_0_label",
    "x": 24.0,
    "y": 128.0,
    "w": 82.0,
    "h": 17.68,
    "text": "All",
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
    "id": "region_1",
    "x": 113.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_1_control",
    "x": 113.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_1_bg",
    "x": 113.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "region_1_label",
    "x": 117.0,
    "y": 128.0,
    "w": 82.0,
    "h": 17.68,
    "text": "US",
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
    "id": "region_2",
    "x": 206.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_2_control",
    "x": 206.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_2_bg",
    "x": 206.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "region_2_label",
    "x": 210.0,
    "y": 128.0,
    "w": 82.0,
    "h": 17.68,
    "text": "HK",
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
    "id": "region_3",
    "x": 299.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_3_control",
    "x": 299.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "region_3_bg",
    "x": 299.0,
    "y": 123.0,
    "w": 90.0,
    "h": 28.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "region_3_label",
    "x": 303.0,
    "y": 128.0,
    "w": 82.0,
    "h": 17.68,
    "text": "CN",
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
    "id": "market_scope",
    "x": 24.0,
    "y": 172.0,
    "w": 356.0,
    "h": 14.96,
    "text": "Tracked stocks \u00b7 not a whole-market ranking",
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
    "id": "market_brief_card",
    "x": 20.0,
    "y": 204.0,
    "w": 366.0,
    "h": 308.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "market_0",
    "x": 20.0,
    "y": 204.0,
    "w": 366.0,
    "h": 92.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "market_0_name",
    "x": 36.0,
    "y": 218.0,
    "w": 330.0,
    "h": 27.200000000000003,
    "text": "US",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 20.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "market_0_sub",
    "x": 36.0,
    "y": 251.0,
    "w": 330.0,
    "h": 16.32,
    "text": "NASDAQ / NYSE \u00b7 USD \u00b7 New York",
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
    "id": "market_0_session",
    "x": 36.0,
    "y": 270.0,
    "w": 330.0,
    "h": 13.600000000000001,
    "text": "Session unavailable in preview",
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
    "id": "market_1",
    "x": 20.0,
    "y": 312.0,
    "w": 366.0,
    "h": 92.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "market_1_name",
    "x": 36.0,
    "y": 326.0,
    "w": 330.0,
    "h": 27.200000000000003,
    "text": "Hong Kong",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 20.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "market_1_sub",
    "x": 36.0,
    "y": 359.0,
    "w": 330.0,
    "h": 16.32,
    "text": "HKEX \u00b7 HKD \u00b7 Hong Kong",
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
    "id": "market_1_session",
    "x": 36.0,
    "y": 378.0,
    "w": 330.0,
    "h": 13.600000000000001,
    "text": "Session unavailable in preview",
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
    "id": "market_2",
    "x": 20.0,
    "y": 420.0,
    "w": 366.0,
    "h": 92.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "market_2_name",
    "x": 36.0,
    "y": 434.0,
    "w": 330.0,
    "h": 27.200000000000003,
    "text": "Mainland China",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 20.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "market_2_sub",
    "x": 36.0,
    "y": 467.0,
    "w": 330.0,
    "h": 16.32,
    "text": "SSE / SZSE \u00b7 CNY \u00b7 Shanghai",
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
    "id": "market_2_session",
    "x": 36.0,
    "y": 486.0,
    "w": 330.0,
    "h": 13.600000000000001,
    "text": "Session unavailable in preview",
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
    "id": "movers_title",
    "x": 24.0,
    "y": 550.0,
    "w": 354.0,
    "h": 29.92,
    "text": "Watchlist movers",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 22.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_0",
    "x": 20.0,
    "y": 590.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_0_control",
    "x": 20.0,
    "y": 590.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_0_label",
    "x": 24.0,
    "y": 610.0,
    "w": 358.0,
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
    "id": "stock_0_symbol",
    "x": 24.0,
    "y": 597.0,
    "w": 112.0,
    "h": 21.76,
    "text": "300750",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_0_name",
    "x": 24.0,
    "y": 621.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u5b81\u5fb7\u65f6\u4ee3",
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
    "id": "stock_0_badge",
    "x": 139.0,
    "y": 608.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_0_market",
    "x": 140.0,
    "y": 612.0,
    "w": 27.0,
    "h": 10.88,
    "text": "CN",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 8.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_0_price",
    "x": 274.0,
    "y": 597.0,
    "w": 102.0,
    "h": 21.76,
    "text": "250.00",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_0_change",
    "x": 284.0,
    "y": 621.0,
    "w": 92.0,
    "h": 16.32,
    "text": "+1.60%",
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
    "id": "spark_0",
    "x": 181.0,
    "y": 607.0,
    "w": 82.0,
    "h": 25.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "stock_0_rule",
    "x": 24.0,
    "y": 648.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_1",
    "x": 20.0,
    "y": 652.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_1_control",
    "x": 20.0,
    "y": 652.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_1_label",
    "x": 24.0,
    "y": 672.0,
    "w": 358.0,
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
    "id": "stock_1_symbol",
    "x": 24.0,
    "y": 659.0,
    "w": 112.0,
    "h": 21.76,
    "text": "AAPL",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_1_name",
    "x": 24.0,
    "y": 683.0,
    "w": 132.0,
    "h": 14.96,
    "text": "Apple",
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
    "id": "stock_1_badge",
    "x": 139.0,
    "y": 670.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_1_market",
    "x": 140.0,
    "y": 674.0,
    "w": 27.0,
    "h": 10.88,
    "text": "US",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 8.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_1_price",
    "x": 274.0,
    "y": 659.0,
    "w": 102.0,
    "h": 21.76,
    "text": "220.00",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_1_change",
    "x": 284.0,
    "y": 683.0,
    "w": 92.0,
    "h": 16.32,
    "text": "+1.20%",
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
    "id": "spark_1",
    "x": 181.0,
    "y": 669.0,
    "w": 82.0,
    "h": 25.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "stock_1_rule",
    "x": 24.0,
    "y": 710.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_2",
    "x": 20.0,
    "y": 714.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_2_control",
    "x": 20.0,
    "y": 714.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_2_label",
    "x": 24.0,
    "y": 734.0,
    "w": 358.0,
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
    "id": "stock_2_symbol",
    "x": 24.0,
    "y": 721.0,
    "w": 112.0,
    "h": 21.76,
    "text": "09988",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_2_name",
    "x": 24.0,
    "y": 745.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u963f\u91cc\u5df4\u5df4",
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
    "id": "stock_2_badge",
    "x": 139.0,
    "y": 732.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_2_market",
    "x": 140.0,
    "y": 736.0,
    "w": 27.0,
    "h": 10.88,
    "text": "HK",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 8.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_2_price",
    "x": 274.0,
    "y": 721.0,
    "w": 102.0,
    "h": 21.76,
    "text": "100.00",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_2_change",
    "x": 284.0,
    "y": 745.0,
    "w": 92.0,
    "h": 16.32,
    "text": "+0.90%",
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
    "id": "spark_2",
    "x": 181.0,
    "y": 731.0,
    "w": 82.0,
    "h": 25.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "stock_2_rule",
    "x": 24.0,
    "y": 772.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_3",
    "x": 20.0,
    "y": 776.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_3_control",
    "x": 20.0,
    "y": 776.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_3_label",
    "x": 24.0,
    "y": 796.0,
    "w": 358.0,
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
    "id": "stock_3_symbol",
    "x": 24.0,
    "y": 783.0,
    "w": 112.0,
    "h": 21.76,
    "text": "600519",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_3_name",
    "x": 24.0,
    "y": 807.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u8d35\u5dde\u8305\u53f0",
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
    "id": "stock_3_badge",
    "x": 139.0,
    "y": 794.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_3_market",
    "x": 140.0,
    "y": 798.0,
    "w": 27.0,
    "h": 10.88,
    "text": "CN",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 8.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_3_price",
    "x": 274.0,
    "y": 783.0,
    "w": 102.0,
    "h": 21.76,
    "text": "1400.00",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_3_change",
    "x": 284.0,
    "y": 807.0,
    "w": 92.0,
    "h": 16.32,
    "text": "+0.80%",
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
    "id": "spark_3",
    "x": 181.0,
    "y": 793.0,
    "w": 82.0,
    "h": 25.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "stock_3_rule",
    "x": 24.0,
    "y": 834.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_4",
    "x": 20.0,
    "y": 838.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_4_control",
    "x": 20.0,
    "y": 838.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_4_label",
    "x": 24.0,
    "y": 858.0,
    "w": 358.0,
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
    "id": "stock_4_symbol",
    "x": 24.0,
    "y": 845.0,
    "w": 112.0,
    "h": 21.76,
    "text": "MSFT",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_4_name",
    "x": 24.0,
    "y": 869.0,
    "w": 132.0,
    "h": 14.96,
    "text": "Microsoft",
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
    "id": "stock_4_badge",
    "x": 139.0,
    "y": 856.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_4_market",
    "x": 140.0,
    "y": 860.0,
    "w": 27.0,
    "h": 10.88,
    "text": "US",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 8.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_4_price",
    "x": 274.0,
    "y": 845.0,
    "w": 102.0,
    "h": 21.76,
    "text": "420.00",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_4_change",
    "x": 284.0,
    "y": 869.0,
    "w": 92.0,
    "h": 16.32,
    "text": "-0.40%",
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
    "id": "spark_4",
    "x": 181.0,
    "y": 855.0,
    "w": 82.0,
    "h": 25.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "stock_4_rule",
    "x": 24.0,
    "y": 896.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_5",
    "x": 20.0,
    "y": 900.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_5_control",
    "x": 20.0,
    "y": 900.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_5_label",
    "x": 24.0,
    "y": 920.0,
    "w": 358.0,
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
    "id": "stock_5_symbol",
    "x": 24.0,
    "y": 907.0,
    "w": 112.0,
    "h": 21.76,
    "text": "00700",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_5_name",
    "x": 24.0,
    "y": 931.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u817e\u8baf\u63a7\u80a1",
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
    "id": "stock_5_badge",
    "x": 139.0,
    "y": 918.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_5_market",
    "x": 140.0,
    "y": 922.0,
    "w": 27.0,
    "h": 10.88,
    "text": "HK",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 8.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_5_price",
    "x": 274.0,
    "y": 907.0,
    "w": 102.0,
    "h": 21.76,
    "text": "400.00",
    "font_src": "self:resources/ux/Inter-600.ttf",
    "size": 16.0,
    "weight": 600,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "stock_5_change",
    "x": 284.0,
    "y": 931.0,
    "w": 92.0,
    "h": 16.32,
    "text": "-0.60%",
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
    "id": "spark_5",
    "x": 181.0,
    "y": 917.0,
    "w": 82.0,
    "h": 25.0,
    "role": "chart.line",
    "native_candidates": [
      "LineChart",
      "LinePlot",
      "D3LineChart"
    ]
  },
  {
    "id": "stock_5_rule",
    "x": 24.0,
    "y": 958.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
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

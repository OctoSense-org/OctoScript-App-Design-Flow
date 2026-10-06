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
    "text": "Stocks",
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
    "id": "edit",
    "x": 310.0,
    "y": 27.0,
    "w": 40.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "edit_control",
    "x": 310.0,
    "y": 27.0,
    "w": 40.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "edit_label",
    "x": 314.0,
    "y": 38.0,
    "w": 32.0,
    "h": 17.68,
    "text": "\u00b7\u00b7\u00b7",
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
    "h": 682.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "search_open",
    "x": 20.0,
    "y": 112.0,
    "w": 366.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "search_open_control",
    "x": 20.0,
    "y": 112.0,
    "w": 366.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "search_open_bg",
    "x": 20.0,
    "y": 112.0,
    "w": 366.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "search_open_label",
    "x": 56.0,
    "y": 121.0,
    "w": 320.0,
    "h": 17.68,
    "text": "Search symbols or companies",
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
    "id": "search_glyph",
    "x": 32.0,
    "y": 121.0,
    "w": 18.0,
    "h": 19.040000000000003,
    "text": "\uf002",
    "font_src": "makepad_widgets:resources/fa-solid-900.ttf",
    "size": 14.0,
    "weight": 900,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "region_0",
    "x": 20.0,
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 163.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 163.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 163.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 158.0,
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
    "y": 163.0,
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
    "id": "watchlist_card",
    "x": 20.0,
    "y": 196.0,
    "w": 366.0,
    "h": 124.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_0",
    "x": 20.0,
    "y": 196.0,
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
    "y": 196.0,
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
    "y": 216.0,
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
    "y": 203.0,
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
    "id": "stock_0_name",
    "x": 24.0,
    "y": 227.0,
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
    "id": "stock_0_badge",
    "x": 139.0,
    "y": 214.0,
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
    "y": 218.0,
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
    "id": "stock_0_price",
    "x": 274.0,
    "y": 203.0,
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
    "id": "stock_0_change",
    "x": 284.0,
    "y": 227.0,
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
    "id": "spark_0",
    "x": 181.0,
    "y": 213.0,
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
    "y": 254.0,
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
    "y": 258.0,
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
    "y": 258.0,
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
    "y": 278.0,
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
    "y": 265.0,
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
    "id": "stock_1_name",
    "x": 24.0,
    "y": 289.0,
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
    "id": "stock_1_badge",
    "x": 139.0,
    "y": 276.0,
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
    "y": 280.0,
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
    "y": 265.0,
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
    "id": "stock_1_change",
    "x": 284.0,
    "y": 289.0,
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
    "id": "spark_1",
    "x": 181.0,
    "y": 275.0,
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
    "y": 316.0,
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
    "y": 320.0,
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
    "y": 320.0,
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
    "y": 340.0,
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
    "y": 327.0,
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
    "id": "stock_2_name",
    "x": 24.0,
    "y": 351.0,
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
    "id": "stock_2_badge",
    "x": 139.0,
    "y": 338.0,
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
    "y": 342.0,
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
    "y": 327.0,
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
    "id": "stock_2_change",
    "x": 284.0,
    "y": 351.0,
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
    "id": "spark_2",
    "x": 181.0,
    "y": 337.0,
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
    "y": 378.0,
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
    "y": 382.0,
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
    "y": 382.0,
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
    "y": 402.0,
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
    "y": 389.0,
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
    "id": "stock_3_name",
    "x": 24.0,
    "y": 413.0,
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
    "id": "stock_3_badge",
    "x": 139.0,
    "y": 400.0,
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
    "y": 404.0,
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
    "id": "stock_3_price",
    "x": 274.0,
    "y": 389.0,
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
    "id": "stock_3_change",
    "x": 284.0,
    "y": 413.0,
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
    "id": "spark_3",
    "x": 181.0,
    "y": 399.0,
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
    "y": 440.0,
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
    "y": 444.0,
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
    "y": 444.0,
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
    "y": 464.0,
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
    "y": 451.0,
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
    "id": "stock_4_name",
    "x": 24.0,
    "y": 475.0,
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
    "id": "stock_4_badge",
    "x": 139.0,
    "y": 462.0,
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
    "y": 466.0,
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
    "id": "stock_4_price",
    "x": 274.0,
    "y": 451.0,
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
    "id": "stock_4_change",
    "x": 284.0,
    "y": 475.0,
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
    "id": "spark_4",
    "x": 181.0,
    "y": 461.0,
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
    "y": 502.0,
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
    "y": 506.0,
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
    "y": 506.0,
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
    "y": 526.0,
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
    "y": 513.0,
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
    "id": "stock_5_name",
    "x": 24.0,
    "y": 537.0,
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
    "id": "stock_5_badge",
    "x": 139.0,
    "y": 524.0,
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
    "y": 528.0,
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
    "id": "stock_5_price",
    "x": 274.0,
    "y": 513.0,
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
    "id": "stock_5_change",
    "x": 284.0,
    "y": 537.0,
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
    "id": "spark_5",
    "x": 181.0,
    "y": 523.0,
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
    "y": 564.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "home_news_heading",
    "x": 24.0,
    "y": 586.0,
    "w": 270.0,
    "h": 27.200000000000003,
    "text": "Business News",
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
    "id": "home_news_all",
    "x": 306.0,
    "y": 580.0,
    "w": 74.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "home_news_all_control",
    "x": 306.0,
    "y": 580.0,
    "w": 74.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "home_news_all_label",
    "x": 310.0,
    "y": 589.0,
    "w": 66.0,
    "h": 17.68,
    "text": "See all",
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
    "id": "story_0",
    "x": 20.0,
    "y": 618.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_0_control",
    "x": 20.0,
    "y": 618.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_0_label",
    "x": 24.0,
    "y": 661.5,
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
    "id": "story_0_source",
    "x": 24.0,
    "y": 626.0,
    "w": 342.0,
    "h": 14.96,
    "text": "Preview Journal \u00b7 US",
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
    "id": "story_0_title_0",
    "x": 24.0,
    "y": 649.0,
    "w": 300.0,
    "h": 21.76,
    "text": "Three markets, one watchlist",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 16.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "save_0",
    "x": 338.0,
    "y": 659.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_0_control",
    "x": 338.0,
    "y": 659.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_0_label",
    "x": 342.0,
    "y": 670.0,
    "w": 34.0,
    "h": 17.68,
    "text": "\u2606",
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
    "id": "story_0_rule",
    "x": 24.0,
    "y": 721.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "refresh",
    "x": 20.0,
    "y": 734.0,
    "w": 366.0,
    "h": 42.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "refresh_control",
    "x": 20.0,
    "y": 734.0,
    "w": 366.0,
    "h": 42.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "refresh_bg",
    "x": 20.0,
    "y": 734.0,
    "w": 366.0,
    "h": 42.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "refresh_label",
    "x": 24.0,
    "y": 746.0,
    "w": 358.0,
    "h": 17.68,
    "text": "Refresh quotes",
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

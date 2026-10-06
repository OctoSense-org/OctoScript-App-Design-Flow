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
    "text": "Search",
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
    "h": 677556.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "search_bg",
    "x": 20.0,
    "y": 112.0,
    "w": 366.0,
    "h": 42.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "search",
    "x": 30.0,
    "y": 114.0,
    "w": 346.0,
    "h": 38.0,
    "role": "input",
    "native_candidates": [
      "TextInput",
      "KitFormField"
    ]
  },
  {
    "id": "search_input",
    "x": 34.0,
    "y": 122.0,
    "w": 338.0,
    "h": 21.76,
    "text": "",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 16.0,
    "weight": 400,
    "role": "input",
    "native_candidates": [
      "TextInput",
      "KitFormField"
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
    "id": "directory_scope",
    "x": 24.0,
    "y": 198.0,
    "w": 354.0,
    "h": 14.96,
    "text": "Public directory \u00b7 access depends on your plan",
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
    "id": "stock_0",
    "x": 20.0,
    "y": 226.0,
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
    "y": 226.0,
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
    "y": 246.0,
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
    "y": 233.0,
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
    "y": 257.0,
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
    "y": 244.0,
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
    "y": 248.0,
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
    "id": "add_0",
    "x": 334.0,
    "y": 237.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_0_control",
    "x": 334.0,
    "y": 237.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_0_bg",
    "x": 334.0,
    "y": 237.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_0_label",
    "x": 338.0,
    "y": 246.0,
    "w": 28.0,
    "h": 17.68,
    "text": "\u2212",
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
    "id": "stock_0_rule",
    "x": 24.0,
    "y": 284.0,
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
    "y": 288.0,
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
    "y": 288.0,
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
    "y": 308.0,
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
    "y": 295.0,
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
    "y": 319.0,
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
    "y": 306.0,
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
    "y": 310.0,
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
    "id": "add_1",
    "x": 334.0,
    "y": 299.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_1_control",
    "x": 334.0,
    "y": 299.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_1_bg",
    "x": 334.0,
    "y": 299.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_1_label",
    "x": 338.0,
    "y": 308.0,
    "w": 28.0,
    "h": 17.68,
    "text": "\u2212",
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
    "id": "stock_1_rule",
    "x": 24.0,
    "y": 346.0,
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
    "y": 350.0,
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
    "y": 350.0,
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
    "y": 370.0,
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
    "y": 357.0,
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
    "y": 381.0,
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
    "y": 368.0,
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
    "y": 372.0,
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
    "id": "add_2",
    "x": 334.0,
    "y": 361.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_2_control",
    "x": 334.0,
    "y": 361.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_2_bg",
    "x": 334.0,
    "y": 361.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_2_label",
    "x": 338.0,
    "y": 370.0,
    "w": 28.0,
    "h": 17.68,
    "text": "\u2212",
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
    "id": "stock_2_rule",
    "x": 24.0,
    "y": 408.0,
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
    "y": 412.0,
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
    "y": 412.0,
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
    "y": 432.0,
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
    "y": 419.0,
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
    "y": 443.0,
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
    "y": 430.0,
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
    "y": 434.0,
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
    "id": "add_3",
    "x": 334.0,
    "y": 423.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_3_control",
    "x": 334.0,
    "y": 423.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_3_bg",
    "x": 334.0,
    "y": 423.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_3_label",
    "x": 338.0,
    "y": 432.0,
    "w": 28.0,
    "h": 17.68,
    "text": "\u2212",
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
    "id": "stock_3_rule",
    "x": 24.0,
    "y": 470.0,
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
    "y": 474.0,
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
    "y": 474.0,
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
    "y": 494.0,
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
    "y": 481.0,
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
    "y": 505.0,
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
    "y": 492.0,
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
    "y": 496.0,
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
    "id": "add_4",
    "x": 334.0,
    "y": 485.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_4_control",
    "x": 334.0,
    "y": 485.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_4_bg",
    "x": 334.0,
    "y": 485.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_4_label",
    "x": 338.0,
    "y": 494.0,
    "w": 28.0,
    "h": 17.68,
    "text": "\u2212",
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
    "id": "stock_4_rule",
    "x": 24.0,
    "y": 532.0,
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
    "y": 536.0,
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
    "y": 536.0,
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
    "y": 556.0,
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
    "y": 543.0,
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
    "y": 567.0,
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
    "y": 554.0,
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
    "y": 558.0,
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
    "id": "add_5",
    "x": 334.0,
    "y": 547.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_5_control",
    "x": 334.0,
    "y": 547.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_5_bg",
    "x": 334.0,
    "y": 547.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_5_label",
    "x": 338.0,
    "y": 556.0,
    "w": 28.0,
    "h": 17.68,
    "text": "\u2212",
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
    "id": "stock_5_rule",
    "x": 24.0,
    "y": 594.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_6",
    "x": 20.0,
    "y": 598.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_6_control",
    "x": 20.0,
    "y": 598.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_6_label",
    "x": 24.0,
    "y": 618.0,
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
    "id": "stock_6_symbol",
    "x": 24.0,
    "y": 605.0,
    "w": 112.0,
    "h": 21.76,
    "text": "TSLA",
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
    "id": "stock_6_name",
    "x": 24.0,
    "y": 629.0,
    "w": 132.0,
    "h": 14.96,
    "text": "Tesla",
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
    "id": "stock_6_badge",
    "x": 139.0,
    "y": 616.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_6_market",
    "x": 140.0,
    "y": 620.0,
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
    "id": "add_6",
    "x": 334.0,
    "y": 609.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_6_control",
    "x": 334.0,
    "y": 609.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_6_bg",
    "x": 334.0,
    "y": 609.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_6_label",
    "x": 338.0,
    "y": 618.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_6_rule",
    "x": 24.0,
    "y": 656.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_7",
    "x": 20.0,
    "y": 660.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_7_control",
    "x": 20.0,
    "y": 660.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_7_label",
    "x": 24.0,
    "y": 680.0,
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
    "id": "stock_7_symbol",
    "x": 24.0,
    "y": 667.0,
    "w": 112.0,
    "h": 21.76,
    "text": "NVDA",
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
    "id": "stock_7_name",
    "x": 24.0,
    "y": 691.0,
    "w": 132.0,
    "h": 14.96,
    "text": "NVIDIA",
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
    "id": "stock_7_badge",
    "x": 139.0,
    "y": 678.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_7_market",
    "x": 140.0,
    "y": 682.0,
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
    "id": "add_7",
    "x": 334.0,
    "y": 671.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_7_control",
    "x": 334.0,
    "y": 671.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_7_bg",
    "x": 334.0,
    "y": 671.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_7_label",
    "x": 338.0,
    "y": 680.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_7_rule",
    "x": 24.0,
    "y": 718.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_8",
    "x": 20.0,
    "y": 722.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_8_control",
    "x": 20.0,
    "y": 722.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_8_label",
    "x": 24.0,
    "y": 742.0,
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
    "id": "stock_8_symbol",
    "x": 24.0,
    "y": 729.0,
    "w": 112.0,
    "h": 21.76,
    "text": "BABA",
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
    "id": "stock_8_name",
    "x": 24.0,
    "y": 753.0,
    "w": 132.0,
    "h": 14.96,
    "text": "Alibaba ADR",
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
    "id": "stock_8_badge",
    "x": 139.0,
    "y": 740.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_8_market",
    "x": 140.0,
    "y": 744.0,
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
    "id": "add_8",
    "x": 334.0,
    "y": 733.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_8_control",
    "x": 334.0,
    "y": 733.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_8_bg",
    "x": 334.0,
    "y": 733.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_8_label",
    "x": 338.0,
    "y": 742.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_8_rule",
    "x": 24.0,
    "y": 780.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_9",
    "x": 20.0,
    "y": 784.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_9_control",
    "x": 20.0,
    "y": 784.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_9_label",
    "x": 24.0,
    "y": 804.0,
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
    "id": "stock_9_symbol",
    "x": 24.0,
    "y": 791.0,
    "w": 112.0,
    "h": 21.76,
    "text": "01810",
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
    "id": "stock_9_name",
    "x": 24.0,
    "y": 815.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u5c0f\u7c73\u96c6\u56e2",
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
    "id": "stock_9_badge",
    "x": 139.0,
    "y": 802.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_9_market",
    "x": 140.0,
    "y": 806.0,
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
    "id": "add_9",
    "x": 334.0,
    "y": 795.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_9_control",
    "x": 334.0,
    "y": 795.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_9_bg",
    "x": 334.0,
    "y": 795.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_9_label",
    "x": 338.0,
    "y": 804.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_9_rule",
    "x": 24.0,
    "y": 842.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_10",
    "x": 20.0,
    "y": 846.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_10_control",
    "x": 20.0,
    "y": 846.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_10_label",
    "x": 24.0,
    "y": 866.0,
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
    "id": "stock_10_symbol",
    "x": 24.0,
    "y": 853.0,
    "w": 112.0,
    "h": 21.76,
    "text": "601318",
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
    "id": "stock_10_name",
    "x": 24.0,
    "y": 877.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u4e2d\u56fd\u5e73\u5b89",
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
    "id": "stock_10_badge",
    "x": 139.0,
    "y": 864.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_10_market",
    "x": 140.0,
    "y": 868.0,
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
    "id": "add_10",
    "x": 334.0,
    "y": 857.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_10_control",
    "x": 334.0,
    "y": 857.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_10_bg",
    "x": 334.0,
    "y": 857.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_10_label",
    "x": 338.0,
    "y": 866.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_10_rule",
    "x": 24.0,
    "y": 904.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_11",
    "x": 20.0,
    "y": 908.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_11_control",
    "x": 20.0,
    "y": 908.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_11_label",
    "x": 24.0,
    "y": 928.0,
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
    "id": "stock_11_symbol",
    "x": 24.0,
    "y": 915.0,
    "w": 112.0,
    "h": 21.76,
    "text": "000001",
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
    "id": "stock_11_name",
    "x": 24.0,
    "y": 939.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u5e73\u5b89\u94f6\u884c",
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
    "id": "stock_11_badge",
    "x": 139.0,
    "y": 926.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_11_market",
    "x": 140.0,
    "y": 930.0,
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
    "id": "add_11",
    "x": 334.0,
    "y": 919.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_11_control",
    "x": 334.0,
    "y": 919.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_11_bg",
    "x": 334.0,
    "y": 919.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_11_label",
    "x": 338.0,
    "y": 928.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_11_rule",
    "x": 24.0,
    "y": 966.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_12",
    "x": 20.0,
    "y": 970.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_12_control",
    "x": 20.0,
    "y": 970.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_12_label",
    "x": 24.0,
    "y": 990.0,
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
    "id": "stock_12_symbol",
    "x": 24.0,
    "y": 977.0,
    "w": 112.0,
    "h": 21.76,
    "text": "GOOG",
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
    "id": "stock_12_name",
    "x": 24.0,
    "y": 1001.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u8c37\u6b4cC",
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
    "id": "stock_12_badge",
    "x": 139.0,
    "y": 988.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_12_market",
    "x": 140.0,
    "y": 992.0,
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
    "id": "add_12",
    "x": 334.0,
    "y": 981.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_12_control",
    "x": 334.0,
    "y": 981.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_12_bg",
    "x": 334.0,
    "y": 981.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_12_label",
    "x": 338.0,
    "y": 990.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_12_rule",
    "x": 24.0,
    "y": 1028.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_13",
    "x": 20.0,
    "y": 1032.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_13_control",
    "x": 20.0,
    "y": 1032.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_13_label",
    "x": 24.0,
    "y": 1052.0,
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
    "id": "stock_13_symbol",
    "x": 24.0,
    "y": 1039.0,
    "w": 112.0,
    "h": 21.76,
    "text": "GOOGL",
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
    "id": "stock_13_name",
    "x": 24.0,
    "y": 1063.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u8c37\u6b4cA",
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
    "id": "stock_13_badge",
    "x": 139.0,
    "y": 1050.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_13_market",
    "x": 140.0,
    "y": 1054.0,
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
    "id": "add_13",
    "x": 334.0,
    "y": 1043.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_13_control",
    "x": 334.0,
    "y": 1043.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_13_bg",
    "x": 334.0,
    "y": 1043.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_13_label",
    "x": 338.0,
    "y": 1052.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_13_rule",
    "x": 24.0,
    "y": 1090.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_14",
    "x": 20.0,
    "y": 1094.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_14_control",
    "x": 20.0,
    "y": 1094.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_14_label",
    "x": 24.0,
    "y": 1114.0,
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
    "id": "stock_14_symbol",
    "x": 24.0,
    "y": 1101.0,
    "w": 112.0,
    "h": 21.76,
    "text": "AMZN",
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
    "id": "stock_14_name",
    "x": 24.0,
    "y": 1125.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u4e9a\u9a6c\u900a",
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
    "id": "stock_14_badge",
    "x": 139.0,
    "y": 1112.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_14_market",
    "x": 140.0,
    "y": 1116.0,
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
    "id": "add_14",
    "x": 334.0,
    "y": 1105.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_14_control",
    "x": 334.0,
    "y": 1105.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_14_bg",
    "x": 334.0,
    "y": 1105.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_14_label",
    "x": 338.0,
    "y": 1114.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_14_rule",
    "x": 24.0,
    "y": 1152.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_15",
    "x": 20.0,
    "y": 1156.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_15_control",
    "x": 20.0,
    "y": 1156.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_15_label",
    "x": 24.0,
    "y": 1176.0,
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
    "id": "stock_15_symbol",
    "x": 24.0,
    "y": 1163.0,
    "w": 112.0,
    "h": 21.76,
    "text": "META",
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
    "id": "stock_15_name",
    "x": 24.0,
    "y": 1187.0,
    "w": 132.0,
    "h": 14.96,
    "text": "Meta",
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
    "id": "stock_15_badge",
    "x": 139.0,
    "y": 1174.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_15_market",
    "x": 140.0,
    "y": 1178.0,
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
    "id": "add_15",
    "x": 334.0,
    "y": 1167.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_15_control",
    "x": 334.0,
    "y": 1167.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_15_bg",
    "x": 334.0,
    "y": 1167.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_15_label",
    "x": 338.0,
    "y": 1176.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_15_rule",
    "x": 24.0,
    "y": 1214.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_16",
    "x": 20.0,
    "y": 1218.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_16_control",
    "x": 20.0,
    "y": 1218.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_16_label",
    "x": 24.0,
    "y": 1238.0,
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
    "id": "stock_16_symbol",
    "x": 24.0,
    "y": 1225.0,
    "w": 112.0,
    "h": 21.76,
    "text": "LLY",
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
    "id": "stock_16_name",
    "x": 24.0,
    "y": 1249.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u793c\u6765",
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
    "id": "stock_16_badge",
    "x": 139.0,
    "y": 1236.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_16_market",
    "x": 140.0,
    "y": 1240.0,
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
    "id": "add_16",
    "x": 334.0,
    "y": 1229.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_16_control",
    "x": 334.0,
    "y": 1229.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_16_bg",
    "x": 334.0,
    "y": 1229.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_16_label",
    "x": 338.0,
    "y": 1238.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_16_rule",
    "x": 24.0,
    "y": 1276.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_17",
    "x": 20.0,
    "y": 1280.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_17_control",
    "x": 20.0,
    "y": 1280.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_17_label",
    "x": 24.0,
    "y": 1300.0,
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
    "id": "stock_17_symbol",
    "x": 24.0,
    "y": 1287.0,
    "w": 112.0,
    "h": 21.76,
    "text": "UNH",
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
    "id": "stock_17_name",
    "x": 24.0,
    "y": 1311.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u8054\u5408\u5065\u5eb7",
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
    "id": "stock_17_badge",
    "x": 139.0,
    "y": 1298.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_17_market",
    "x": 140.0,
    "y": 1302.0,
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
    "id": "add_17",
    "x": 334.0,
    "y": 1291.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_17_control",
    "x": 334.0,
    "y": 1291.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_17_bg",
    "x": 334.0,
    "y": 1291.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_17_label",
    "x": 338.0,
    "y": 1300.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_17_rule",
    "x": 24.0,
    "y": 1338.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_18",
    "x": 20.0,
    "y": 1342.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_18_control",
    "x": 20.0,
    "y": 1342.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_18_label",
    "x": 24.0,
    "y": 1362.0,
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
    "id": "stock_18_symbol",
    "x": 24.0,
    "y": 1349.0,
    "w": 112.0,
    "h": 21.76,
    "text": "XOM",
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
    "id": "stock_18_name",
    "x": 24.0,
    "y": 1373.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u57c3\u514b\u68ee\u7f8e\u5b5a",
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
    "id": "stock_18_badge",
    "x": 139.0,
    "y": 1360.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_18_market",
    "x": 140.0,
    "y": 1364.0,
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
    "id": "add_18",
    "x": 334.0,
    "y": 1353.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_18_control",
    "x": 334.0,
    "y": 1353.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_18_bg",
    "x": 334.0,
    "y": 1353.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_18_label",
    "x": 338.0,
    "y": 1362.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_18_rule",
    "x": 24.0,
    "y": 1400.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_19",
    "x": 20.0,
    "y": 1404.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_19_control",
    "x": 20.0,
    "y": 1404.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_19_label",
    "x": 24.0,
    "y": 1424.0,
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
    "id": "stock_19_symbol",
    "x": 24.0,
    "y": 1411.0,
    "w": 112.0,
    "h": 21.76,
    "text": "TSM",
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
    "id": "stock_19_name",
    "x": 24.0,
    "y": 1435.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u53f0\u79ef\u7535",
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
    "id": "stock_19_badge",
    "x": 139.0,
    "y": 1422.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_19_market",
    "x": 140.0,
    "y": 1426.0,
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
    "id": "add_19",
    "x": 334.0,
    "y": 1415.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_19_control",
    "x": 334.0,
    "y": 1415.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_19_bg",
    "x": 334.0,
    "y": 1415.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_19_label",
    "x": 338.0,
    "y": 1424.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_19_rule",
    "x": 24.0,
    "y": 1462.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_20",
    "x": 20.0,
    "y": 1466.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_20_control",
    "x": 20.0,
    "y": 1466.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_20_label",
    "x": 24.0,
    "y": 1486.0,
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
    "id": "stock_20_symbol",
    "x": 24.0,
    "y": 1473.0,
    "w": 112.0,
    "h": 21.76,
    "text": "V",
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
    "id": "stock_20_name",
    "x": 24.0,
    "y": 1497.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u7ef4\u8428",
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
    "id": "stock_20_badge",
    "x": 139.0,
    "y": 1484.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_20_market",
    "x": 140.0,
    "y": 1488.0,
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
    "id": "add_20",
    "x": 334.0,
    "y": 1477.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_20_control",
    "x": 334.0,
    "y": 1477.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_20_bg",
    "x": 334.0,
    "y": 1477.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_20_label",
    "x": 338.0,
    "y": 1486.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_20_rule",
    "x": 24.0,
    "y": 1524.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_21",
    "x": 20.0,
    "y": 1528.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_21_control",
    "x": 20.0,
    "y": 1528.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_21_label",
    "x": 24.0,
    "y": 1548.0,
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
    "id": "stock_21_symbol",
    "x": 24.0,
    "y": 1535.0,
    "w": 112.0,
    "h": 21.76,
    "text": "WMT",
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
    "id": "stock_21_name",
    "x": 24.0,
    "y": 1559.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u6c83\u5c14\u739b",
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
    "id": "stock_21_badge",
    "x": 139.0,
    "y": 1546.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_21_market",
    "x": 140.0,
    "y": 1550.0,
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
    "id": "add_21",
    "x": 334.0,
    "y": 1539.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_21_control",
    "x": 334.0,
    "y": 1539.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_21_bg",
    "x": 334.0,
    "y": 1539.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_21_label",
    "x": 338.0,
    "y": 1548.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_21_rule",
    "x": 24.0,
    "y": 1586.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_22",
    "x": 20.0,
    "y": 1590.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_22_control",
    "x": 20.0,
    "y": 1590.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_22_label",
    "x": 24.0,
    "y": 1610.0,
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
    "id": "stock_22_symbol",
    "x": 24.0,
    "y": 1597.0,
    "w": 112.0,
    "h": 21.76,
    "text": "JPM",
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
    "id": "stock_22_name",
    "x": 24.0,
    "y": 1621.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u6469\u6839\u5927\u901a",
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
    "id": "stock_22_badge",
    "x": 139.0,
    "y": 1608.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_22_market",
    "x": 140.0,
    "y": 1612.0,
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
    "id": "add_22",
    "x": 334.0,
    "y": 1601.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_22_control",
    "x": 334.0,
    "y": 1601.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_22_bg",
    "x": 334.0,
    "y": 1601.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_22_label",
    "x": 338.0,
    "y": 1610.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_22_rule",
    "x": 24.0,
    "y": 1648.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_23",
    "x": 20.0,
    "y": 1652.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_23_control",
    "x": 20.0,
    "y": 1652.0,
    "w": 366.0,
    "h": 58.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "stock_23_label",
    "x": 24.0,
    "y": 1672.0,
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
    "id": "stock_23_symbol",
    "x": 24.0,
    "y": 1659.0,
    "w": 112.0,
    "h": 21.76,
    "text": "JNJ",
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
    "id": "stock_23_name",
    "x": 24.0,
    "y": 1683.0,
    "w": 132.0,
    "h": 14.96,
    "text": "\u5f3a\u751f",
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
    "id": "stock_23_badge",
    "x": 139.0,
    "y": 1670.0,
    "w": 29.0,
    "h": 21.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "stock_23_market",
    "x": 140.0,
    "y": 1674.0,
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
    "id": "add_23",
    "x": 334.0,
    "y": 1663.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_23_control",
    "x": 334.0,
    "y": 1663.0,
    "w": 36.0,
    "h": 36.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "add_23_bg",
    "x": 334.0,
    "y": 1663.0,
    "w": 36.0,
    "h": 36.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "add_23_label",
    "x": 338.0,
    "y": 1672.0,
    "w": 28.0,
    "h": 17.68,
    "text": "+",
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
    "id": "stock_23_rule",
    "x": 24.0,
    "y": 1710.0,
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

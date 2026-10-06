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
    "text": "Business News",
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
    "h": 791.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "region_0",
    "x": 20.0,
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 127.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 127.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 127.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 122.0,
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
    "y": 127.0,
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
    "id": "related_news_card",
    "x": 20.0,
    "y": 178.0,
    "w": 366.0,
    "h": 216.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "story_0",
    "x": 20.0,
    "y": 178.0,
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
    "y": 178.0,
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
    "y": 221.5,
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
    "y": 186.0,
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
    "y": 209.0,
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
    "y": 219.0,
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
    "y": 219.0,
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
    "y": 230.0,
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
    "y": 281.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "story_1",
    "x": 20.0,
    "y": 286.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_1_control",
    "x": 20.0,
    "y": 286.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_1_label",
    "x": 24.0,
    "y": 329.5,
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
    "id": "story_1_source",
    "x": 24.0,
    "y": 294.0,
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
    "id": "story_1_title_0",
    "x": 24.0,
    "y": 317.0,
    "w": 300.0,
    "h": 21.76,
    "text": "Apple supplier outlook in focus",
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
    "id": "save_1",
    "x": 338.0,
    "y": 327.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_1_control",
    "x": 338.0,
    "y": 327.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_1_label",
    "x": 342.0,
    "y": 338.0,
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
    "id": "story_1_rule",
    "x": 24.0,
    "y": 389.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "story_2",
    "x": 20.0,
    "y": 394.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_2_control",
    "x": 20.0,
    "y": 394.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_2_label",
    "x": 24.0,
    "y": 437.5,
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
    "id": "story_2_source",
    "x": 24.0,
    "y": 402.0,
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
    "id": "story_2_title_0",
    "x": 24.0,
    "y": 425.0,
    "w": 300.0,
    "h": 21.76,
    "text": "What investors are watching this",
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
    "id": "story_2_title_1",
    "x": 24.0,
    "y": 449.0,
    "w": 300.0,
    "h": 21.76,
    "text": "week",
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
    "id": "save_2",
    "x": 338.0,
    "y": 435.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_2_control",
    "x": 338.0,
    "y": 435.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_2_label",
    "x": 342.0,
    "y": 446.0,
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
    "id": "story_2_rule",
    "x": 24.0,
    "y": 497.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "story_3",
    "x": 20.0,
    "y": 502.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_3_control",
    "x": 20.0,
    "y": 502.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_3_label",
    "x": 24.0,
    "y": 545.5,
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
    "id": "story_3_source",
    "x": 24.0,
    "y": 510.0,
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
    "id": "story_3_title_0",
    "x": 24.0,
    "y": 533.0,
    "w": 300.0,
    "h": 21.76,
    "text": "A closer look at hardware demand",
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
    "id": "save_3",
    "x": 338.0,
    "y": 543.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_3_control",
    "x": 338.0,
    "y": 543.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_3_label",
    "x": 342.0,
    "y": 554.0,
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
    "id": "story_3_rule",
    "x": 24.0,
    "y": 605.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "story_4",
    "x": 20.0,
    "y": 610.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_4_control",
    "x": 20.0,
    "y": 610.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_4_label",
    "x": 24.0,
    "y": 653.5,
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
    "id": "story_4_source",
    "x": 24.0,
    "y": 618.0,
    "w": 342.0,
    "h": 14.96,
    "text": "Preview Journal \u00b7 HK",
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
    "id": "story_4_title_0",
    "x": 24.0,
    "y": 641.0,
    "w": 300.0,
    "h": 21.76,
    "text": "\u89c2\u5bdf\u6e2f\u80a1\u79d1\u6280\u677f\u5757",
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
    "id": "save_4",
    "x": 338.0,
    "y": 651.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_4_control",
    "x": 338.0,
    "y": 651.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_4_label",
    "x": 342.0,
    "y": 662.0,
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
    "id": "story_4_rule",
    "x": 24.0,
    "y": 713.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "story_5",
    "x": 20.0,
    "y": 718.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_5_control",
    "x": 20.0,
    "y": 718.0,
    "w": 366.0,
    "h": 105.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "story_5_label",
    "x": 24.0,
    "y": 761.5,
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
    "id": "story_5_source",
    "x": 24.0,
    "y": 726.0,
    "w": 342.0,
    "h": 14.96,
    "text": "Preview Journal \u00b7 CN",
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
    "id": "story_5_title_0",
    "x": 24.0,
    "y": 749.0,
    "w": 300.0,
    "h": 21.76,
    "text": "A\u80a1\u516c\u53f8\u52a8\u6001",
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
    "id": "save_5",
    "x": 338.0,
    "y": 759.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_5_control",
    "x": 338.0,
    "y": 759.0,
    "w": 42.0,
    "h": 40.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "save_5_label",
    "x": 342.0,
    "y": 770.0,
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
    "id": "story_5_rule",
    "x": 24.0,
    "y": 821.0,
    "w": 356.0,
    "h": 0.5,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "news_refresh",
    "x": 20.0,
    "y": 838.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "news_refresh_control",
    "x": 20.0,
    "y": 838.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "news_refresh_bg",
    "x": 20.0,
    "y": 838.0,
    "w": 366.0,
    "h": 44.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "news_refresh_label",
    "x": 24.0,
    "y": 851.0,
    "w": 358.0,
    "h": 17.68,
    "text": "Refresh news",
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

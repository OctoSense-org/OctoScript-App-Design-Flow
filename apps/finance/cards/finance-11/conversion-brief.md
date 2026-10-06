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
    "text": "Settings",
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
    "h": 773.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "preview",
    "x": 20.0,
    "y": 125.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "preview_control",
    "x": 20.0,
    "y": 125.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "preview_bg",
    "x": 20.0,
    "y": 125.0,
    "w": 366.0,
    "h": 50.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "preview_label",
    "x": 24.0,
    "y": 141.0,
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
    "id": "preview_name",
    "x": 36.0,
    "y": 140.0,
    "w": 218.0,
    "h": 20.400000000000002,
    "text": "Preview data",
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
    "id": "preview_value",
    "x": 266.0,
    "y": 140.0,
    "w": 108.0,
    "h": 19.040000000000003,
    "text": "On",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "theme",
    "x": 20.0,
    "y": 183.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "theme_control",
    "x": 20.0,
    "y": 183.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "theme_bg",
    "x": 20.0,
    "y": 183.0,
    "w": 366.0,
    "h": 50.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "theme_label",
    "x": 24.0,
    "y": 199.0,
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
    "id": "theme_name",
    "x": 36.0,
    "y": 198.0,
    "w": 218.0,
    "h": 20.400000000000002,
    "text": "Appearance",
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
    "id": "theme_value",
    "x": 266.0,
    "y": 198.0,
    "w": 108.0,
    "h": 19.040000000000003,
    "text": "Dark",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "language",
    "x": 20.0,
    "y": 241.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "language_control",
    "x": 20.0,
    "y": 241.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "language_bg",
    "x": 20.0,
    "y": 241.0,
    "w": 366.0,
    "h": 50.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "language_label",
    "x": 24.0,
    "y": 257.0,
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
    "id": "language_name",
    "x": 36.0,
    "y": 256.0,
    "w": 218.0,
    "h": 20.400000000000002,
    "text": "Language",
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
    "id": "language_value",
    "x": 266.0,
    "y": 256.0,
    "w": 108.0,
    "h": 19.040000000000003,
    "text": "English",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "colors",
    "x": 20.0,
    "y": 299.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "colors_control",
    "x": 20.0,
    "y": 299.0,
    "w": 366.0,
    "h": 50.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "colors_bg",
    "x": 20.0,
    "y": 299.0,
    "w": 366.0,
    "h": 50.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "colors_label",
    "x": 24.0,
    "y": 315.0,
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
    "id": "colors_name",
    "x": 36.0,
    "y": 314.0,
    "w": 218.0,
    "h": 20.400000000000002,
    "text": "Rising prices",
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
    "id": "colors_value",
    "x": 266.0,
    "y": 314.0,
    "w": 108.0,
    "h": 19.040000000000003,
    "text": "Green",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "providers_title",
    "x": 24.0,
    "y": 380.0,
    "w": 354.0,
    "h": 31.28,
    "text": "Data sources",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 23.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "provider_note",
    "x": 24.0,
    "y": 413.0,
    "w": 354.0,
    "h": 14.96,
    "text": "Keys stay in memory for this session",
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
    "id": "alltick_title",
    "x": 24.0,
    "y": 445.0,
    "w": 352.0,
    "h": 19.040000000000003,
    "text": "AllTick \u00b7 quotes & history",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "alltick_bg",
    "x": 20.0,
    "y": 472.0,
    "w": 366.0,
    "h": 42.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "alltick",
    "x": 30.0,
    "y": 474.0,
    "w": 346.0,
    "h": 38.0,
    "role": "input",
    "native_candidates": [
      "TextInput",
      "KitFormField"
    ]
  },
  {
    "id": "alltick_input",
    "x": 34.0,
    "y": 482.0,
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
    "id": "finnhub_title",
    "x": 24.0,
    "y": 544.0,
    "w": 352.0,
    "h": 19.040000000000003,
    "text": "Finnhub \u00b7 English news",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "finnhub_bg",
    "x": 20.0,
    "y": 571.0,
    "w": 366.0,
    "h": 42.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "finnhub",
    "x": 30.0,
    "y": 573.0,
    "w": 346.0,
    "h": 38.0,
    "role": "input",
    "native_candidates": [
      "TextInput",
      "KitFormField"
    ]
  },
  {
    "id": "finnhub_input",
    "x": 34.0,
    "y": 581.0,
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
    "id": "tushare_title",
    "x": 24.0,
    "y": 643.0,
    "w": 352.0,
    "h": 19.040000000000003,
    "text": "Tushare \u00b7 Chinese news",
    "font_src": "self:resources/ux/Inter-400.ttf",
    "size": 14.0,
    "weight": 400,
    "role": "text",
    "native_candidates": [
      "Label",
      "TextFlow"
    ]
  },
  {
    "id": "tushare_bg",
    "x": 20.0,
    "y": 670.0,
    "w": 366.0,
    "h": 42.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "tushare",
    "x": 30.0,
    "y": 672.0,
    "w": 346.0,
    "h": 38.0,
    "role": "input",
    "native_candidates": [
      "TextInput",
      "KitFormField"
    ]
  },
  {
    "id": "tushare_input",
    "x": 34.0,
    "y": 680.0,
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
    "id": "provider_refresh",
    "x": 20.0,
    "y": 757.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "provider_refresh_control",
    "x": 20.0,
    "y": 757.0,
    "w": 366.0,
    "h": 44.0,
    "role": "button",
    "native_candidates": [
      "Button",
      "KitButton"
    ]
  },
  {
    "id": "provider_refresh_bg",
    "x": 20.0,
    "y": 757.0,
    "w": 366.0,
    "h": 44.0,
    "role": "layout",
    "native_candidates": [
      "View"
    ]
  },
  {
    "id": "provider_refresh_label",
    "x": 24.0,
    "y": 770.0,
    "w": 358.0,
    "h": 17.68,
    "text": "Connect & refresh",
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
    "id": "coverage_note",
    "x": 24.0,
    "y": 819.0,
    "w": 356.0,
    "h": 14.96,
    "text": "Access and history depend on your subscription.",
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
    "id": "sources_note",
    "x": 24.0,
    "y": 842.0,
    "w": 356.0,
    "h": 13.600000000000001,
    "text": "AllTick / Finnhub / Tushare \u00b7 original sources retained",
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

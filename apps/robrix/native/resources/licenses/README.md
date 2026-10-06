# Bundled font notices

The font binaries were imported unchanged from Robrix2. Their embedded name
and copyright tables remain intact. License texts were retrieved from the
font projects on 2026-09-16:

- LXGWWenKaiRegular.ttf: https://github.com/lxgw/LxgwWenKai/blob/main/OFL.txt
- NotoColorEmoji.ttf: https://github.com/googlefonts/noto-emoji/blob/main/fonts/LICENSE
- LiberationMono-Regular.ttf: https://github.com/liberationfonts/liberation-fonts/blob/main/LICENSE

On macOS, generated `system_*` symlinks may resolve to locally installed Apple
fonts. Those symlinks are ignored. Android uses the bundled fallback fonts;
do not distribute macOS system fonts with an Android build.

`native/src/cached_widget.rs` adapts Makepad's cached widget wrapper at the
locked runtime revision. `Makepad-MIT.txt` preserves its copyright and license.

Mobile Latin UI text uses the shared Makepad RobotoFlex.ttf. Its unmodified
font and OFL notice come from the locked framework resources.

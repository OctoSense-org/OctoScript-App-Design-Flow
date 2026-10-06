//! Camera as a standalone app: one window, the Camera module inside it, no
//! window manager. The module is the same `CAMERA_MODULE` the OctoSense
//! shell links in, so this binary and the shell run identical code; only
//! the host around it differs (`octosense-app-host`).
//!
//! The replica's settings come from the environment, as under the shell;
//! `--locale <id>` is the one argument the module's open schema takes.
use makepad_widgets::*;

app_main!(App, font_set: International);

script_mod! {
    use mod.prelude.widgets.*
    use mod.widgets.*

    startup() do #(App::script_component(vm)) {
        ui: Root {
            main_window := Window {
                window.title: "Camera"
                window.inner_size: vec2(412, 892)
                pass +: { clear_color: #000 }
                body +: {
                    padding: 0 margin: 0 spacing: 0
                    host := AppHostView {}
                }
            }
        }
    }
}

#[derive(Script, ScriptHook)]
pub struct App {
    #[live]
    ui: WidgetRef,
    #[rust]
    opened: bool,
}

/// `--locale <id>`, else CAMERA_LOCALE, else the module's default.
fn open_json() -> String {
    let args: Vec<String> = std::env::args().collect();
    let flag = args.windows(2).find(|w| w[0] == "--locale").map(|w| w[1].clone());
    match flag.or_else(|| std::env::var("CAMERA_LOCALE").ok()).filter(|v| !v.is_empty()) {
        Some(locale) => format!("{{{:?}:{:?}}}", "locale", locale),
        None => "{}".to_string(),
    }
}

impl AppMain for App {
    fn script_mod(vm: &mut ScriptVm) -> ScriptValue {
        makepad_widgets::script_mod(vm);
        octosense_app_host::script_mod(vm);
        self::script_mod(vm)
    }

    fn handle_event(&mut self, cx: &mut Cx, event: &Event) {
        if !self.opened {
            self.opened = true;
            octosense_app_host::open_in(&self.ui.widget(cx, ids!(host)), &octosense_camera::CAMERA_MODULE, &open_json());
        }
        self.ui.handle_event(cx, event, &mut Scope::empty());
    }
}

//! In-process Mail controller. Only the UI transport uses device loopback;
//! POP3/SMTP sockets originate on Android and need no desktop companion.
use crate::{
    network::{self, text},
    scenes::{self, SceneFrame},
};
use makepad_widgets::{
    makepad_platform::thread::{ThreadOptions, ThreadSpawner},
    Cx,
};
use serde_json::{json, Value};
use std::{
    collections::HashSet,
    fs::{self, OpenOptions},
    io::{Read, Write},
    net::{TcpListener, TcpStream},
    path::{Path, PathBuf},
    sync::{
        atomic::{AtomicBool, Ordering},
        mpsc::{self, Receiver, SyncSender},
        Arc,
    },
    time::{Duration, Instant},
};

pub struct DeviceRuntime {
    ready: Receiver<Result<String, String>>,
    stop: Arc<AtomicBool>,
}
impl DeviceRuntime {
    pub fn start(cx: &mut Cx) -> Result<Self, String> {
        let config: Value = std::env::var("MAKEPAD_APP_CONFIG")
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or(json!({}));
        let dir = cx
            .os_type()
            .get_data_dir()
            .map(PathBuf::from)
            .unwrap_or_else(|| std::env::temp_dir().join("octosense-native-mail"));
        let (sender, ready) = mpsc::sync_channel(1);
        let stop = Arc::new(AtomicBool::new(false));
        let cancelled = stop.clone();
        let spawner = cx.thread_spawner().clone();
        cx.thread_spawner()
            .spawn_worker(
                ThreadOptions {
                    name: Some("mail-device-controller".into()),
                    ..Default::default()
                },
                move || {
                    if let Err(error) = serve(&dir, &config, &spawner, cancelled, &sender) {
                        let _ = sender.try_send(Err(error));
                    }
                },
            )
            .map_err(|_| "Cannot start the on-device mail service.")?
            .detach();
        Ok(Self { ready, stop })
    }
    pub fn endpoint(&self) -> Option<Result<String, String>> {
        self.ready.try_recv().ok()
    }
    pub fn shutdown(&self) {
        self.stop.store(true, Ordering::Release);
    }
}
impl Drop for DeviceRuntime {
    fn drop(&mut self) {
        self.shutdown();
    }
}

fn atomic(path: &Path, value: &Value) -> Result<(), String> {
    fs::create_dir_all(path.parent().ok_or("Missing mail directory")?)
        .map_err(|_| "Cannot create private mail storage.")?;
    let temporary = path.with_extension("new");
    let mut options = OpenOptions::new();
    options.write(true).truncate(true).create(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }
    let mut file = options
        .open(&temporary)
        .map_err(|_| "Cannot write private mail storage.")?;
    serde_json::to_writer(&mut file, value).map_err(|_| "Cannot save mail data.")?;
    file.sync_all()
        .map_err(|_| "Cannot finish saving mail data.")?;
    fs::rename(temporary, path).map_err(|_| "Cannot finish saving mail data.".into())
}
fn read_json(path: &Path) -> Option<Value> {
    serde_json::from_slice(&fs::read(path).ok()?).ok()
}
fn random_token() -> Result<String, String> {
    let mut bytes = [0u8; 32];
    fs::File::open("/dev/urandom")
        .and_then(|mut f| f.read_exact(&mut bytes))
        .map_err(|_| "Secure random source unavailable.")?;
    Ok(bytes.iter().map(|v| format!("{v:02x}")).collect())
}
fn empty_box(account: &Value) -> Value {
    json!({"address":account["address"],"messages":[],"available":0,"has_more":true,"host":account["host"]})
}

pub fn demo_box() -> Value {
    let mut messages = Vec::new();
    for i in 0..150 {
        let subject = match i {
            0 => "Your weekly design digest".into(),
            1 => "Weekend travel plans".into(),
            149 => "Project Aurora — final notes".into(),
            _ => format!("Project update {i:03}"),
        };
        let html = if i == 0 {
            format!("<h2>A quieter inbox</h2><p>Your Mail app now runs on this phone.</p><table style='border-collapse:collapse;width:100%'><tr><th style='background:#eef5ff;padding:12px'>This week</th><th style='background:#eef5ff;padding:12px'>Status</th></tr><tr><td style='padding:12px'>Design review</td><td>Ready</td></tr><tr><td style='padding:12px'>Android release</td><td>Testing</td></tr></table>{}<p><strong>End of the weekly digest.</strong></p>",(1..=28).map(|n|format!("<p>Note {n}: Find what matters with subject search, read the complete message, and keep your mailbox with you.</p>")).collect::<String>())
        } else {
            String::new()
        };
        let body = if i == 1 {
            (1..=50)
                .map(|n| {
                    format!("Day {n}: A walk by the water, a good coffee, and time to explore.\n\n")
                })
                .collect()
        } else {
            format!("Hello,\n\nHere is update {i:03}. The next review is ready.\n\nBest,\nAlex")
        };
        messages.push(json!({"id":format!("demo-{i}"),"uid":format!("demo-{i}"),"sender":if i==0{"Design Weekly"}else if i==1{"Jamie Chen"}else{"Alex Morgan"},"address":"alex@example.com","subject":subject,"body":body,"preview":if i==0{"Ideas, progress, and a few things worth reading."}else if i==1{"Let's take the scenic route this weekend."}else{"The latest notes and next steps for the project."},"html":html,"date":"2026-09-16T09:24:00Z","time":if i<2{"9:24 AM"}else{"Yesterday"},"unread":i%3==0,"flagged":false,"archived":false,"inline_images":{},"attachment_items":[],"attachments":0,"source":"demo"}));
    }
    json!({"address":"preview@example.com","messages":messages,"available":150,"has_more":false,"host":"pop.gmail.com"})
}
struct Job {
    kind: String,
    account: Value,
    seen: HashSet<String>,
    draft: Value,
    epoch: u64,
}
struct Reply {
    kind: String,
    result: Result<Value, String>,
    epoch: u64,
}
struct Controller {
    state: Value,
    account: Value,
    password: String,
    dir: PathBuf,
    endpoint: String,
    frame: SceneFrame,
    revision: u64,
    sequence: u64,
    sender: SyncSender<Job>,
    results: Receiver<Reply>,
    epoch: u64,
    dirty: bool,
    edit_due: Option<Instant>,
    probe: Option<PathBuf>,
    last_action: String,
}
impl Controller {
    fn new(
        base: &Path,
        config: &Value,
        endpoint: String,
        sender: SyncSender<Job>,
        results: Receiver<Reply>,
    ) -> Result<Self, String> {
        let demo = config["mail_demo"] == true;
        let dir = base.join(if demo { "mail-demo" } else { "mail" });
        fs::create_dir_all(&dir).map_err(|_| "Cannot create mail storage.")?;
        let mut account = read_json(&dir.join("account.json")).unwrap_or_else(network::defaults);
        // Explicit setup import is consumed once into Android's private app data.
        if !demo {
            if let Some(path) = config["mail_bootstrap"].as_str() {
                let path = Path::new(path);
                if let Some(import) = read_json(path) {
                    let candidate = import.get("account").cloned().unwrap_or(import.clone());
                    network::validate(&candidate)?;
                    atomic(&dir.join("account.json"), &candidate)?;
                    account = candidate;
                    if let Some(mailbox) = import.get("mailbox") {
                        atomic(
                            &dir.join(format!("mailbox-{}.json", network::identity(&account))),
                            mailbox,
                        )?;
                    }
                    fs::remove_file(path)
                        .map_err(|_| "Cannot remove the consumed account setup file.")?;
                }
            }
        }
        if demo {
            account = network::defaults();
            account["address"] = json!("preview@example.com");
            account["username"] = json!("preview@example.com");
        }
        let mailbox = if demo {
            demo_box()
        } else {
            read_json(&dir.join(format!("mailbox-{}.json", network::identity(&account))))
                .unwrap_or_else(|| empty_box(&account))
        };
        let mut form = account.clone();
        form.as_object_mut().unwrap().remove("password");
        let mut state = json!({"mailbox":mailbox,"screen":"inbox","folder":"inbox","query":"","search_focused":false,"list_scroll":0,"list_start":0,"selected":"","demo":demo,
            "account_form":form,"password_saved":!text(&account,"password").is_empty(),"password_entry":false,"settings_focus":"","draft":{"to":"","subject":"","body":""},"drafts":[],"busy":false,"notice":"","send_uncertain":false});
        state["drafts"] =
            read_json(&dir.join(format!("drafts-{}.json", network::identity(&account))))
                .filter(Value::is_array)
                .unwrap_or(json!([]));
        let frame = scenes::render(&state, &endpoint, "device-0");
        let probe = config["mail_probe"].as_str().map(PathBuf::from);
        Ok(Self {
            state,
            account,
            password: String::new(),
            dir,
            endpoint,
            frame,
            revision: 0,
            sequence: 0,
            sender,
            results,
            epoch: 0,
            dirty: false,
            edit_due: None,
            probe,
            last_action: String::new(),
        })
    }
    fn save_box(&self) {
        if self.state["demo"] != true {
            let _ = atomic(
                &self
                    .dir
                    .join(format!("mailbox-{}.json", network::identity(&self.account))),
                &self.state["mailbox"],
            );
        }
    }
    fn saved_form(&mut self) {
        let mut form = self.account.clone();
        form.as_object_mut().unwrap().remove("password");
        self.state["account_form"] = form;
        self.state["password_entry"] = json!(false);
        self.state["settings_focus"] = json!("");
        self.password.clear();
    }
    fn mount(&mut self) {
        self.revision += 1;
        self.frame = scenes::render(
            &self.state,
            &self.endpoint,
            &format!("device-{}", self.revision),
        );
        self.sequence = 0;
        self.dirty = false;
        self.edit_due = None;
    }
    fn queue(&mut self, kind: &str, account: Value) {
        if self.state["busy"] == true {
            return;
        }
        if self.state["demo"] == true {
            self.state["notice"] = json!("Demo mailbox · no network requests");
            self.dirty = true;
            return;
        }
        if let Err(error) = network::validate(&account) {
            self.state["notice"] = json!(error);
            self.dirty = true;
            return;
        }
        let seen = self.state["mailbox"]["messages"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|m| m["uid"].as_str().map(str::to_owned))
            .chain(
                self.state["mailbox"]["skipped_uids"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter_map(|v| v.as_str().map(str::to_owned)),
            )
            .collect();
        let draft = self.state["draft"].clone();
        if kind == "send" {
            if self.state["send_uncertain"] == true {
                return;
            }
            if let Err(error) = atomic(&self.dir.join("delivery-pending.json"), &draft) {
                self.state["notice"] = json!(error);
                return;
            }
        }
        match self.sender.try_send(Job {
            kind: kind.into(),
            account,
            seen,
            draft,
            epoch: self.epoch,
        }) {
            Ok(()) => {
                self.state["busy"] = json!(true);
                self.state["notice"] = json!(if kind == "send" {
                    "Sending securely…"
                } else {
                    "Connecting securely…"
                });
                self.dirty = true;
            }
            Err(_) => {
                self.state["notice"] = json!("Mail worker is busy. Try again.");
                self.dirty = true;
            }
        }
    }
    fn poll(&mut self) {
        while let Ok(reply) = self.results.try_recv() {
            if reply.epoch != self.epoch {
                continue;
            }
            self.state["busy"] = json!(false);
            self.dirty = true;
            match reply.result {
                Ok(value) => match reply.kind.as_str() {
                    "test" => {
                        self.state["notice"] = json!(format!(
                            "Connected securely · {} messages available",
                            value["available"]
                        ));
                        self.state["last_connection"] = value;
                    }
                    "fetch" => {
                        let mut existing = self.state["mailbox"]["messages"]
                            .as_array()
                            .cloned()
                            .unwrap_or_default();
                        let count = value["messages"].as_array().map(Vec::len).unwrap_or(0);
                        for message in value["messages"].as_array().into_iter().flatten() {
                            if !existing.iter().any(|m| m["uid"] == message["uid"]) {
                                existing.push(message.clone());
                            }
                        }
                        existing.sort_by(|a, b| text(b, "date").cmp(text(a, "date")));
                        let mut mailbox = value;
                        mailbox["messages"] = existing.into();
                        self.state["mailbox"] = mailbox;
                        self.state["notice"] =
                            json!(format!("Downloaded {count} · on this device"));
                        self.state["last_connection"] = json!({"tls_verified":true,"transport":"device-pop3","downloaded":count});
                        self.save_box();
                        makepad_widgets::log!(
                            "mail: device POP3 TLS verified; downloaded {} messages",
                            count
                        );
                    }
                    "send" => {
                        let _ = fs::remove_file(self.dir.join("delivery-pending.json"));
                        self.state["notice"] = json!("Message sent");
                        self.state["screen"] = json!("inbox");
                        self.state["draft"] = json!({"to":"","subject":"","body":""});
                    }
                    _ => {}
                },
                Err(error) => {
                    if reply.kind == "send" {
                        let uncertain = error.starts_with("Delivery uncertain");
                        self.state["send_uncertain"] = json!(uncertain);
                        if !uncertain {
                            let _ = fs::remove_file(self.dir.join("delivery-pending.json"));
                        }
                    }
                    if reply.kind == "fetch" {
                        self.state["load_failed"] = json!(true);
                    }
                    self.state["notice"] = json!(error);
                }
            }
        }
        if self.edit_due.is_some_and(|t| Instant::now() >= t) {
            self.dirty = true;
        }
        if self.dirty {
            self.mount();
        }
    }
    fn action(&mut self, control: &Value, value: Option<&Value>) {
        let event = text(control, "event");
        let payload = &control["payload"];
        self.last_action = event.into();
        match event {
            "navigate" => {
                self.state["screen"] = payload["screen"].clone();
                self.state["search_focused"] = json!(false);
                if matches!(text(payload, "screen"), "settings" | "mailboxes") {
                    self.saved_form();
                }
                if payload["screen"] == "mailboxes" {
                    self.state["query"] = json!("");
                    self.state["list_scroll"] = json!(0);
                    self.state["list_start"] = json!(0);
                }
            }
            "folder" => {
                self.state["folder"] = payload["folder"].clone();
                self.state["screen"] = json!("inbox");
                self.state["query"] = json!("");
                self.state["list_scroll"] = json!(0);
                self.state["list_start"] = json!(0);
                self.state["search_focused"] = json!(false);
            }
            "open" => {
                self.state["selected"] = payload["id"].clone();
                self.state["screen"] = json!("read");
                self.state["search_focused"] = json!(false);
                let id = payload["id"].clone();
                if let Some(m) = self.state["mailbox"]["messages"]
                    .as_array_mut()
                    .and_then(|a| a.iter_mut().find(|m| m["id"] == id))
                {
                    m["unread"] = json!(false);
                }
                self.save_box();
            }
            "search" => {
                self.state["query"] = value.cloned().unwrap_or(json!(""));
                self.state["search_focused"] = json!(true);
                self.state["list_scroll"] = json!(0);
                self.state["list_start"] = json!(0);
                self.edit_due = Some(Instant::now() + Duration::from_millis(250));
                return;
            }
            "clear_search" => {
                self.state["query"] = json!("");
                self.state["search_focused"] = json!(false);
                self.state["list_scroll"] = json!(0);
                self.state["list_start"] = json!(0);
            }
            "sync" | "load_more" => {
                self.state["load_failed"] = json!(false);
                self.queue("fetch", self.account.clone());
                return;
            }
            "account_test" => {
                let mut a = self.state["account_form"].clone();
                a["password"] = if self.password.is_empty() {
                    self.account["password"].clone()
                } else {
                    json!(self.password)
                };
                self.queue("test", a);
                return;
            }
            "account_field" => {
                if let Some(key) = payload["field"].as_str() {
                    self.state["account_form"][key] = value.cloned().unwrap_or(json!(""));
                    self.state["settings_focus"] = json!(format!("server_{key}"));
                    self.state["notice"] = json!("Unsaved changes");
                }
                self.edit_due = Some(Instant::now() + Duration::from_millis(350));
                return;
            }
            "account_password" => {
                self.state["password_entry"] = json!(true);
                self.password.clear();
            }
            "password" => {
                self.password = value
                    .and_then(Value::as_str)
                    .unwrap_or("")
                    .chars()
                    .filter(|c| !c.is_whitespace())
                    .collect();
                return;
            }
            "account_security" | "smtp_security" => {
                let (key, port) = if event == "account_security" {
                    ("security", "port")
                } else {
                    ("smtp_security", "smtp_port")
                };
                self.state["account_form"][key] = payload["security"].clone();
                self.state["account_form"][port] = json!(match (key, text(payload, "security")) {
                    ("security", "tls") => "995",
                    ("security", _) => "110",
                    (_, "tls") => "465",
                    _ => "587",
                });
                self.state["settings_focus"] = json!("");
            }
            "account_recent" => {
                self.state["account_form"]["recent"] =
                    json!(self.state["account_form"]["recent"] != true);
            }
            "account_save" => {
                let mut a = self.state["account_form"].clone();
                a["password"] = if !self.password.is_empty() {
                    json!(self.password)
                } else if network::identity(&a) == network::identity(&self.account) {
                    self.account["password"].clone()
                } else {
                    json!("")
                };
                match network::validate(&a).and_then(|_| atomic(&self.dir.join("account.json"), &a))
                {
                    Ok(()) => {
                        if network::identity(&a) != network::identity(&self.account) {
                            self.epoch += 1;
                            self.state["busy"] = json!(false);
                            self.state["mailbox"] = read_json(
                                &self
                                    .dir
                                    .join(format!("mailbox-{}.json", network::identity(&a))),
                            )
                            .unwrap_or_else(|| empty_box(&a));
                        }
                        self.account = a;
                        self.saved_form();
                        self.state["password_saved"] = json!(true);
                        self.state["notice"] = json!("Saved on this device");
                    }
                    Err(error) => self.state["notice"] = json!(error),
                }
            }
            "live" => {
                self.state["screen"] = json!("inbox");
            }
            "sample" => {
                self.state["notice"] =
                    json!("Use a separate demo session to keep accounts isolated.");
            }
            "flag" | "archive" | "unread" => {
                let id = self.state["selected"].clone();
                let key = match event {
                    "flag" => "flagged",
                    "archive" => "archived",
                    _ => "unread",
                };
                if let Some(m) = self.state["mailbox"]["messages"]
                    .as_array_mut()
                    .and_then(|a| a.iter_mut().find(|m| m["id"] == id))
                {
                    m[key] = json!(m[key] != true);
                }
                if event != "flag" {
                    self.state["screen"] = json!("inbox");
                }
                self.state["notice"] = json!("Updated on this device");
                self.save_box();
            }
            "compose" | "reply" => {
                let mut draft = json!({"to":"","subject":"","body":"","message_id":format!("<{}@octosense.local>",random_token().unwrap_or_else(|_|network::hash(&self.revision.to_string())))});
                if event == "reply" {
                    if let Some(m) = self.state["mailbox"]["messages"]
                        .as_array()
                        .and_then(|a| a.iter().find(|m| m["id"] == self.state["selected"]))
                    {
                        draft["to"] = m["address"].clone();
                        draft["subject"] = json!(format!("Re: {}", text(m, "subject")));
                        draft["in_reply_to"] = m["message_id"].clone();
                    }
                }
                self.state["draft"] = draft;
                self.state["screen"] = json!("compose");
                self.state["send_uncertain"] =
                    json!(self.dir.join("delivery-pending.json").exists());
                self.state["notice"] = json!("");
            }
            "draft_field" => {
                if let Some(key) = payload["field"].as_str() {
                    self.state["draft"][key] = value.cloned().unwrap_or(json!(""));
                }
                return;
            }
            "save_draft" => {
                let draft = self.state["draft"].clone();
                self.state["drafts"].as_array_mut().unwrap().push(draft);
                let _ = atomic(
                    &self
                        .dir
                        .join(format!("drafts-{}.json", network::identity(&self.account))),
                    &self.state["drafts"],
                );
                self.state["screen"] = json!("inbox");
                self.state["notice"] = json!("Draft saved on this device");
            }
            "send" => {
                self.queue("send", self.account.clone());
                return;
            }
            "open_draft" => {
                if let Some(draft) = payload["index"]
                    .as_u64()
                    .and_then(|i| self.state["drafts"].get(i as usize))
                    .cloned()
                {
                    self.state["draft"] = draft;
                    self.state["screen"] = json!("compose");
                }
            }
            "attachments" => {
                self.state["screen"] = json!("attachments");
            }
            _ => {
                self.state["notice"] =
                    json!("This control is not available in the on-device POP3 view.");
            }
        }
        self.dirty = true;
    }
    fn exchange(&mut self, request: &Value) -> Value {
        if request["nonce"] == self.frame.value["nonce"] {
            if let Some(scroll) = request["scroll"].as_array().and_then(|a| a.first()) {
                if self.edit_due.is_none()
                    && matches!(text(&self.state, "screen"), "inbox" | "search")
                {
                    let y = scroll["y"].as_f64().unwrap_or(0.).max(0.);
                    self.state["list_scroll"] = json!(y);
                    let first = (y / 88.) as usize;
                    let start = self.state["list_start"].as_u64().unwrap_or(0) as usize;
                    let length = scenes::visible(&self.state).len();
                    if (first < start + 4 && start > 0)
                        || (first + 6 > start + 56 && start + 60 < length)
                    {
                        self.state["list_start"] =
                            json!(first.saturating_sub(12).min(length.saturating_sub(60)));
                        self.dirty = true;
                    }
                    if y > 0.
                        && scroll["max_y"].as_f64().unwrap_or(0.) - y < 300.
                        && self.state["mailbox"]["has_more"] == true
                        && text(&self.state, "query").is_empty()
                        && text(&self.state, "folder") == "inbox"
                        && self.state["busy"] != true
                        && !self.state["load_failed"].as_bool().unwrap_or(false)
                    {
                        self.queue("fetch", self.account.clone());
                    }
                }
            }
            for action in request["actions"].as_array().into_iter().flatten() {
                let sequence = action["sequence"].as_u64().unwrap_or(0);
                if sequence <= self.sequence {
                    continue;
                }
                self.sequence = sequence;
                if let Some(control) = self.frame.actions.get(text(action, "id")).cloned() {
                    if control["enabled"] == false {
                        continue;
                    }
                    let kind = text(&action["action"], "kind");
                    if (control["input"] == true) != (kind == "changed") {
                        continue;
                    }
                    self.action(&control, action["action"].get("value"));
                }
            }
            if let Some(path) = &self.probe {
                let probe = json!({"mode":"device","demo":self.state["demo"],"nonce":self.frame.value["nonce"],"screen":self.state["screen"],"message_count":self.state["mailbox"]["messages"].as_array().map(Vec::len).unwrap_or(0),"available":self.state["mailbox"]["available"],"list_start":self.state["list_start"],"list_scroll":self.state["list_scroll"],"busy":self.state["busy"],"last_connection":self.state["last_connection"],"last_action":self.last_action,"mapping":self.frame.mapping,"layout":request["layout"]});
                let _ = atomic(path, &probe);
            }
        }
        self.poll();
        let mut response = json!({"ack":request["sequence"]});
        if request["nonce"] != self.frame.value["nonce"] {
            response["frame"] = self.frame.value.clone();
        }
        response
    }
}

fn serve(
    base: &Path,
    config: &Value,
    spawner: &ThreadSpawner,
    stop: Arc<AtomicBool>,
    ready: &SyncSender<Result<String, String>>,
) -> Result<(), String> {
    let listener =
        TcpListener::bind("127.0.0.1:0").map_err(|_| "Cannot start device-local UI transport.")?;
    listener
        .set_nonblocking(true)
        .map_err(|_| "Cannot configure device UI transport.")?;
    let token = random_token()?;
    let endpoint = format!(
        "http://127.0.0.1:{}/{token}",
        listener.local_addr().unwrap().port()
    );
    let (jobs, receiver) = mpsc::sync_channel::<Job>(2);
    let (sender, results) = mpsc::sync_channel(2);
    let network_stop = stop.clone();
    spawner
        .spawn_worker(
            ThreadOptions {
                name: Some("mail-network".into()),
                ..Default::default()
            },
            move || {
                while !network_stop.load(Ordering::Acquire) {
                    if let Ok(job) = receiver.recv_timeout(Duration::from_millis(100)) {
                        let result = match job.kind.as_str() {
                            "test" => network::test(&job.account),
                            "fetch" => network::fetch(&job.account, &job.seen),
                            "send" => network::send(&job.account, &job.draft),
                            _ => Err("Unknown mail operation.".into()),
                        };
                        let _ = sender.try_send(Reply {
                            kind: job.kind,
                            result,
                            epoch: job.epoch,
                        });
                    }
                }
            },
        )
        .map_err(|_| "Cannot start device network worker.")?
        .detach();
    let mut app = Controller::new(base, config, endpoint.clone(), jobs, results)?;
    ready
        .try_send(Ok(endpoint))
        .map_err(|_| "Mail UI stopped during startup.")?;
    makepad_widgets::log!("mail: independent on-device controller ready");
    while !stop.load(Ordering::Acquire) {
        app.poll();
        match listener.accept() {
            Ok((mut socket, _)) => {
                let _ = handle(&mut socket, &token, &mut app);
            }
            Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                std::thread::sleep(Duration::from_millis(8))
            }
            Err(_) => return Err("Device UI connection closed.".into()),
        }
    }
    Ok(())
}
fn handle(socket: &mut TcpStream, token: &str, app: &mut Controller) -> Result<(), String> {
    // macOS hands accepted sockets the listener's non-blocking flag; the
    // reads below expect a blocking socket with a timeout.
    socket
        .set_nonblocking(false)
        .map_err(|_| "Socket setup failed")?;
    socket
        .set_read_timeout(Some(Duration::from_secs(3)))
        .map_err(|_| "Socket setup failed")?;
    socket
        .set_write_timeout(Some(Duration::from_secs(3)))
        .map_err(|_| "Socket setup failed")?;
    let mut data = Vec::new();
    let mut buffer = [0u8; 8192];
    let header_end;
    loop {
        let n = socket
            .read(&mut buffer)
            .map_err(|_| "Incomplete UI request")?;
        if n == 0 {
            return Err("Empty UI request".into());
        }
        data.extend_from_slice(&buffer[..n]);
        if let Some(end) = data.windows(4).position(|v| v == b"\r\n\r\n") {
            header_end = end + 4;
            break;
        }
        if data.len() > 32768 {
            return Err("Oversized headers".into());
        }
    }
    let headers = std::str::from_utf8(&data[..header_end]).map_err(|_| "Invalid UI headers")?;
    let first = headers.lines().next().unwrap_or("");
    let route = first.split_whitespace().nth(1).unwrap_or("").to_owned();
    let post = first.starts_with("POST ");
    let length = headers
        .lines()
        .filter_map(|line| line.split_once(':'))
        .find(|(key, _)| key.eq_ignore_ascii_case("content-length"))
        .and_then(|(_, v)| v.trim().parse::<usize>().ok())
        .unwrap_or(0);
    if length > 262144 {
        return Err("Oversized UI request".into());
    }
    while data.len() < header_end + length {
        let n = socket
            .read(&mut buffer)
            .map_err(|_| "Incomplete UI request")?;
        if n == 0 {
            return Err("Incomplete UI body".into());
        }
        data.extend_from_slice(&buffer[..n]);
    }
    let (status, content_type, body) = if post && route == format!("/{token}/exchange") {
        let request: Value = serde_json::from_slice(&data[header_end..header_end + length])
            .map_err(|_| "Invalid UI request")?;
        (
            "200 OK",
            "application/json",
            serde_json::to_vec(&app.exchange(&request)).unwrap(),
        )
    } else if let Some(asset) = route.strip_prefix(&format!("/{token}/assets/")) {
        if let Some(value) = app.frame.assets.get(asset) {
            ("200 OK", "image/svg+xml", value.as_bytes().to_vec())
        } else {
            ("404 Not Found", "text/plain", Vec::new())
        }
    } else {
        ("404 Not Found", "text/plain", Vec::new())
    };
    socket.write_all(format!("HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n",body.len()).as_bytes()).and_then(|_|socket.write_all(&body)).map_err(|_|"UI disconnected".into())
}

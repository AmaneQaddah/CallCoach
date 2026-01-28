import json

THEME_CSS = """
<style>
  :root{
    --bg:#f6f8ff;
    --bg2:#ffffff;
    --text:#111827;
    --muted:#6b7280;
    --border:#e5e7eb;
    --primary:#2563eb;
    --ok:#16a34a;
    --danger:#ef4444;
    --shadow: 0 14px 34px rgba(17,24,39,.10);
  }
  *{ box-sizing:border-box; }
  body{
    margin:0;
    padding:18px;
    min-height:100vh;
    background: radial-gradient(900px 500px at 20% 0%, rgba(37,99,235,.10), transparent 65%),
                radial-gradient(900px 500px at 80% 0%, rgba(34,197,94,.10), transparent 65%),
                linear-gradient(180deg, var(--bg), #ffffff);
    color:var(--text);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  }
  body.centerScreen{ display:flex; align-items:center; justify-content:center; padding:26px; }
  body.centerScreen .wrap{ width:min(1100px, 100%); }
  .wrap{ max-width: 1180px; margin: 0 auto; }
  .top{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:14px; }
  .title{ font-size:22px; font-weight:900; letter-spacing:.2px; display:flex; align-items:center; gap:10px; }
  .pill{
    font-size:12px; color:var(--muted);
    border:1px solid var(--border);
    padding:6px 10px; border-radius:999px;
    background: rgba(255,255,255,.70);
  }
  .pill.ok{ color: var(--ok); border-color: rgba(22,163,74,.25); }
  .pill.lock{ color:#b45309; border-color: rgba(245,158,11,.35); }
  .card{
    border:1px solid var(--border);
    border-radius:18px;
    background: rgba(255,255,255,.92);
    padding:16px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(6px);
  }
  .muted{ color: var(--muted); font-size: 13px; line-height: 1.4; }
  .row{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
  .btn{
    appearance:none; border:1px solid var(--border);
    background: rgba(255,255,255,.85);
    color:var(--text);
    padding:12px 14px; border-radius:14px;
    font-weight:900; cursor:pointer;
    transition: .15s ease;
    width: 100%;
    text-align:left;
  }
  .btn:hover{ transform: translateY(-1px); border-color: rgba(37,99,235,.35); }
  .btn.primary{
    border-color: rgba(37,99,235,.25);
    background: linear-gradient(135deg, rgba(37,99,235,.10), rgba(34,197,94,.10));
  }
  .btn:disabled{ opacity:.55; cursor:not-allowed; transform:none !important; }
  .smallbtn{
    width:auto; padding:10px 12px; border-radius: 12px;
    font-weight: 900; border:1px solid var(--border);
    background: rgba(255,255,255,.88);
    color: var(--text); cursor:pointer; transition: .15s ease;
  }
  .smallbtn:hover{ transform: translateY(-1px); border-color: rgba(37,99,235,.35); }
  .field{
    width:100%;
    border:1px solid var(--border);
    background: rgba(255,255,255,.90);
    color: var(--text);
    border-radius:12px;
    padding:12px 12px;
    font-size: 14px;
    outline: none;
  }
  .field:focus{ border-color: rgba(37,99,235,.50); box-shadow: 0 0 0 4px rgba(37,99,235,.12); }
  .gridCards{ display:grid; gap:14px; grid-template-columns: 1fr 1fr 1fr; }
  @media (max-width: 980px){ .gridCards{ grid-template-columns: 1fr; } }
  .sectionTitle{ font-weight:1000; margin: 0 0 10px; display:flex; align-items:center; justify-content:space-between; gap:10px; }
  .status{ display:flex; align-items:center; gap:10px; margin-top:6px; color:var(--muted); font-size:13px; }
  .dot{ width:10px; height:10px; border-radius:50%; background: rgba(107,114,128,.35); box-shadow:0 0 0 4px rgba(107,114,128,.10); }
  .dot.ok{ background: var(--ok); box-shadow:0 0 0 4px rgba(22,163,74,.12); }
  .dot.bad{ background: var(--danger); box-shadow:0 0 0 4px rgba(239,68,68,.12); }
  pre{
    margin:0;
    border:1px solid var(--border);
    background: rgba(249,250,251,.90);
    padding:12px;
    border-radius:14px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 13px;
    line-height: 1.35;
    color: #111827;
  }

  /* Coach toast */
  .toastWrap{
    position: fixed; inset: 0; z-index: 9999;
    display:flex; align-items:flex-start; justify-content:center;
    padding: 16px; pointer-events: none;
  }
  .toast{
    width: min(560px, calc(100vw - 32px));
    pointer-events:none;
    border-radius: 16px;
    padding: 12px 12px;
    opacity: 0;
    transform: translateY(-8px) scale(.98);
    transition: .18s ease;
    box-shadow: 0 18px 45px rgba(17,24,39,.12);
    border:1px solid rgba(37,99,235,.35);
    background: rgba(255,255,255,.96);
  }
  .toast.show{ opacity: 1; transform: translateY(0) scale(1); }
  .toastTitle{ font-weight: 1000; display:flex; justify-content: space-between; align-items:center; gap: 10px; }
  .toastTag{
    font-size: 11px; color: var(--muted);
    border: 1px solid var(--border);
    padding: 4px 8px; border-radius: 999px;
    background: rgba(249,250,251,.90);
  }
  .toastTip{ margin-top: 8px; font-size: 15px; line-height: 1.25; font-weight: 900; color: #111827; }

  .badge{ display:inline-flex; align-items:center; gap:8px; padding:8px 10px; border-radius:999px;
          border:1px solid var(--border); background: rgba(249,250,251,.90); font-weight:1000; }
  .pass{ color: var(--ok); border-color: rgba(22,163,74,.25); }
  .fail{ color: var(--danger); border-color: rgba(239,68,68,.25); }
</style>
"""

def _esc(s: str) -> str:
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


# -------------------------
# Login
# -------------------------
LOGIN_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Login</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
  <style>
    .roleWrap{ display:flex; gap:10px; margin-bottom:12px; }
    @media (max-width: 700px){ .roleWrap{ flex-direction:column; } }
    .roleBtn{
      flex:1;
      border:1px solid var(--border);
      background: rgba(255,255,255,.88);
      color: var(--text);
      padding:12px 12px;
      border-radius:14px;
      font-weight: 1000;
      cursor:pointer;
      transition:.15s ease;
      text-align:left;
    }
    .roleBtn:hover{ transform: translateY(-1px); border-color: rgba(37,99,235,.35); }
    .roleBtn.active{
      border-color: rgba(37,99,235,.45);
      background: linear-gradient(135deg, rgba(37,99,235,.10), rgba(34,197,94,.10));
    }
    .roleTitle{ font-size:14px; font-weight:1000; }
    .roleDesc{ font-size:12px; color: var(--muted); margin-top:6px; line-height:1.25; }
    .err{ color: var(--danger); font-weight: 900; margin-top: 10px; }
  </style>
</head>
<body class="centerScreen">
  <div class="wrap">
    <div class="top">
      <div class="title">🧑‍💼 Training System</div>
      <div class="pill">Login</div>
    </div>

    <div class="card" style="max-width:560px;">
      <div class="roleWrap">
        <button id="roleTrainee" class="roleBtn active" type="button">
          <div class="roleTitle">🎧 Trainee</div>
          <div class="roleDesc">Onboarding + Training + Exam</div>
        </button>

        <button id="roleRecruiter" class="roleBtn" type="button">
          <div class="roleTitle">📊 Recruiter</div>
          <div class="roleDesc">Results</div>
        </button>
      </div>

      <input id="email" class="field" placeholder="Email" type="email" autocomplete="username" />
      <div style="height:10px;"></div>
      <input id="password" class="field" placeholder="Password" type="password" autocomplete="current-password" />

      <div id="err" class="err" style="display:none;"></div>

      <div style="height:14px;"></div>
      <div class="row" style="justify-content:flex-end;">
        <button id="loginBtn" class="smallbtn" style="border-color:rgba(37,99,235,.35);">Sign in</button>
      </div>
    </div>
  </div>

<script>
  const emailEl = document.getElementById("email");
  const passEl  = document.getElementById("password");
  const errEl   = document.getElementById("err");
  const btn     = document.getElementById("loginBtn");

  const roleTraineeBtn = document.getElementById("roleTrainee");
  const roleRecruiterBtn = document.getElementById("roleRecruiter");

  let role = localStorage.getItem("login_role") || "trainee";
  role = (role === "recruiter") ? "recruiter" : "trainee";

  function renderRole(){
    roleTraineeBtn.classList.toggle("active", role === "trainee");
    roleRecruiterBtn.classList.toggle("active", role === "recruiter");
    localStorage.setItem("login_role", role);
  }
  roleTraineeBtn.onclick = () => { role = "trainee"; renderRole(); };
  roleRecruiterBtn.onclick = () => { role = "recruiter"; renderRole(); };
  renderRole();

  async function doLogin(){
    errEl.style.display = "none";
    btn.disabled = true;
    try{
      const resp = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ email: emailEl.value, password: passEl.value, role })
      });
      const data = await resp.json();
      if(!resp.ok) throw new Error(data?.detail || "Login failed");
      window.location.href = data.redirect || "/app";
    }catch(e){
      errEl.textContent = e.message;
      errEl.style.display = "block";
    }finally{
      btn.disabled = false;
    }
  }
  btn.onclick = doLogin;
  passEl.addEventListener("keydown", (e)=>{ if(e.key==="Enter") doLogin(); });
  emailEl.addEventListener("keydown", (e)=>{ if(e.key==="Enter") doLogin(); });
</script>
</body>
</html>
"""

# -------------------------
# Dashboard
# -------------------------
DASHBOARD_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
</head>
<body class="centerScreen">
  <div class="wrap">
    <div class="top">
      <div class="title">🏠 Dashboard</div>
      <div class="row">
        <div class="pill">__USER__</div>
        <button class="smallbtn" onclick="window.location.href='/logout'">Logout</button>
      </div>
    </div>

    <div class="gridCards">
      <div class="card">
        <div class="sectionTitle">📚 Onboarding</div>
        <button class="btn primary" onclick="window.location.href='/onboarding'">Open</button>
      </div>

      <div class="card">
        <div class="sectionTitle">🧠 Training</div>
        __TRAINING_BUTTON__
      </div>

      <div class="card">
        <div class="sectionTitle">✅ Exam (Voice)</div>
        <button class="btn primary" onclick="window.location.href='/exam'">Start</button>
      </div>

      __ADMIN_CARD__
    </div>
  </div>
</body>
</html>
"""

# -------------------------
# Training picker
# -------------------------
TRAINING_PICKER_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Training</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
</head>
<body class="centerScreen">
  <div class="wrap">
    <div class="top">
      <div class="title">🧠 Choose level</div>
      <div class="row">
        <button class="smallbtn" onclick="window.location.href='/app'">Back</button>
      </div>
    </div>

    <div class="card" style="max-width:720px;">
      <div style="display:grid; gap:12px; grid-template-columns:1fr;">
        <button class="btn primary" onclick="chooseLevel('easy')">🙂 Easy</button>
        <button class="btn primary" onclick="chooseLevel('medium')">😐 Medium</button>
        <button class="btn primary" onclick="chooseLevel('hard')">😟 Hard</button>
      </div>
      <div class="muted" style="margin-top:10px;">You will speak with a simulated customer.</div>
    </div>
  </div>

<script>
  function chooseLevel(level){
    localStorage.setItem("call_level", level);
    window.location.href = `/training/live?level=${encodeURIComponent(level)}`;
  }
</script>
</body>
</html>
"""

# -------------------------
# Shared WebRTC JS
# - Collect transcript automatically
# - Coach (training) triggers ONLY on checklist and ONLY ONCE per tag
# -------------------------
WEBRTC_JS = r"""
<script>
  const qs = new URLSearchParams(window.location.search);
  function getLevel(defaultLevel){
    const lv = (qs.get("level") || localStorage.getItem("call_level") || defaultLevel || "easy").toLowerCase();
    return (lv === "easy" || lv === "medium" || lv === "hard") ? lv : "easy";
  }

  let pc = null;
  let micStream = null;
  let transcriptLines = [];
  let transcriptChanged = false;

  // For customer deltas
  let custDelta = "";

  function setDot(state){
    const dot = document.getElementById("dot");
    const txt = document.getElementById("statusText");
    dot.classList.remove("ok","bad");
    if(state === "ready"){ txt.textContent = "Ready"; }
    if(state === "connecting"){ txt.textContent = "Connecting…"; }
    if(state === "live"){ dot.classList.add("ok"); txt.textContent = "Live"; }
    if(state === "error"){ dot.classList.add("bad"); txt.textContent = "Error"; }
    if(state === "ended"){ txt.textContent = "Ended"; }
  }

  function appendLine(role, text){
    const t = (text || "").trim();
    if(!t) return;
    transcriptLines.push(`${role}: ${t}`);
    transcriptChanged = true;

    const box = document.getElementById("transcriptBox");
    if(box){
      box.value = transcriptLines.join("\n");
      box.scrollTop = box.scrollHeight;
    }
  }

  function fullTranscript(){
    return transcriptLines.join("\n").trim();
  }

  async function waitIceComplete(pc){
    if(pc.iceGatheringState === "complete") return;
    await new Promise((resolve) => {
      const check = () => {
        if(pc.iceGatheringState === "complete"){
          pc.removeEventListener("icegatheringstatechange", check);
          resolve();
        }
      };
      pc.addEventListener("icegatheringstatechange", check);
    });
  }

  function setupDataChannel(dc, opts){
    const onRealtimeEvent = opts?.onRealtimeEvent;

    dc.onmessage = (evt) => {
      let msg = null;
      try { msg = JSON.parse(evt.data); } catch { return; }
      if(!msg || !msg.type) return;

      // AGENT transcription (your voice)
      if(msg.type === "conversation.item.input_audio_transcription.completed"){
        appendLine("AGENT", msg.transcript || msg.text || "");
        if(onRealtimeEvent) onRealtimeEvent("agent_turn");
        return;
      }

      // CUSTOMER text transcript (model)
      if(msg.type === "response.audio_transcript.delta"){
        custDelta += (msg.delta || "");
        return;
      }
      if(msg.type === "response.audio_transcript.done"){
        appendLine("CUSTOMER", custDelta || msg.transcript || "");
        custDelta = "";
        if(onRealtimeEvent) onRealtimeEvent("customer_turn");
        return;
      }

      // Some sessions send plain text
      if(msg.type === "response.text.delta"){
        custDelta += (msg.delta || "");
        return;
      }
      if(msg.type === "response.text.done"){
        appendLine("CUSTOMER", custDelta || msg.text || "");
        custDelta = "";
        if(onRealtimeEvent) onRealtimeEvent("customer_turn");
        return;
      }
    };
  }

  async function startCall(opts){
    const level = opts.level;
    const sessionUrl = opts.sessionUrl;
    const onRealtimeEvent = opts.onRealtimeEvent;

    if(pc) return;

    setDot("connecting");

    try{
      micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      pc = new RTCPeerConnection();

      // Local track
      micStream.getTracks().forEach(t => pc.addTrack(t, micStream));

      // Remote audio
      pc.ontrack = (e) => {
        const audio = document.getElementById("remoteAudio");
        if(audio && e.streams && e.streams[0]){
          audio.srcObject = e.streams[0];
          audio.play().catch(()=>{});
        }
      };

      // Data channel
      const dc = pc.createDataChannel("oai-events");
      setupDataChannel(dc, { onRealtimeEvent });

      const offer = await pc.createOffer({ offerToReceiveAudio: true });
      await pc.setLocalDescription(offer);
      await waitIceComplete(pc);

      const resp = await fetch(sessionUrl + `?level=${encodeURIComponent(level)}`, {
        method: "POST",
        headers: { "Content-Type": "application/sdp" },
        body: pc.localDescription.sdp
      });
      const answerSdp = await resp.text();
      if(!resp.ok) throw new Error(answerSdp || "Session failed");

      await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });

      setDot("live");
      document.getElementById("startBtn").disabled = true;
      document.getElementById("endBtn").disabled = false;
      const finishBtn = document.getElementById("finishBtn");
      if(finishBtn) finishBtn.disabled = true;

    }catch(e){
      console.error(e);
      setDot("error");
      stopCall();
      alert("Mic/WebRTC error: " + (e?.message || e));
    }
  }

  function stopCall(){
    try{
      if(pc){ pc.close(); pc = null; }
      if(micStream){
        micStream.getTracks().forEach(t => t.stop());
        micStream = null;
      }
    }catch{}
    document.getElementById("startBtn").disabled = false;
    document.getElementById("endBtn").disabled = true;
    const finishBtn = document.getElementById("finishBtn");
    if(finishBtn) finishBtn.disabled = false;
    setDot("ended");
  }

  // Coach toast (training only)
  let shownTags = new Set();       // "opening", "empathy", ...
  let shownTips = new Set();       // exact tip string
  let coachBusy = false;

  function showToast(titleTag, tip){
    const wrap = document.getElementById("toastWrap");
    const toast = document.getElementById("toast");
    const tag = document.getElementById("toastTag");
    const tipEl = document.getElementById("toastTip");

    if(!wrap || !toast) return;

    tag.textContent = titleTag || "tip";
    tipEl.textContent = tip || "";
    toast.classList.add("show");
    setTimeout(()=> toast.classList.remove("show"), 3200);
  }

  async function maybeCoach(){
    const coachEnabled = !!document.getElementById("coachEnabled");
    if(!coachEnabled) return;
    if(coachBusy) return;
    if(!transcriptChanged) return;

    coachBusy = true;
    transcriptChanged = false;

    try{
      const t = fullTranscript();
      if(!t) return;

      const r = await fetch("/coach", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ transcript: t })
      });
      const data = await r.json();
      if(!r.ok) return;

      const should = !!data.should_intervene;
      const tip = (data.tip || "").trim();
      const tag = (data.reason_tag || "other").trim();
      if(!should || !tip) return;

      // ANTI-REPEAT: show each checklist tag once, and each tip once
      if(shownTags.has(tag)) return;
      if(shownTips.has(tip)) return;

      shownTags.add(tag);
      shownTips.add(tip);

      showToast(tag, tip);

    }catch(e){
      // ignore
    }finally{
      coachBusy = false;
    }
  }

  // throttle coach checks
  setInterval(maybeCoach, 1200);

  window._rt = { startCall, stopCall, fullTranscript, getLevel };
</script>
"""

# -------------------------
# Training LIVE (VOICE + COACH)
# -------------------------
TRAINING_LIVE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Training (Voice)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="title">🎧 Training (Voice)</div>
      <div class="row">
        <button class="smallbtn" onclick="window.location.href='/training'">Back</button>
        <button class="smallbtn" onclick="window.location.href='/app'">Dashboard</button>
      </div>
    </div>

    <div class="card">
      <div class="row" style="justify-content:space-between;">
        <div>
          <div class="sectionTitle">Call status</div>
          <div class="status">
            <div id="dot" class="dot"></div>
            <div id="statusText">Ready</div>
            <div class="pill" id="levelPill">level: —</div>
          </div>
          <div class="muted" style="margin-top:8px;">Speak with the customer. Coach pops only when needed.</div>
        </div>

        <div class="row">
          <button id="startBtn" class="smallbtn" style="border-color:rgba(37,99,235,.35);">Start call</button>
          <button id="endBtn" class="smallbtn" disabled>End call</button>
          <button id="finishBtn" class="smallbtn" disabled>Finish & report</button>
        </div>
      </div>

      <div style="height:14px;"></div>

      <div class="row" style="gap:14px; align-items:flex-start;">
        <div style="flex:1;">
          <div class="sectionTitle">Transcript (hidden by default)</div>
          <textarea id="transcriptBox" class="field" style="height:260px; font-family: ui-monospace, Menlo, Consolas, monospace;" placeholder="Auto transcript will appear here…"></textarea>
          <div class="muted" style="margin-top:8px;">You don’t need to paste anything.</div>
        </div>

        <div style="width:320px;">
          <div class="sectionTitle">Tips</div>
          <div class="muted">Coach is enabled. It will not repeat the same checklist item.</div>
          <div style="height:10px;"></div>
          <div class="pill ok">Checklist-based</div>
          <input id="coachEnabled" type="hidden" value="1" />
        </div>
      </div>

      <audio id="remoteAudio" autoplay></audio>
    </div>
  </div>

  <div class="toastWrap" id="toastWrap">
    <div class="toast" id="toast">
      <div class="toastTitle">
        <div>Coach</div>
        <div class="toastTag" id="toastTag">tip</div>
      </div>
      <div class="toastTip" id="toastTip"></div>
    </div>
  </div>

  __WEBRTC_JS__

<script>
  const level = window._rt.getLevel("easy");
  document.getElementById("levelPill").textContent = "level: " + level;

  document.getElementById("startBtn").onclick = async () => {
    await window._rt.startCall({
      level,
      sessionUrl: "/session",
      onRealtimeEvent: (t) => { /* optional */ }
    });
  };

  document.getElementById("endBtn").onclick = () => window._rt.stopCall();

  document.getElementById("finishBtn").onclick = async () => {
    const t = window._rt.fullTranscript();
    if(!t){
      alert("No transcript collected yet. Speak first.");
      return;
    }
    try{
      const r = await fetch("/aftercall", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ transcript: t, level })
      });
      const data = await r.json();
      if(!r.ok) throw new Error(data?.detail || "aftercall failed");
      window.location.href = `/training/report/${data.attempt_id}`;
    }catch(e){
      alert(e.message || e);
    }
  };
</script>
</body>
</html>
"""

# -------------------------
# Exam LIVE (VOICE) ✅✅✅  (NO PASTE TRANSCRIPT)
# -------------------------
EXAM_LIVE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Exam (Voice)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="title">✅ Exam (Voice)</div>
      <div class="row">
        <button class="smallbtn" onclick="window.location.href='/app'">Dashboard</button>
      </div>
    </div>

    <div class="card">
      <div class="row" style="justify-content:space-between;">
        <div>
          <div class="sectionTitle">Choose level</div>
          <div class="row">
            <select id="levelSel" class="field" style="max-width:220px;">
              <option value="easy">Easy</option>
              <option value="medium" selected>Medium</option>
              <option value="hard">Hard</option>
            </select>
            <div class="status">
              <div id="dot" class="dot"></div>
              <div id="statusText">Ready</div>
            </div>
          </div>
          <div class="muted" style="margin-top:8px;">This is a graded voice call. No coach tips.</div>
        </div>

        <div class="row">
          <button id="startBtn" class="smallbtn" style="border-color:rgba(37,99,235,.35);">Start exam call</button>
          <button id="endBtn" class="smallbtn" disabled>End call</button>
          <button id="finishBtn" class="smallbtn" disabled>Finish & grade</button>
        </div>
      </div>

      <div style="height:14px;"></div>

      <div class="row" style="gap:14px; align-items:flex-start;">
        <div style="flex:1;">
          <div class="sectionTitle">Transcript (auto)</div>
          <textarea id="transcriptBox" class="field" style="height:260px; font-family: ui-monospace, Menlo, Consolas, monospace;" placeholder="Auto transcript will appear here…"></textarea>
          <div class="muted" style="margin-top:8px;">No pasting. We collect it automatically.</div>
        </div>

        <div style="width:320px;">
          <div class="sectionTitle">Exam rules</div>
          <div class="muted">
            Speak naturally. When finished, click “Finish & grade”.
          </div>
        </div>
      </div>

      <audio id="remoteAudio" autoplay></audio>
    </div>
  </div>

  __WEBRTC_JS__

<script>
  const sel = document.getElementById("levelSel");
  const saved = (localStorage.getItem("exam_level") || "medium").toLowerCase();
  if(saved) sel.value = saved;

  sel.onchange = () => localStorage.setItem("exam_level", sel.value);

  document.getElementById("startBtn").onclick = async () => {
    const level = sel.value;
    await window._rt.startCall({
      level,
      sessionUrl: "/session",
      onRealtimeEvent: (t) => { /* no coach */ }
    });
  };

  document.getElementById("endBtn").onclick = () => window._rt.stopCall();

  document.getElementById("finishBtn").onclick = async () => {
    const level = sel.value;
    const t = window._rt.fullTranscript();
    if(!t){
      alert("No transcript collected yet. Speak first.");
      return;
    }
    try{
      const r = await fetch("/grade", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ transcript: t, level })
      });
      const data = await r.json();
      if(!r.ok) throw new Error(data?.detail || "grade failed");
      window.location.href = `/exam/report/${data.attempt_id}`;
    }catch(e){
      alert(e.message || e);
    }
  };
</script>
</body>
</html>
"""

# -------------------------
# Onboarding page
# -------------------------
ONBOARDING_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Onboarding</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
  <style>
    .box{ border:1px solid var(--border); border-radius:16px; padding:16px; background: rgba(255,255,255,.92); }
    .links{ display:flex; gap:10px; flex-wrap:wrap; margin-top:12px; }
    .chip{
      border:1px solid var(--border);
      padding:10px 12px;
      border-radius:999px;
      background: rgba(249,250,251,.90);
      cursor:pointer;
      font-weight:900;
      font-size:13px;
    }
    .chip:hover{ transform: translateY(-1px); border-color: rgba(37,99,235,.35); }
    .doneBtn{
      margin-top:14px;
      width:100%;
      padding:12px 14px;
      border-radius:12px;
      font-weight:1000;
      border:1px solid var(--border);
      background: linear-gradient(135deg, rgba(37,99,235,.10), rgba(34,197,94,.10));
      cursor:pointer;
    }
    .doneBtn:disabled{ opacity:.55; cursor:not-allowed; }
  </style>
</head>
<body class="centerScreen">
  <div class="wrap">
    <div class="top">
      <div class="title">📚 Onboarding</div>
      <div class="row">
        <button class="smallbtn" onclick="window.location.href='/app'">Back</button>
      </div>
    </div>

    <div class="card" style="max-width:820px;">
      <div class="box">
        <div class="muted">Complete onboarding before Training is unlocked.</div>
        <div class="links">
          <div class="chip" onclick="window.open('__PDF__','_blank')">📄 PDF</div>
          <div class="chip" onclick="window.open('__VIDEO__','_blank')">▶️ Video</div>
        </div>

        <button class="doneBtn" id="doneBtn">Mark done ✓</button>
        <div id="msg" class="muted" style="margin-top:10px;"></div>
      </div>
    </div>
  </div>

<script>
  const btn = document.getElementById("doneBtn");
  const msg = document.getElementById("msg");

  const alreadyDone = (__DONE__ === true);
  if(alreadyDone){
    btn.disabled = true;
    msg.textContent = "Done ✓";
  }

  btn.onclick = async () => {
    btn.disabled = true;
    msg.textContent = "";
    try{
      const r = await fetch("/onboarding/done", { method:"POST" });
      const data = await r.json();
      if(!r.ok) throw new Error(data?.detail || "Error");
      msg.textContent = "Done ✓";
      setTimeout(()=> window.location.href="/app", 350);
    }catch(e){
      msg.textContent = "Error";
      btn.disabled = false;
    }
  };
</script>
</body>
</html>
"""

# -------------------------
# Admin (minimal)
# -------------------------
ADMIN_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Admin</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  __THEME_CSS__
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="title">🛠 Admin</div>
      <div class="row">
        <div class="pill">__USER__</div>
        <button class="smallbtn" onclick="window.location.href='/logout'">Logout</button>
      </div>
    </div>

    <div class="card">
      <div class="sectionTitle">Attempts</div>
      <div class="muted" id="msg">Loading…</div>
      <div style="height:10px;"></div>
      <div id="list"></div>
    </div>
  </div>

<script>
  async function load(){
    const msg = document.getElementById("msg");
    const list = document.getElementById("list");
    try{
      const r = await fetch("/admin/api/attempts");
      const data = await r.json();
      if(!r.ok) throw new Error(data?.detail || "Error");
      msg.textContent = "";
      const items = data.items || [];
      list.innerHTML = items.map(a => {
        const id = a.id;
        const mode = a.mode || "";
        const lvl = a.level || "";
        const user = a.user_email || "";
        const when = a.created_at || "";
        const href = (mode === "exam") ? `/exam/report/${id}` : `/training/report/${id}`;
        return `
          <div class="mini" style="padding:10px;border:1px solid var(--border);border-radius:14px;margin-bottom:10px;background:rgba(249,250,251,.9);">
            <div style="font-weight:1000">${mode.toUpperCase()} #${id} <span class="pill">lvl: ${lvl}</span></div>
            <div class="muted">${user} ${when ? "• " + when : ""}</div>
            <div style="height:8px;"></div>
            <button class="smallbtn" onclick="window.location.href='${href}'">Open report</button>
          </div>
        `;
      }).join("");
    }catch(e){
      msg.textContent = e.message || "Error";
    }
  }
  load();
</script>
</body>
</html>
"""

# -------------------------
# Reports (robust parsing)
# -------------------------
def _parse_json_any(x):
    if x is None:
        return {}
    if isinstance(x, dict):
        return x
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return {}
        # try direct json
        try:
            return json.loads(s)
        except Exception:
            # try extracting {...}
            try:
                i = s.find("{")
                j = s.rfind("}")
                if i >= 0 and j > i:
                    return json.loads(s[i:j+1])
            except Exception:
                return {}
    return {}

def build_training_report_html(a: dict) -> str:
    lvl = _esc(a.get("level",""))
    score = int(a.get("checklist_score", 0) or 0)
    raw = a.get("checklist_json","") or ""
    rep = _parse_json_any(raw)
    items = rep.get("items") or []
    highlights = rep.get("highlights") or []
    improvements = rep.get("improvements") or []
    next_say = rep.get("next_time_say") or []

    def pill():
        return f'<div class="pill">Level: {lvl}</div>'

    def render_items():
        if not items:
            return f"<div class='muted'>Could not parse checklist output.</div><pre>{_esc(str(raw))}</pre>"
        rows = []
        for it in items:
            st = (it.get("status") or "").lower()
            badge = "pill ok" if st=="done" else ("pill lock" if st=="partial" else "pill")
            rows.append(f"""
              <div style="padding:10px;border:1px solid var(--border);border-radius:14px;background:rgba(249,250,251,.9);margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
                  <div style="font-weight:1000">{_esc(it.get("title",""))}</div>
                  <div class="{badge}">{_esc(st or "missing")}</div>
                </div>
                <div class="muted" style="margin-top:6px;">Evidence: {_esc(it.get("evidence",""))}</div>
                <div class="muted">Note: {_esc(it.get("note",""))}</div>
              </div>
            """)
        return "\n".join(rows)

    def render_list(arr):
        if not arr:
            return "<div class='muted'>—</div>"
        return "<ul>" + "".join([f"<li>{_esc(str(x))}</li>" for x in arr]) + "</ul>"

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Training report</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  {THEME_CSS}
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="title">📄 Training report</div>
      <div class="row">
        {pill()}
        <button class="smallbtn" onclick="window.location.href='/training'">New training</button>
        <button class="smallbtn" onclick="window.location.href='/app'">Dashboard</button>
      </div>
    </div>

    <div class="card">
      <div class="row" style="justify-content:space-between;">
        <div class="sectionTitle">Checklist</div>
        <div class="pill">{score}%</div>
      </div>

      <div style="height:10px;"></div>
      {render_items()}

      <div style="height:12px;"></div>
      <div class="row" style="gap:14px; align-items:stretch;">
        <div class="card" style="flex:1;">
          <div class="sectionTitle">✨ Highlights</div>
          {render_list(highlights)}
        </div>
        <div class="card" style="flex:1;">
          <div class="sectionTitle">🧩 Improve</div>
          {render_list(improvements)}
        </div>
      </div>

      <div style="height:12px;"></div>
      <div class="card">
        <div class="sectionTitle">💬 Try saying</div>
        {render_list(next_say)}
      </div>
    </div>
  </div>
</body>
</html>
"""
    return html

def build_exam_report_html(a: dict) -> str:
    lvl = _esc(a.get("level",""))
    score = int(a.get("score", 0) or 0)
    passed = bool(a.get("passed", 0))
    badge = "badge pass" if passed else "badge fail"
    summary = _esc(a.get("summary","") or "")
    strengths = _parse_json_any(a.get("strengths","[]"))
    improvements = _parse_json_any(a.get("improvements","[]"))
    checklist_raw = a.get("checklist_json","") or ""
    checklist = _parse_json_any(checklist_raw)
    checklist_score = int(a.get("checklist_score", 0) or 0)

    def render_list(arr):
        if not arr:
            return "<div class='muted'>—</div>"
        return "<ul>" + "".join([f"<li>{_esc(str(x))}</li>" for x in arr]) + "</ul>"

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Exam report</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  {THEME_CSS}
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="title">📄 Exam report</div>
      <div class="row">
        <div class="pill">Level: {lvl}</div>
        <button class="smallbtn" onclick="window.location.href='/exam'">New exam</button>
        <button class="smallbtn" onclick="window.location.href='/app'">Dashboard</button>
      </div>
    </div>

    <div class="card">
      <div class="row" style="justify-content:space-between;">
        <div class="{badge}">{'PASS' if passed else 'FAIL'}</div>
        <div class="pill">Score: {score}</div>
        <div class="pill">Checklist: {checklist_score}%</div>
      </div>

      <div style="height:12px;"></div>
      <div class="card">
        <div class="sectionTitle">Summary</div>
        <div class="muted">{summary or '—'}</div>
      </div>

      <div style="height:12px;"></div>
      <div class="row" style="gap:14px; align-items:stretch;">
        <div class="card" style="flex:1;">
          <div class="sectionTitle">Strengths</div>
          {render_list(strengths if isinstance(strengths, list) else [])}
        </div>
        <div class="card" style="flex:1;">
          <div class="sectionTitle">Improvements</div>
          {render_list(improvements if isinstance(improvements, list) else [])}
        </div>
      </div>

      <div style="height:12px;"></div>
      <div class="card">
        <div class="sectionTitle">Checklist details</div>
        <pre>{_esc(json.dumps(checklist, ensure_ascii=False, indent=2)) if checklist else _esc(str(checklist_raw))}</pre>
      </div>
    </div>
  </div>
</body>
</html>
"""
    return html


# -------------------------
# Builders
# -------------------------
def build_login_html() -> str:
    return LOGIN_HTML.replace("__THEME_CSS__", THEME_CSS)

def build_dashboard_html(user_email: str, show_admin: bool = False, training_enabled: bool = True) -> str:
    safe_user = _esc(user_email or "")

    admin_card = ""
    if show_admin:
        admin_card = """
          <div class="card">
            <div class="sectionTitle">🛠 Admin</div>
            <button class="btn" onclick="window.location.href='/admin'">Open</button>
          </div>
        """.strip()

    if training_enabled:
        training_btn = """<button class="btn primary" onclick="window.location.href='/training'">Start</button>"""
    else:
        training_btn = """<button class="btn" onclick="window.location.href='/onboarding'">Locked</button>"""

    return (
        DASHBOARD_HTML.replace("__THEME_CSS__", THEME_CSS)
        .replace("__USER__", safe_user)
        .replace("__ADMIN_CARD__", admin_card)
        .replace("__TRAINING_BUTTON__", training_btn)
    )

def build_training_picker_html() -> str:
    return TRAINING_PICKER_HTML.replace("__THEME_CSS__", THEME_CSS)

def build_training_live_html() -> str:
    return (TRAINING_LIVE_HTML
            .replace("__THEME_CSS__", THEME_CSS)
            .replace("__WEBRTC_JS__", WEBRTC_JS))

def build_exam_html() -> str:
    return (EXAM_LIVE_HTML
            .replace("__THEME_CSS__", THEME_CSS)
            .replace("__WEBRTC_JS__", WEBRTC_JS))

def build_admin_html(user_email: str) -> str:
    safe_user = _esc(user_email or "")
    return ADMIN_HTML.replace("__THEME_CSS__", THEME_CSS).replace("__USER__", safe_user)

def build_onboarding_html(cfg: dict, done: bool = False) -> str:
    pdf_url = (cfg or {}).get("pdf_url") or "/static/onboarding.pdf"
    video_url = (cfg or {}).get("video_url") or "https://www.youtube.com/"
    html = ONBOARDING_HTML.replace("__THEME_CSS__", THEME_CSS)
    html = html.replace("__PDF__", (pdf_url or "").replace("<","").replace(">",""))
    html = html.replace("__VIDEO__", (video_url or "").replace("<","").replace(">",""))
    html = html.replace("__DONE__", "true" if done else "false")
    return html

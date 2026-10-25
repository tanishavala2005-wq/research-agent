import time
import html as html_lib
from urllib.parse import urlparse

import streamlit as st
from pdf_export import make_pdf
from graph import build_graph

st.set_page_config(page_title="Multi-Agent Research Assistant", page_icon="🔬", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0b0f1f, #151b3b, #0e2a47, #1a1040);
    background-size: 400% 400%;
    animation: bgmove 18s ease infinite;
    color: #e8ecff;
}
@keyframes bgmove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
header[data-testid="stHeader"] {background: transparent;}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li, .stApp label {color: #e8ecff;}

/* Step headers */
.step {display:flex; align-items:center; gap:14px; margin: 30px 0 12px 0;}
.step .num {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #6a5cff, #00d4ff);
    display:flex; align-items:center; justify-content:center;
    font-weight: 800; color: white; font-size: 17px;
    box-shadow: 0 0 18px rgba(0,212,255,0.5);
    flex-shrink: 0;
}
.step .ttl {font-size: 20px; font-weight: 700; color: #ffffff;}
.step .sub {font-size: 13px; opacity: .65; margin-top: 2px;}
.hint {font-size: 13px; opacity: .65; margin: 6px 0 8px 2px;}
.placeholder {
    border: 1px dashed rgba(255,255,255,0.25);
    border-radius: 16px; padding: 30px; text-align: center; opacity: .6;
}

/* Input box */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background-color: #eef1ff !important;
    border-radius: 14px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
.stTextInput input,
input[type="text"] {
    background-color: #eef1ff !important;
    color: #0b0f1f !important;
    -webkit-text-fill-color: #0b0f1f !important;
    caret-color: #6a5cff !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    padding: 14px !important;
}
div[data-baseweb="input"] input::placeholder,
.stTextInput input::placeholder {
    color: #6b7399 !important;
    -webkit-text-fill-color: #6b7399 !important;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    background: linear-gradient(90deg, #6a5cff, #00d4ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    box-shadow: 0 0 20px rgba(106,92,255,0.5);
    transition: transform .2s, box-shadow .2s;
}
.stButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 0 35px rgba(0,212,255,0.7);
}

/* Example chips */
.st-key-chips button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(120,140,255,0.45) !important;
    box-shadow: none !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border-radius: 999px !important;
    color: #cfd6ff !important;
}
.st-key-chips button:hover {
    background: rgba(106,92,255,0.35) !important;
    box-shadow: 0 0 16px rgba(0,212,255,0.5) !important;
}

/* Agent cards */
.pipe {display: flex; gap: 16px; margin: 10px 0; flex-wrap: wrap;}
.agent {
    flex: 1; min-width: 180px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    transition: all .4s;
}
.agent .icon {font-size: 34px;}
.agent .name {font-weight: 700; margin-top: 6px;}
.agent .desc {font-size: 12px; opacity: .7; margin-top: 4px;}
.agent .status {margin-top: 10px; font-size: 12px; font-weight: 600; letter-spacing: 1px;}
.agent .time {font-size: 11px; opacity: .65; margin-top: 4px; min-height: 14px;}
.agent.waiting {opacity: .45;}
.agent.running {border-color: #00d4ff; animation: pulse 1.3s infinite;}
.agent.done {border-color: #2ee59d; box-shadow: 0 0 18px rgba(46,229,157,0.35);}
.agent.done .status {color: #2ee59d;}
.agent.running .status {color: #00d4ff;}
@keyframes pulse {
    0% {box-shadow: 0 0 0 0 rgba(0,212,255,0.6);}
    70% {box-shadow: 0 0 0 18px rgba(0,212,255,0);}
    100% {box-shadow: 0 0 0 0 rgba(0,212,255,0);}
}

/* Metrics */
.metric {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px; padding: 16px; text-align: center;
}
.metric .num {font-size: 28px; font-weight: 800; color: #00d4ff;}
.metric .lbl {font-size: 12px; opacity: .7;}

/* Source cards */
.src {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-left: 4px solid #6a5cff;
    border-radius: 12px; padding: 12px 16px; margin-bottom: 10px;
}
.src a {color: #8fe9ff !important; text-decoration: none; font-weight: 600;}
.src a:hover {text-decoration: underline;}
.src .dom {font-size: 12px; opacity: .65; margin-top: 2px;}

/* Trace */
.trace {
    font-family: Consolas, monospace; font-size: 13px;
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 14px 16px;
}
.trace .row {padding: 3px 0;}
.trace .t {color: #7f8bd6;}
.trace .ok {color: #2ee59d;}
.trace .warn {color: #ffb86b;}

/* Expander (Critic's final feedback) dark theme */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {
    background: transparent !important;
    color: #e8ecff !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    color: #e8ecff !important;
    fill: #e8ecff !important;
    opacity: 1 !important;
}

/* Hide Deploy + scrollbars */
.stAppDeployButton, [data-testid="stAppDeployButton"] {display: none !important;}
::-webkit-scrollbar {display: none;}
html, body, .stApp, [data-testid="stAppViewContainer"], section.main, .main {
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}

/* Running indicator visible */
[data-testid="stStatusWidget"],
[data-testid="stStatusWidget"] * {color: #00d4ff !important; opacity: 1 !important;}
[data-testid="stStatusWidget"] img,
[data-testid="stStatusWidget"] svg {filter: invert(1) brightness(2) !important; opacity: 1 !important;}
[data-testid="stStatusWidget"] button {color: #ffffff !important; font-weight: 600 !important;}
[data-testid="stToolbar"] button,
[data-testid="stToolbar"] svg {color: #e8ecff !important; fill: #e8ecff !important; opacity: 1 !important;}
</style>
""", unsafe_allow_html=True)

# ---------- 3D hero ----------
HERO = """
<style>
  html, body {margin:0; padding:0; overflow:hidden !important; background:transparent;}
  ::-webkit-scrollbar { display: none; }
</style>
<div id="wrap" style="position:relative;width:100%;height:280px;font-family:sans-serif;overflow:hidden;">
  <div id="c" style="position:absolute;inset:0;overflow:hidden;"></div>
  <div style="position:absolute;inset:0;display:flex;flex-direction:column;
              align-items:center;justify-content:center;pointer-events:none;text-align:center;">
    <div style="font-size:42px;font-weight:800;color:white;
                text-shadow:0 0 25px rgba(0,212,255,0.8);">Multi-Agent Research Assistant</div>
    <div style="color:#aab4ff;margin-top:8px;">Give a topic. Four AI agents research it and write a cited report.</div>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const el = document.getElementById('c');
const W = el.clientWidth, H = 280;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 100);
camera.position.z = 7;
const renderer = new THREE.WebGLRenderer({alpha: true, antialias: true});
renderer.setSize(W, H);
renderer.domElement.style.display = 'block';
el.appendChild(renderer.domElement);

const group = new THREE.Group();
scene.add(group);

const colors = [0x6a5cff, 0x00d4ff, 0x2ee59d, 0xff6ad5];
const nodes = [];
for (let i = 0; i < 4; i++) {
  const a = (i / 4) * Math.PI * 2;
  const m = new THREE.Mesh(
    new THREE.SphereGeometry(0.35, 32, 32),
    new THREE.MeshBasicMaterial({color: colors[i]})
  );
  m.position.set(Math.cos(a) * 3, Math.sin(a) * 1.2, Math.sin(a) * 1.5);
  group.add(m);
  nodes.push(m);
}
for (let i = 0; i < 4; i++) {
  const geo = new THREE.BufferGeometry().setFromPoints(
    [nodes[i].position, nodes[(i + 1) % 4].position]
  );
  group.add(new THREE.Line(geo, new THREE.LineBasicMaterial({color: 0x8899ff, transparent: true, opacity: 0.6})));
}

const pts = [];
for (let i = 0; i < 400; i++) {
  pts.push((Math.random() - 0.5) * 18, (Math.random() - 0.5) * 8, (Math.random() - 0.5) * 10);
}
const pg = new THREE.BufferGeometry();
pg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
const particles = new THREE.Points(pg, new THREE.PointsMaterial({color: 0x99aaff, size: 0.04}));
scene.add(particles);

let mx = 0, my = 0;
window.addEventListener('mousemove', (e) => {
  mx = (e.clientX / window.innerWidth - 0.5) * 2;
  my = (e.clientY / 280 - 0.5) * 2;
});

let t = 0;
function animate() {
  requestAnimationFrame(animate);
  t += 0.02;
  group.rotation.y += 0.006;
  particles.rotation.y -= 0.0008;
  camera.position.x += (mx * 0.8 - camera.position.x) * 0.05;
  camera.position.y += (-my * 0.4 - camera.position.y) * 0.05;
  camera.lookAt(0, 0, 0);
  nodes.forEach((n, i) => n.scale.setScalar(1 + Math.sin(t + i) * 0.2));
  renderer.render(scene, camera);
}
animate();
</script>
"""
st.iframe(HERO, height=300)

# ---------- Config ----------
AGENTS = [
    ("planner", "🧠", "Planner", "Splits topic into questions"),
    ("researcher", "🔎", "Researcher", "Searches the web"),
    ("writer", "✍️", "Writer", "Drafts a cited report"),
    ("critic", "🕵️", "Critic", "Fact-checks the draft"),
]
STATUS_TEXT = {"waiting": "WAITING", "running": "WORKING...", "done": "DONE ✓"}
NEXT = {"planner": "researcher", "researcher": "writer", "writer": "critic"}
EXAMPLES = [
    "Impact of AI on healthcare diagnostics",
    "Future of quantum computing",
    "Large language models in education",
    "Renewable energy storage technologies",
]


def step(n, title, sub):
    st.markdown(
        f'<div class="step"><div class="num">{n}</div>'
        f'<div><div class="ttl">{title}</div><div class="sub">{sub}</div></div></div>',
        unsafe_allow_html=True,
    )


def pipeline_html(states, times):
    out = '<div class="pipe">'
    for key, icon, name, desc in AGENTS:
        s = states[key]
        t = f"{times[key]:.1f}s" if key in times else ""
        out += (
            f'<div class="agent {s}">'
            f'<div class="icon">{icon}</div>'
            f'<div class="name">{name}</div>'
            f'<div class="desc">{desc}</div>'
            f'<div class="status">{STATUS_TEXT[s]}</div>'
            f'<div class="time">{t}</div>'
            f'</div>'
        )
    return out + "</div>"


def set_topic(value):
    st.session_state["topic_input"] = value


def describe(node, state):
    if node == "planner":
        return f"Split the topic into {len(state['questions'])} research questions"
    if node == "researcher":
        return f"Collected {len(state['sources'])} sources from the web"
    if node == "writer":
        return f"Drafted a report ({len(state['report'].split())} words)"
    if node == "critic":
        if "APPROVED" in state["feedback"]:
            return "APPROVED the report"
        return "Found issues, sent the report back to the Writer"
    return ""


def render_results(res):
    verdict = "APPROVED ✓" if "APPROVED" in res["feedback"] else "REVISED"
    metrics = [
        (len(res["sources"]), "SOURCES USED"),
        (res["revisions"], "CRITIC REVIEWS"),
        (f"{res['total']:.0f}s", "TOTAL TIME"),
        (verdict, "FINAL VERDICT"),
    ]
    for col, (num, lbl) in zip(st.columns(4), metrics):
        col.markdown(
            f'<div class="metric"><div class="num">{num}</div>'
            f'<div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.write("")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 Report", "🔗 Sources", "❓ Research Questions", "🧬 Agent Trace"]
    )
    with tab1:
        # Pehle poori report ka text
        st.markdown(res["report"])
        st.divider()
        # Uske neeche download buttons
        d1, d2, _ = st.columns([1, 1, 3])
        d1.download_button(
            "⬇️ Download PDF",
            make_pdf(res["report"], res["sources"]),
            file_name="research_report.pdf",
            mime="application/pdf",
            key="dl_pdf",
        )
        d2.download_button(
            "⬇️ Download .md",
            res["report"],
            file_name="research_report.md",
            key="dl_md",
        )
    with tab2:
        for s in res["sources"]:
            domain = urlparse(s["url"]).netloc.replace("www.", "")
            title = html_lib.escape(s["title"])
            st.markdown(
                f'<div class="src"><b>[{s["id"]}]</b> '
                f'<a href="{s["url"]}" target="_blank">{title}</a>'
                f'<div class="dom">{html_lib.escape(domain)}</div></div>',
                unsafe_allow_html=True)
    with tab3:
        for q in res["questions"]:
            st.markdown(f"- {q}")
    with tab4:
        rows = ""
        for secs, node, msg in res["trace"]:
            cls = "warn" if "issues" in msg else "ok"
            rows += (
                f'<div class="row"><span class="t">[{secs:5.1f}s]</span> '
                f'<span class="{cls}">{node.upper():<10}</span> '
                f'{html_lib.escape(msg)}</div>')
        st.markdown(f'<div class="trace">{rows}</div>', unsafe_allow_html=True)
        with st.expander("Critic's final feedback"):
            st.write(res["feedback"])


# =====================  STEP 1: TOPIC  =====================
step(1, "Choose your topic", "Type your own topic, or click an example below")

topic = st.text_input(
    "Research topic",
    key="topic_input",
    placeholder="e.g. Impact of AI on healthcare diagnostics",
    label_visibility="collapsed",
)
st.markdown('<div class="hint">💡 Or try an example (click to fill the box):</div>',
            unsafe_allow_html=True)
with st.container(key="chips"):
    cols = st.columns(len(EXAMPLES))
    for col, ex in zip(cols, EXAMPLES):
        col.button(ex, key=f"chip_{ex}", on_click=set_topic, args=(ex,))

# =====================  STEP 2: GENERATE  =====================
step(2, "Generate the report", "Takes about 1-2 minutes. Four agents work one after another")
run = st.button("🚀 Generate Report")

# =====================  STEP 3: AGENTS  =====================
step(3, "Watch the agents work", "Waiting → Working → Done, with time taken by each")
pipeline_box = st.empty()

# =====================  STEP 4: RESULTS  =====================
step(4, "Read your results", "Report, sources, research questions and agent trace")
results_box = st.empty()

saved = st.session_state.get("result")

if run:
    if not topic.strip():
        st.warning("Please enter a topic in Step 1 first.")
        pipeline_box.markdown(
            pipeline_html({k: "waiting" for k, *_ in AGENTS}, {}), unsafe_allow_html=True)
    else:
        st.session_state.pop("result", None)
        app = build_graph()
        state = {
            "topic": topic, "questions": [], "sources": [],
            "report": "", "feedback": "", "revisions": 0,
        }
        states = {k: "waiting" for k, *_ in AGENTS}
        states["planner"] = "running"
        times, trace = {}, []
        start = last = time.time()
        pipeline_box.markdown(pipeline_html(states, times), unsafe_allow_html=True)
        results_box.markdown(
            '<div class="placeholder">⏳ Agents are working. '
            'Your report will appear here.</div>', unsafe_allow_html=True)

        try:
            for s in app.stream(state):
                node = list(s.keys())[0]
                state.update(s[node])
                now = time.time()
                times[node] = times.get(node, 0) + (now - last)
                trace.append((now - start, node, describe(node, state)))
                last = now
                states[node] = "done"

                if node in NEXT:
                    states[NEXT[node]] = "running"
                elif node == "critic":
                    if "APPROVED" not in state["feedback"] and state["revisions"] < 2:
                        states["writer"] = "running"
                        states["critic"] = "waiting"

                # Live draft: Writer ka text turant Step 4 me dikhao
                if node == "writer":
                    with results_box.container():
                        st.markdown("#### 📝 Live draft (Critic is reviewing...)")
                        st.markdown(state["report"])

                pipeline_box.markdown(pipeline_html(states, times), unsafe_allow_html=True)

            st.session_state["result"] = {
                "questions": state["questions"], "sources": state["sources"],
                "report": state["report"], "feedback": state["feedback"],
                "revisions": state["revisions"], "total": time.time() - start,
                "trace": trace, "times": times,
            }
            st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif saved:
    done_states = {k: "done" for k, *_ in AGENTS}
    pipeline_box.markdown(pipeline_html(done_states, saved["times"]), unsafe_allow_html=True)
    with results_box.container():
        render_results(saved)
else:
    pipeline_box.markdown(
        pipeline_html({k: "waiting" for k, *_ in AGENTS}, {}), unsafe_allow_html=True)
    results_box.markdown(
        '<div class="placeholder">📄 Your report will appear here '
        'after you click <b>Generate Report</b>.</div>', unsafe_allow_html=True)
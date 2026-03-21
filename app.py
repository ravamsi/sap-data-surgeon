import streamlit as st
import pandas as pd
from io import BytesIO
from collections import defaultdict
from validator import validate_file, SAP_EC_SCHEMA
from ai_explainer import explain_error
from pdf_report import generate_pdf_report

st.set_page_config(
    page_title="SAP EC Data Surgeon",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem 4rem 2.5rem; max-width: 1200px; }
.stApp { background: #070c18; }

/* ── Stepper ── */
.stepper {
    display: flex; align-items: center; gap: 0;
    background: #0d1525; border: 1px solid #1a2e4a;
    border-radius: 12px; padding: 0; margin-bottom: 2rem;
    overflow: hidden;
}
.step-item {
    flex: 1; display: flex; align-items: center; gap: 10px;
    padding: 14px 20px; position: relative;
}
.step-item.active { background: rgba(37,99,235,0.12); }
.step-item.done { background: rgba(34,197,94,0.06); }
.step-dot {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600; flex-shrink: 0;
    border: 1.5px solid #1a2e4a; color: #3d5a80;
    background: transparent;
}
.step-item.active .step-dot {
    background: #2563eb; border-color: #2563eb; color: white;
}
.step-item.done .step-dot {
    background: #16a34a; border-color: #16a34a; color: white;
}
.step-text { font-size: 12px; color: #3d5a80; font-weight: 400; }
.step-item.active .step-text { color: #93c5fd; font-weight: 500; }
.step-item.done .step-text { color: #4ade80; }
.step-divider { width: 1px; height: 32px; background: #1a2e4a; flex-shrink: 0; }

/* ── Hero ── */
.hero {
    background: #0d1525; border: 1px solid #1a2e4a;
    border-radius: 14px; padding: 2.2rem 2.5rem;
    margin-bottom: 1.5rem; position: relative; overflow: hidden;
}
.hero-eyebrow {
    font-size: 11px; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: #3b82f6;
    margin-bottom: 10px; display: flex; align-items: center; gap: 8px;
}
.hero-eyebrow::before {
    content: ''; width: 20px; height: 1.5px; background: #3b82f6;
}
.hero h1 {
    font-size: 1.9rem; font-weight: 600; color: #e8f0fe;
    margin: 0 0 8px 0; line-height: 1.25; letter-spacing: -0.02em;
}
.hero p { color: #64748b; font-size: 0.9rem; margin: 0; line-height: 1.65; max-width: 560px; }
.hero-meta {
    margin-top: 1.25rem; padding-top: 1.25rem;
    border-top: 1px solid #1a2e4a;
    display: flex; align-items: center; gap: 12px;
}
.cert-tag {
    font-size: 11px; padding: 3px 10px; border-radius: 99px;
    background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2);
    color: #4ade80;
}
.author-tag { font-size: 12px; color: #475569; }

/* ── Upload zone override ── */
[data-testid="stFileUploader"] section {
    background: #0d1525 !important;
    border: 1.5px dashed #1a2e4a !important;
    border-radius: 10px !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #2563eb !important;
}

/* ── File loaded bar ── */
.file-bar {
    display: flex; align-items: center; justify-content: space-between;
    background: #0d1525; border: 1px solid #1a2e4a;
    border-radius: 10px; padding: 10px 16px; margin: 10px 0 1.5rem;
}
.file-bar-left { display: flex; align-items: center; gap: 10px; }
.file-dot { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; }
.file-name { font-size: 13px; color: #e2e8f0; font-weight: 500; }
.file-meta { font-size: 12px; color: #475569; }
.file-bar-right { font-size: 12px; color: #475569; }

/* ── Summary cards ── */
.summary-row {
    display: grid; grid-template-columns: 200px 1fr;
    gap: 12px; margin: 1.5rem 0;
}
.gauge-card {
    background: #0d1525; border: 1px solid #1a2e4a;
    border-radius: 14px; padding: 1.25rem;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; gap: 8px;
}
.gauge-score-label {
    font-size: 11px; color: #475569; text-transform: uppercase;
    letter-spacing: 0.08em;
}
.gauge-verdict { font-size: 12px; color: #64748b; text-align: center; }
.stats-and-health {
    background: #0d1525; border: 1px solid #1a2e4a;
    border-radius: 14px; padding: 1.25rem 1.5rem;
}
.stat-row {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 10px; margin-bottom: 1.25rem;
    padding-bottom: 1.25rem; border-bottom: 1px solid #1a2e4a;
}
.stat-item { }
.stat-label { font-size: 10px; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.stat-value { font-size: 1.6rem; font-weight: 600; line-height: 1; color: #e2e8f0; }
.stat-value.danger { color: #f87171; }
.stat-value.success { color: #4ade80; }
.health-label { font-size: 10px; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.fh-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.fh-name { font-family: 'DM Mono', monospace; font-size: 11px; color: #64748b; width: 100px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fh-bg { flex: 1; height: 5px; background: #1a2e4a; border-radius: 3px; overflow: hidden; }
.fh-fill { height: 5px; border-radius: 3px; }
.fh-count { font-size: 10px; color: #475569; width: 18px; text-align: right; }

/* ── Top issues card ── */
.top-issues {
    background: #0d1525; border: 1px solid #1a2e4a;
    border-radius: 14px; padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}
.ti-header {
    font-size: 12px; font-weight: 500; color: #93c5fd;
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.ti-header::before { content: '●'; font-size: 8px; color: #3b82f6; }
.ti-item {
    display: flex; align-items: baseline; gap: 10px;
    padding: 5px 0; border-bottom: 1px solid #1a2e4a;
    font-size: 12px;
}
.ti-item:last-child { border-bottom: none; }
.ti-num { color: #3b82f6; font-weight: 600; min-width: 20px; font-size: 14px; }
.ti-text { color: #94a3b8; }
.ti-field { font-family: 'DM Mono', monospace; color: #64748b; font-size: 11px; margin-left: auto; }

/* ── Error groups ── */
.error-group { margin-bottom: 10px; }
.group-header {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 8px;
    cursor: pointer; font-size: 13px;
}
.group-header.critical { background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); }
.group-header.warning  { background: rgba(251,191,36,0.07);  border: 1px solid rgba(251,191,36,0.2); }
.group-header.info     { background: rgba(96,165,250,0.07);  border: 1px solid rgba(96,165,250,0.18); }
.group-count {
    font-size: 11px; padding: 2px 8px; border-radius: 99px; font-weight: 500;
}
.group-count.critical { background: rgba(248,113,113,0.15); color: #f87171; }
.group-count.warning  { background: rgba(251,191,36,0.15);  color: #fbbf24; }
.group-count.info     { background: rgba(96,165,250,0.15);  color: #60a5fa; }
.group-title { font-weight: 500; }
.group-title.critical { color: #fca5a5; }
.group-title.warning  { color: #fde68a; }
.group-title.info     { color: #bfdbfe; }

/* ── Error rows ── */
.err-row {
    display: flex; gap: 0; margin: 4px 0 4px 24px;
    border-radius: 0 8px 8px 0; overflow: hidden;
    font-size: 12px; line-height: 1.5;
}
.err-row.critical { border-left: 3px solid #f87171; background: rgba(248,113,113,0.06); }
.err-row.warning  { border-left: 3px solid #fbbf24; background: rgba(251,191,36,0.05); }
.err-row.info     { border-left: 3px solid #60a5fa; background: rgba(96,165,250,0.05); }
.err-row.autofixed{ border-left: 3px solid #4ade80; background: rgba(74,222,128,0.05); }
.err-cell { padding: 8px 12px; }
.err-row-num { color: #475569; min-width: 48px; font-family: 'DM Mono', monospace; font-size: 11px; }
.err-field { color: #93c5fd; min-width: 140px; font-family: 'DM Mono', monospace; font-size: 11px; }
.err-type { min-width: 160px; }
.sev-pill { font-size: 10px; padding: 2px 8px; border-radius: 99px; font-weight: 500; display: inline-block; }
.sev-critical { background: rgba(248,113,113,0.15); color: #f87171; }
.sev-warning  { background: rgba(251,191,36,0.12);  color: #fbbf24; }
.sev-info     { background: rgba(96,165,250,0.12);  color: #60a5fa; }
.sev-fixed    { background: rgba(74,222,128,0.1);   color: #4ade80; }
.err-msg { color: #94a3b8; flex: 1; }

/* ── Section label ── */
.sec-label {
    font-size: 10px; font-weight: 500; color: #3d5a80;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1.75rem 0 0.75rem;
}

/* ── Download row ── */
.dl-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 1rem; }

/* ── Streamlit button overrides ── */
.stButton > button {
    background: #2563eb !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 14px !important;
    padding: 0.65rem 2rem !important; width: 100% !important;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #1d4ed8 !important; }
.stDownloadButton > button {
    background: #0d1525 !important; color: #60a5fa !important;
    border: 1px solid #1a2e4a !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: rgba(37,99,235,0.1) !important;
    border-color: #2563eb !important;
}
[data-testid="stMetric"] {
    background: #0d1525 !important; border: 1px solid #1a2e4a !important;
    border-radius: 10px !important; padding: 0.9rem 1.1rem !important;
}
[data-testid="stMetricLabel"] { color: #475569 !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; }
[data-testid="stSidebar"] {
    background: #060b15 !important;
    border-right: 1px solid #1a2e4a !important;
}
div[data-testid="stMarkdownContainer"] p { color: #64748b; }
.stAlert { border-radius: 10px !important; border: none !important; }
h1, h2, h3 { color: #e2e8f0 !important; }
div[data-testid="stExpander"] {
    background: #0d1525 !important;
    border: 1px solid #1a2e4a !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ──
def get_severity(error_type):
    t = error_type.lower()
    if "auto-fix" in t:
        return "autofixed"
    if "warning" in t:
        return "warning"
    if "cross-field" in t and "warning" in t:
        return "warning"
    if "cross-field" in t:
        return "info"
    return "critical"

def sev_label(sev):
    return {"critical": "Critical", "warning": "Warning",
            "info": "Info", "autofixed": "Auto-fixed"}.get(sev, "Info")

def ring_gauge_svg(score, color):
    r = 48
    circ = 2 * 3.14159 * r
    filled = (score / 100) * circ
    gap = circ - filled
    return f"""
<svg width="130" height="130" viewBox="0 0 130 130">
  <circle cx="65" cy="65" r="{r}" fill="none"
    stroke="#1a2e4a" stroke-width="10"/>
  <circle cx="65" cy="65" r="{r}" fill="none"
    stroke="{color}" stroke-width="10"
    stroke-dasharray="{filled:.1f} {gap:.1f}"
    stroke-dashoffset="{circ/4:.1f}"
    stroke-linecap="round"
    transform="rotate(-90 65 65)"/>
  <text x="65" y="60" text-anchor="middle"
    font-family="DM Sans,sans-serif" font-size="26"
    font-weight="600" fill="{color}">{score}%</text>
  <text x="65" y="78" text-anchor="middle"
    font-family="DM Sans,sans-serif" font-size="11"
    fill="#475569">readiness</text>
</svg>"""

def stepper_html(step):
    steps = ["Upload", "Validate", "Review", "Export"]
    items = []
    for i, s in enumerate(steps):
        n = i + 1
        cls = "active" if n == step else ("done" if n < step else "")
        dot = "✓" if n < step else str(n)
        items.append(f"""
        <div class="step-item {cls}">
            <div class="step-dot">{dot}</div>
            <div class="step-text">{s}</div>
        </div>""")
        if i < len(steps) - 1:
            items.append('<div class="step-divider"></div>')
    return f'<div class="stepper">{"".join(items)}</div>'

# ── Sidebar ──
with st.sidebar:
    st.markdown("""
    <div style='padding:1.25rem 0 0.5rem'>
        <div style='font-size:10px;color:#3d5a80;text-transform:uppercase;
        letter-spacing:0.12em;margin-bottom:14px'>How it works</div>
    </div>""", unsafe_allow_html=True)
    for num, text in [("01","Upload CSV or Excel"), ("02","Click Run Audit"),
                       ("03","Review AI explanations"), ("04","Download reports")]:
        st.markdown(f"""
        <div style='display:flex;gap:10px;align-items:flex-start;margin-bottom:12px'>
            <span style='font-family:DM Mono,monospace;font-size:11px;color:#2563eb;
            font-weight:500;flex-shrink:0;margin-top:1px'>{num}</span>
            <span style='font-size:13px;color:#64748b;line-height:1.4'>{text}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid #1a2e4a;margin:1rem 0'>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:12px;color:#3d5a80;line-height:2'>
        🔒 &nbsp;Processed in memory only<br>
        🗑️ &nbsp;No data stored or shared<br>
        ⚡ &nbsp;Results in under 2 minutes
    </div>""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">SAP SuccessFactors · Employee Central</div>
    <h1>Pre-Migration Data Audit</h1>
    <p>Upload your employee data file. Every field is validated against SAP EC rules,
    each error explained in plain English, and a corrected file returned — ready for import.</p>
    <div class="hero-meta">
        <span class="author-tag">Built by Vamsi Rayala</span>
        <span class="cert-tag">SAP EC Certified</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Upload ──
st.markdown(stepper_html(1), unsafe_allow_html=True)
st.markdown('<div class="sec-label">Upload data file</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop CSV or Excel here",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

if uploaded is None:
    # Empty state
    required = [f for f, r in SAP_EC_SCHEMA.items() if r["required"]]
    optional = [f for f, r in SAP_EC_SCHEMA.items() if not r["required"]]
    req_items = "".join([f'<span style="font-family:DM Mono,monospace;font-size:11px;'
                         f'color:#64748b;padding:2px 0;display:block">{f}</span>'
                         for f in required])
    opt_items = "".join([f'<span style="font-family:DM Mono,monospace;font-size:11px;'
                         f'color:#3d5a80;padding:2px 0;display:block">{f}</span>'
                         for f in optional])
    st.markdown(f"""
    <div style='background:#0d1525;border:1px solid #1a2e4a;border-radius:12px;
    padding:1.25rem 1.5rem;margin-top:1rem;display:grid;
    grid-template-columns:1fr 1fr;gap:1.5rem'>
        <div>
            <div style='font-size:10px;color:#3d5a80;text-transform:uppercase;
            letter-spacing:0.08em;margin-bottom:8px'>Required columns</div>
            {req_items}
        </div>
        <div>
            <div style='font-size:10px;color:#3d5a80;text-transform:uppercase;
            letter-spacing:0.08em;margin-bottom:8px'>Optional columns</div>
            {opt_items}
        </div>
    </div>""", unsafe_allow_html=True)

    # Template download
    tdata = {
        "userId":["EMP001","EMP002"],"firstName":["Marco","Sofia"],
        "lastName":["Rossi","Bianchi"],"hireDate":["2024-01-15","2024-03-01"],
        "startDate":["2024-01-15","2024-03-01"],"country":["ITA","DEU"],
        "company":["Acme SpA","Acme SpA"],"businessUnit":["IT","HR"],
        "department":["Engineering","Human Resources"],"division":["Tech","People"],
        "jobCode":["DEV01","HR01"],"payGroup":["PG-ITA","PG-DEU"],
        "email":["marco@company.com","sofia@company.com"],
        "gender":["M","F"],"employmentType":["Employee","Employee"],
        "contractType":["Permanent","Fixed-Term"],"payFrequency":["Monthly","Monthly"],
        "managerId":["EMP000","EMP000"],"costCenter":["CC-001","CC-002"],
    }
    tdf = pd.DataFrame(tdata)
    tout = BytesIO()
    with pd.ExcelWriter(tout, engine="openpyxl") as w:
        tdf.to_excel(w, sheet_name="Employee Data", index=False)
    tout.seek(0)
    st.markdown('<div style="margin-top:1rem">', unsafe_allow_html=True)
    st.download_button("📥 Download SAP EC Template (.xlsx)", data=tout,
                       file_name="sap_ec_template.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── Load ──
try:
    df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") \
         else pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

required_fields = [f for f, r in SAP_EC_SCHEMA.items() if r["required"]]
found = [f for f in required_fields if f in df.columns]
missing_cols = [f for f in required_fields if f not in df.columns]

st.markdown(f"""
<div class="file-bar">
    <div class="file-bar-left">
        <div class="file-dot"></div>
        <span class="file-name">{uploaded.name}</span>
        <span class="file-meta">{len(df):,} rows · {len(df.columns)} columns</span>
    </div>
    <span class="file-bar-right">{len(found)}/{len(required_fields)} required columns found</span>
</div>""", unsafe_allow_html=True)

if missing_cols:
    st.warning(f"Missing required columns: {', '.join(missing_cols)}")

# ── Step 2: Validate ──
st.markdown(stepper_html(2), unsafe_allow_html=True)
run = st.button("▶  Run Full Audit", type="primary", use_container_width=True)

if not run:
    st.stop()

with st.spinner("Validating against SAP EC field schema..."):
    errors, corrected_df = validate_file(df)

auto_fixed  = [e for e in errors if "Auto-fixed" in e["error_type"]]
real_errors = [e for e in errors if "Auto-fixed" not in e["error_type"]]

# Attach severity
for e in real_errors:
    e["_sev"] = get_severity(e["error_type"])
for e in auto_fixed:
    e["_sev"] = "autofixed"

# Score
total_checks = len(df) * len([f for f in SAP_EC_SCHEMA if f in df.columns])
score = max(0, round(((total_checks - len(real_errors)) / total_checks) * 100)) \
        if total_checks > 0 else 0

if score >= 90:
    score_color, score_verdict = "#4ade80", "Excellent — nearly import-ready"
elif score >= 70:
    score_color, score_verdict = "#fbbf24", "Good — a few issues to fix"
elif score >= 50:
    score_color, score_verdict = "#f97316", "Fair — several issues need attention"
else:
    score_color, score_verdict = "#f87171", "Poor — significant cleanup required"

# ── Step 3: Review ──
st.markdown(stepper_html(3), unsafe_allow_html=True)

# Field health
field_error_counts = defaultdict(int)
for e in real_errors:
    field_error_counts[str(e["field"])] += 1
top_fields = sorted(field_error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
max_count = max((c for _, c in top_fields), default=1)

fh_rows = ""
for fname, cnt in top_fields:
    pct = int((cnt / max_count) * 100)
    bar_color = "#f87171" if cnt >= 2 else "#fbbf24"
    label = fname[:14] + "…" if len(fname) > 14 else fname
    fh_rows += f"""
    <div class="fh-row">
        <span class="fh-name">{label}</span>
        <div class="fh-bg"><div class="fh-fill" style="width:{pct}%;background:{bar_color}"></div></div>
        <span class="fh-count">{cnt}</span>
    </div>"""

err_class  = "danger" if real_errors else "success"
err_val    = str(len(real_errors))
fix_class  = "success" if auto_fixed else ""

col_gauge, col_stats = st.columns([1, 2.5])

with col_gauge:
    st.markdown(f"""
    <div class="gauge-card" style="height:100%">
        <div class="gauge-score-label">Readiness score</div>
        {ring_gauge_svg(score, score_color)}
        <div class="gauge-verdict">{score_verdict}</div>
    </div>""", unsafe_allow_html=True)

with col_stats:
    st.markdown(f"""
    <div class="stats-and-health">
        <div class="stat-row">
            <div class="stat-item">
                <div class="stat-label">Errors found</div>
                <div class="stat-value {err_class}">{err_val}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Auto-corrected</div>
                <div class="stat-value {fix_class}">{len(auto_fixed)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Rows processed</div>
                <div class="stat-value">{len(df):,}</div>
            </div>
        </div>
        <div class="health-label">Fields with most errors</div>
        {fh_rows if fh_rows else '<span style="font-size:12px;color:#3d5a80">No errors found</span>'}
    </div>""", unsafe_allow_html=True)

if not real_errors and not auto_fixed:
    st.success("✅ No errors found. Your file appears ready for SAP import.")
else:
    # ── Top issues card ──
    by_type = defaultdict(list)
    for e in real_errors:
        by_type[e["error_type"]].append(e)

    ti_items = ""
    for etype, errs in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)[:4]:
        fields = list({str(e["field"]) for e in errs})
        field_str = fields[0] if len(fields) == 1 else f"{fields[0]} +{len(fields)-1}"
        ti_items += f"""
        <div class="ti-item">
            <span class="ti-num">{len(errs)}</span>
            <span class="ti-text">{etype}</span>
            <span class="ti-field">{field_str}</span>
        </div>"""

    st.markdown(
        '<div class="top-issues"><div class="ti-header">Top issues to fix</div>'
        + ti_items +
        '</div>',
        unsafe_allow_html=True
    )

    # ── AI Explanations ──
    with st.spinner(f"Generating AI explanations for {len(real_errors)} errors..."):
        for e in real_errors:
            e["ai_fix"] = explain_error(e)

    # ── Grouped errors ──
    sev_order  = ["critical", "warning", "info"]
    sev_labels = {"critical": "Critical errors — import will fail",
                  "warning":  "Warnings — may cause issues",
                  "info":     "Cross-field notices"}
    sev_groups = defaultdict(list)
    for e in real_errors:
        sev_groups[e["_sev"]].append(e)

    st.markdown('<div class="sec-label">Errors by severity</div>',
                unsafe_allow_html=True)

    for sev in sev_order:
        if sev not in sev_groups:
            continue
        group = sev_groups[sev]
        rows_html = ""
        for e in group:
            fix = e.get("ai_fix", e.get("description", ""))
            rows_html += f"""
            <div class="err-row {sev}">
                <div class="err-cell err-row-num">Row {e['row']}</div>
                <div class="err-cell err-field">{e['field']}</div>
                <div class="err-cell err-type">
                    <span class="sev-pill sev-{sev}">{sev_label(sev)}</span>
                </div>
                <div class="err-cell err-msg">{fix}</div>
            </div>"""

        with st.expander(f"{sev_labels[sev]}  ({len(group)})", expanded=(sev=="critical")):
            st.markdown(rows_html, unsafe_allow_html=True)

    # Auto-fixed
    if auto_fixed:
        rows_html = ""
        for e in auto_fixed:
            rows_html += f"""
            <div class="err-row autofixed">
                <div class="err-cell err-row-num">Row {e['row']}</div>
                <div class="err-cell err-field">{e['field']}</div>
                <div class="err-cell err-type">
                    <span class="sev-pill sev-fixed">Auto-fixed</span>
                </div>
                <div class="err-cell err-msg">{e['description']}</div>
            </div>"""
        with st.expander(f"Auto-corrected items  ({len(auto_fixed)})", expanded=False):
            st.markdown(rows_html, unsafe_allow_html=True)

# ── Step 4: Export ──
st.markdown(stepper_html(4), unsafe_allow_html=True)
st.markdown('<div class="sec-label">Download results</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        if real_errors:
            pd.DataFrame(real_errors).to_excel(w, sheet_name="Error Report", index=False)
        if auto_fixed:
            pd.DataFrame(auto_fixed).to_excel(w, sheet_name="Auto-Fixed", index=False)
        corrected_df.to_excel(w, sheet_name="Corrected Data", index=False)
    out.seek(0)
    st.download_button(
        "📊 Download Excel Report (.xlsx)", data=out,
        file_name=f"sap_audit_{uploaded.name.split('.')[0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col2:
    pdf_buf = generate_pdf_report(
        filename=uploaded.name, total_rows=len(df),
        score=score, score_label=score_verdict,
        real_errors=real_errors, auto_fixed=auto_fixed
    )
    st.download_button(
        "📄 Download PDF Summary (.pdf)", data=pdf_buf,
        file_name=f"sap_audit_{uploaded.name.split('.')[0]}.pdf",
        mime="application/pdf", use_container_width=True
    )
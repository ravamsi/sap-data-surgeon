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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem 4rem 2.5rem; max-width: 1200px; }
.stApp { background: #f4f6f9; }

/* ── Stepper ── */
.stepper {
    display: flex; align-items: center;
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 12px; margin-bottom: 2rem;
    overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.step-item {
    flex: 1; display: flex; align-items: center; gap: 10px;
    padding: 14px 20px;
}
.step-item.active { background: #eff6ff; }
.step-item.done   { background: #f0fdf4; }
.step-dot {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600; flex-shrink: 0;
    border: 1.5px solid #cbd5e1; color: #94a3b8;
}
.step-item.active .step-dot { background: #2563eb; border-color: #2563eb; color: white; }
.step-item.done   .step-dot { background: #16a34a; border-color: #16a34a; color: white; }
.step-text { font-size: 12px; color: #94a3b8; }
.step-item.active .step-text { color: #2563eb; font-weight: 500; }
.step-item.done   .step-text { color: #16a34a; }
.step-divider { width: 1px; height: 32px; background: #e2e8f0; flex-shrink: 0; }

/* ── Hero ── */
.hero {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 2.2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.hero-eyebrow {
    font-size: 11px; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: #2563eb;
    margin-bottom: 10px; display: flex; align-items: center; gap: 8px;
}
.hero-eyebrow::before { content: ''; width: 20px; height: 1.5px; background: #2563eb; }
.hero h1 {
    font-size: 1.9rem; font-weight: 600; color: #0f172a;
    margin: 0 0 8px 0; line-height: 1.25; letter-spacing: -0.02em;
}
.hero p { color: #64748b; font-size: 0.9rem; margin: 0; line-height: 1.65; max-width: 560px; }
.hero-meta {
    margin-top: 1.25rem; padding-top: 1.25rem;
    border-top: 1px solid #e2e8f0;
    display: flex; align-items: center; gap: 12px;
}
.author-tag { font-size: 12px; color: #94a3b8; }

/* ── File bar ── */
.file-bar {
    display: flex; align-items: center; justify-content: space-between;
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 10px 16px; margin: 10px 0 1.5rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.file-bar-left { display: flex; align-items: center; gap: 10px; }
.file-dot { width: 8px; height: 8px; border-radius: 50%; background: #16a34a; }
.file-name { font-size: 13px; color: #0f172a; font-weight: 500; }
.file-meta { font-size: 12px; color: #94a3b8; }
.file-bar-right { font-size: 12px; color: #94a3b8; }

/* ── Gauge card ── */
.gauge-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 1.25rem;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    height: 100%;
}
.gauge-score-label {
    font-size: 10px; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 0.1em;
}
.gauge-verdict { font-size: 12px; color: #64748b; text-align: center; }

/* ── Stats and health ── */
.stats-and-health {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.stat-row {
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 10px; margin-bottom: 1.25rem; padding-bottom: 1.25rem;
    border-bottom: 1px solid #f1f5f9;
}
.stat-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.stat-value { font-size: 1.8rem; font-weight: 600; line-height: 1; color: #0f172a; }
.stat-value.danger  { color: #dc2626; }
.stat-value.success { color: #16a34a; }
.health-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.fh-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.fh-name { font-family: 'DM Mono', monospace; font-size: 11px; color: #64748b; width: 100px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fh-bg   { flex: 1; height: 5px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.fh-fill { height: 5px; border-radius: 3px; }
.fh-count { font-size: 10px; color: #94a3b8; width: 18px; text-align: right; }

/* ── Top issues ── */
.top-issues {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.ti-header {
    font-size: 12px; font-weight: 500; color: #2563eb;
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.ti-header::before { content: '●'; font-size: 8px; color: #2563eb; }
.ti-item {
    display: flex; align-items: baseline; gap: 10px;
    padding: 6px 0; border-bottom: 1px solid #f1f5f9;
    font-size: 12px;
}
.ti-item:last-child { border-bottom: none; }
.ti-num  { color: #2563eb; font-weight: 600; min-width: 20px; font-size: 14px; }
.ti-text { color: #475569; }
.ti-field { font-family: 'DM Mono', monospace; color: #94a3b8; font-size: 11px; margin-left: auto; }

/* ── Error groups ── */
.group-header { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-size: 13px; }
.group-count  { font-size: 11px; padding: 2px 8px; border-radius: 99px; font-weight: 500; }
.group-count.critical { background: #fee2e2; color: #dc2626; }
.group-count.warning  { background: #fef3c7; color: #d97706; }
.group-count.info     { background: #dbeafe; color: #2563eb; }

/* ── Error rows ── */
.err-row {
    display: flex; gap: 0; margin: 4px 0 4px 24px;
    border-radius: 0 8px 8px 0; overflow: hidden; font-size: 12px; line-height: 1.5;
}
.err-row.critical { border-left: 3px solid #ef4444; background: #fff5f5; }
.err-row.warning  { border-left: 3px solid #f59e0b; background: #fffbeb; }
.err-row.info     { border-left: 3px solid #3b82f6; background: #eff6ff; }
.err-row.autofixed{ border-left: 3px solid #22c55e; background: #f0fdf4; }
.err-cell { padding: 8px 12px; }
.err-row-num { color: #94a3b8; min-width: 48px; font-family: 'DM Mono', monospace; font-size: 11px; }
.err-field   { color: #2563eb; min-width: 140px; font-family: 'DM Mono', monospace; font-size: 11px; }
.sev-pill { font-size: 10px; padding: 2px 8px; border-radius: 99px; font-weight: 500; display: inline-block; }
.sev-critical { background: #fee2e2; color: #dc2626; }
.sev-warning  { background: #fef3c7; color: #d97706; }
.sev-info     { background: #dbeafe; color: #2563eb; }
.sev-fixed    { background: #dcfce7; color: #16a34a; }
.err-type { min-width: 160px; }
.err-msg  { color: #475569; flex: 1; }

/* ── Section label ── */
.sec-label {
    font-size: 10px; font-weight: 500; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1.75rem 0 0.75rem;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: #2563eb !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 14px !important;
    padding: 0.65rem 2rem !important; width: 100% !important;
}
.stButton > button:hover { background: #1d4ed8 !important; }
.stDownloadButton > button {
    background: #ffffff !important; color: #2563eb !important;
    border: 1px solid #bfdbfe !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: #eff6ff !important; border-color: #2563eb !important;
}
[data-testid="stFileUploader"] section {
    background: #ffffff !important; border: 1.5px dashed #cbd5e1 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] section:hover { border-color: #2563eb !important; }
[data-testid="stMetric"] {
    background: #ffffff !important; border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important; padding: 0.9rem 1.1rem !important;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #0f172a !important; }
[data-testid="stSidebar"] {
    background: #ffffff !important; border-right: 1px solid #e2e8f0 !important;
}
div[data-testid="stMarkdownContainer"] p { color: #64748b; }
.stAlert { border-radius: 10px !important; }
h1, h2, h3 { color: #0f172a !important; }
div[data-testid="stExpander"] {
    background: #ffffff !important; border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ──
def get_severity(error_type):
    t = error_type.lower()
    if "auto-fix" in t:    return "autofixed"
    if "warning"  in t:    return "warning"
    if "cross-field" in t: return "info"
    return "critical"

def sev_label(sev):
    return {"critical":"Critical","warning":"Warning",
            "info":"Notice","autofixed":"Auto-fixed"}.get(sev,"Info")

def ring_gauge_svg(score, color):
    r = 48
    circ = 2 * 3.14159 * r
    filled = (score / 100) * circ
    gap = circ - filled
    return f"""
<svg width="130" height="130" viewBox="0 0 130 130">
  <circle cx="65" cy="65" r="{r}" fill="none" stroke="#f1f5f9" stroke-width="10"/>
  <circle cx="65" cy="65" r="{r}" fill="none" stroke="{color}" stroke-width="10"
    stroke-dasharray="{filled:.1f} {gap:.1f}"
    stroke-dashoffset="{circ/4:.1f}"
    stroke-linecap="round" transform="rotate(-90 65 65)"/>
  <text x="65" y="60" text-anchor="middle"
    font-family="DM Sans,sans-serif" font-size="26"
    font-weight="600" fill="{color}">{score}%</text>
  <text x="65" y="78" text-anchor="middle"
    font-family="DM Sans,sans-serif" font-size="11"
    fill="#94a3b8">readiness</text>
</svg>"""

def stepper_html(step):
    steps = ["Upload","Validate","Review","Export"]
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
        <div style='font-size:10px;color:#94a3b8;text-transform:uppercase;
        letter-spacing:0.12em;margin-bottom:14px'>How it works</div>
    </div>""", unsafe_allow_html=True)
    for num, text in [("01","Upload CSV or Excel"),("02","Click Run Audit"),
                       ("03","Review AI explanations"),("04","Download reports")]:
        st.markdown(f"""
        <div style='display:flex;gap:10px;align-items:flex-start;margin-bottom:12px'>
            <span style='font-family:DM Mono,monospace;font-size:11px;color:#2563eb;
            font-weight:500;flex-shrink:0;margin-top:1px'>{num}</span>
            <span style='font-size:13px;color:#64748b;line-height:1.4'>{text}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1rem 0'>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:12px;color:#94a3b8;line-height:2.2'>
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
</div>
""", unsafe_allow_html=True)

# ── Step 1 ──
st.markdown(stepper_html(1), unsafe_allow_html=True)
st.markdown('<div class="sec-label">Upload data file</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop CSV or Excel here", type=["csv","xlsx"],
    label_visibility="collapsed"
)

if uploaded is None:
    required = [f for f, r in SAP_EC_SCHEMA.items() if r["required"]]
    optional = [f for f, r in SAP_EC_SCHEMA.items() if not r["required"]]
    req_items = "".join([
        f'<span style="font-family:DM Mono,monospace;font-size:11px;color:#475569;'
        f'padding:2px 0;display:block">{f}</span>' for f in required])
    opt_items = "".join([
        f'<span style="font-family:DM Mono,monospace;font-size:11px;color:#94a3b8;'
        f'padding:2px 0;display:block">{f}</span>' for f in optional])
    st.markdown(f"""
    <div style='background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;
    padding:1.25rem 1.5rem;margin-top:1rem;display:grid;
    grid-template-columns:1fr 1fr;gap:1.5rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.06)'>
        <div>
            <div style='font-size:10px;color:#94a3b8;text-transform:uppercase;
            letter-spacing:0.08em;margin-bottom:8px'>Required columns</div>
            {req_items}
        </div>
        <div>
            <div style='font-size:10px;color:#94a3b8;text-transform:uppercase;
            letter-spacing:0.08em;margin-bottom:8px'>Optional columns</div>
            {opt_items}
        </div>
    </div>""", unsafe_allow_html=True)

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

# ── Step 2 ──
st.markdown(stepper_html(2), unsafe_allow_html=True)
run = st.button("▶  Run Full Audit", type="primary", use_container_width=True)
if not run:
    st.stop()

with st.spinner("Validating against SAP EC field schema..."):
    errors, corrected_df = validate_file(df)

auto_fixed  = [e for e in errors if "Auto-fixed" in e["error_type"]]
real_errors = [e for e in errors if "Auto-fixed" not in e["error_type"]]

for e in real_errors: e["_sev"] = get_severity(e["error_type"])
for e in auto_fixed:  e["_sev"] = "autofixed"

total_checks = len(df) * len([f for f in SAP_EC_SCHEMA if f in df.columns])
score = max(0, round(((total_checks - len(real_errors)) / total_checks) * 100)) \
        if total_checks > 0 else 0

if score >= 90:   score_color, score_verdict = "#16a34a", "Excellent — nearly import-ready"
elif score >= 70: score_color, score_verdict = "#d97706", "Good — a few issues to fix"
elif score >= 50: score_color, score_verdict = "#ea580c", "Fair — several issues need attention"
else:             score_color, score_verdict = "#dc2626", "Poor — significant cleanup required"

# Field health
field_error_counts = defaultdict(int)
for e in real_errors:
    field_error_counts[str(e["field"])] += 1
top_fields = sorted(field_error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
max_count  = max((c for _, c in top_fields), default=1)

fh_rows = ""
for fname, cnt in top_fields:
    pct = int((cnt / max_count) * 100)
    bar_color = "#ef4444" if cnt >= 2 else "#f59e0b"
    label = fname[:14] + "…" if len(fname) > 14 else fname
    fh_rows += f"""
    <div class="fh-row">
        <span class="fh-name">{label}</span>
        <div class="fh-bg"><div class="fh-fill" style="width:{pct}%;background:{bar_color}"></div></div>
        <span class="fh-count">{cnt}</span>
    </div>"""

err_class = "danger" if real_errors else "success"
fix_class = "success" if auto_fixed else ""

# ── Step 3 ──
st.markdown(stepper_html(3), unsafe_allow_html=True)

col_gauge, col_stats = st.columns([1, 2.5])
with col_gauge:
    st.markdown(f"""
    <div class="gauge-card">
        <div class="gauge-score-label">Readiness score</div>
        {ring_gauge_svg(score, score_color)}
        <div class="gauge-verdict">{score_verdict}</div>
    </div>""", unsafe_allow_html=True)

with col_stats:
    st.markdown(f"""
    <div class="stats-and-health">
        <div class="stat-row">
            <div>
                <div class="stat-label">Errors found</div>
                <div class="stat-value {err_class}">{len(real_errors)}</div>
            </div>
            <div>
                <div class="stat-label">Auto-corrected</div>
                <div class="stat-value {fix_class}">{len(auto_fixed)}</div>
            </div>
            <div>
                <div class="stat-label">Rows processed</div>
                <div class="stat-value">{len(df):,}</div>
            </div>
        </div>
        <div class="health-label">Fields with most errors</div>
        {fh_rows if fh_rows else '<span style="font-size:12px;color:#94a3b8">No errors found</span>'}
    </div>""", unsafe_allow_html=True)

if not real_errors and not auto_fixed:
    st.success("✅ No errors found. Your file appears ready for SAP import.")
else:
    # Top issues
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
        + ti_items + '</div>',
        unsafe_allow_html=True
    )

    # AI explanations
    with st.spinner(f"Generating AI explanations for {len(real_errors)} errors..."):
        for e in real_errors:
            e["ai_fix"] = explain_error(e)

    # Grouped errors
    sev_order  = ["critical","warning","info"]
    sev_labels = {
        "critical": "Critical errors — import will fail",
        "warning":  "Warnings — may cause issues",
        "info":     "Cross-field notices"
    }
    sev_groups = defaultdict(list)
    for e in real_errors:
        sev_groups[e["_sev"]].append(e)

    st.markdown('<div class="sec-label">Errors by severity</div>',
                unsafe_allow_html=True)

    for sev in sev_order:
        if sev not in sev_groups: continue
        group = sev_groups[sev]
        rows_html = ""
        for e in group:
            fix = e.get("ai_fix", e.get("description",""))
            rows_html += f"""
            <div class="err-row {sev}">
                <div class="err-cell err-row-num">Row {e['row']}</div>
                <div class="err-cell err-field">{e['field']}</div>
                <div class="err-cell err-type">
                    <span class="sev-pill sev-{sev}">{sev_label(sev)}</span>
                </div>
                <div class="err-cell err-msg">{fix}</div>
            </div>"""
        with st.expander(f"{sev_labels[sev]}  ({len(group)})",
                         expanded=(sev == "critical")):
            st.markdown(rows_html, unsafe_allow_html=True)

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
        with st.expander(f"Auto-corrected items  ({len(auto_fixed)})",
                         expanded=False):
            st.markdown(rows_html, unsafe_allow_html=True)

# ── Step 4 ──
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
    st.markdown("""
        <div style='margin-top:3rem;padding-top:1.5rem;border-top:1px solid #e2e8f0;
        text-align:center;font-size:12px;color:#94a3b8'>
        Built by Vamsi Rayala · sapdatavalidator.streamlit.app
        </div>
        """, unsafe_allow_html=True)
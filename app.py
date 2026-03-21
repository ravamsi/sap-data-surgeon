import streamlit as st
import pandas as pd
from io import BytesIO
from validator import validate_file, SAP_EC_SCHEMA
from ai_explainer import explain_error

st.set_page_config(
    page_title="SAP EC Data Surgeon",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 SAP SuccessFactors — Pre-Migration Data Audit")
st.caption(
    "Upload your employee data file. The tool validates it against SAP EC field rules, "
    "explains every error in plain English, and returns a corrected file ready for import."
)
st.divider()

# ── Sidebar ──
with st.sidebar:
    st.header("How it works")
    st.markdown("""
1. Upload your CSV or Excel file
2. Click **Run Audit**
3. Review errors with AI explanations
4. Download the corrected file
    """)
    st.divider()
    st.caption("Built by Vamsi Rayala · SAP EC Certified")

# ── File Upload ──
uploaded = st.file_uploader(
    "Upload employee data file",
    type=["csv", "xlsx"],
    help="Your file should have column headers matching SAP EC field names (userId, firstName, hireDate, etc.)"
)

if uploaded is None:
    st.info("Upload a file above to begin the audit.")

    template_data = {
        "userId": ["EMP001", "EMP002"],
        "firstName": ["Marco", "Sofia"],
        "lastName": ["Rossi", "Bianchi"],
        "hireDate": ["2024-01-15", "2024-03-01"],
        "startDate": ["2024-01-15", "2024-03-01"],
        "country": ["ITA", "DEU"],
        "company": ["Acme SpA", "Acme SpA"],
        "businessUnit": ["IT", "HR"],
        "department": ["Engineering", "Human Resources"],
        "division": ["Tech", "People"],
        "jobCode": ["DEV01", "HR01"],
        "payGroup": ["PG-ITA", "PG-DEU"],
        "email": ["marco.rossi@company.com", "sofia.bianchi@company.com"],
        "gender": ["M", "F"],
        "employmentType": ["Employee", "Employee"],
        "contractType": ["Permanent", "Fixed-Term"],
        "payFrequency": ["Monthly", "Monthly"],
        "managerId": ["EMP000", "EMP000"],
        "costCenter": ["CC-001", "CC-002"],
    }

    template_df = pd.DataFrame(template_data)
    template_output = BytesIO()
    with pd.ExcelWriter(template_output, engine="openpyxl") as writer:
        template_df.to_excel(writer, sheet_name="Employee Data", index=False)
    template_output.seek(0)

    with st.expander("Expected column names"):
        required = [f for f, r in SAP_EC_SCHEMA.items() if r["required"]]
        optional = [f for f, r in SAP_EC_SCHEMA.items() if not r["required"]]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Required**")
            for f in required:
                st.markdown(f"- `{f}`")
        with col2:
            st.markdown("**Optional**")
            for f in optional:
                st.markdown(f"- `{f}`")

    st.download_button(
        label="📥 Download SAP EC Template (.xlsx)",
        data=template_output,
        file_name="sap_ec_employee_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Download this template, fill it with your employee data, then upload it above"
    )
    st.stop()

# ── Load file ──
try:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

st.success(f"File loaded: **{len(df)} rows · {len(df.columns)} columns**")

# ── Column check ──
required_fields = [f for f, r in SAP_EC_SCHEMA.items() if r["required"]]
found = [f for f in required_fields if f in df.columns]
missing_cols = [f for f in required_fields if f not in df.columns]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total rows", len(df))
c2.metric("Total columns", len(df.columns))
c3.metric("Required columns found", f"{len(found)} / {len(required_fields)}")
c4.metric("Missing required columns", len(missing_cols), delta_color="inverse")

if missing_cols:
    st.warning(f"Missing required columns: {', '.join(missing_cols)}")

# ── Run button ──
if st.button("▶  Run Full Audit", type="primary", use_container_width=True):

    with st.spinner("Validating against SAP EC schema..."):
        errors, corrected_df = validate_file(df)

    auto_fixed  = [e for e in errors if "Auto-fixed" in e["error_type"]]
    real_errors = [e for e in errors if "Auto-fixed" not in e["error_type"]]

    st.divider()

    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Errors requiring manual fix", len(real_errors),
                delta=f"-{len(real_errors)}" if real_errors else None, delta_color="inverse")
    col2.metric("Issues auto-corrected", len(auto_fixed))
    col3.metric("Rows processed", len(df))

    if not real_errors and not auto_fixed:
        st.success("✅ No errors found. Your file appears ready for SAP import.")
    else:
        # AI explanations
        if real_errors:
            st.subheader("Errors requiring your attention")
            with st.spinner(f"Generating AI explanations for {len(real_errors)} errors..."):
                for e in real_errors:
                    e["What to do"] = explain_error(e)

            display_df = pd.DataFrame(real_errors)[
                ["row", "field", "bad_value", "error_type", "What to do"]
            ]
            display_df.columns = ["Row", "Field", "Bad Value", "Error Type", "AI Explanation & Fix"]
            st.dataframe(display_df, use_container_width=True, height=400)

        if auto_fixed:
            with st.expander(f"✅ {len(auto_fixed)} issues auto-corrected (date format standardization)"):
                auto_df = pd.DataFrame(auto_fixed)[["row","field","bad_value","description"]]
                auto_df.columns = ["Row","Field","Original Value","What was fixed"]
                st.dataframe(auto_df, use_container_width=True)

    # ── Download ──
    st.divider()
    st.subheader("Download results")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if real_errors:
            pd.DataFrame(real_errors).to_excel(writer, sheet_name="Error Report", index=False)
        if auto_fixed:
            pd.DataFrame(auto_fixed).to_excel(writer, sheet_name="Auto-Fixed Items", index=False)
        corrected_df.to_excel(writer, sheet_name="Corrected Data", index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Full Audit Report (.xlsx)",
        data=output,
        file_name=f"sap_ec_audit_{uploaded.name.split('.')[0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
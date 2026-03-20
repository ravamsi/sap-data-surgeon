import pandas as pd
from datetime import datetime

SAP_EC_SCHEMA = {
    "userId":         {"required": True,  "type": "string",   "max_len": 100},
    "firstName":      {"required": True,  "type": "string",   "max_len": 128},
    "lastName":       {"required": True,  "type": "string",   "max_len": 128},
    "hireDate":       {"required": True,  "type": "date"},
    "startDate":      {"required": True,  "type": "date"},
    "country":        {"required": True,  "type": "picklist", "values": ["ITA","DEU","GBR","FRA","ESP","NLD","USA","IND","CHE","BEL"]},
    "company":        {"required": True,  "type": "string",   "max_len": 128},
    "businessUnit":   {"required": False, "type": "string",   "max_len": 128},
    "department":     {"required": True,  "type": "string",   "max_len": 128},
    "division":       {"required": False, "type": "string",   "max_len": 128},
    "jobCode":        {"required": True,  "type": "string",   "max_len": 32},
    "payGroup":       {"required": True,  "type": "string",   "max_len": 32},
    "email":          {"required": True,  "type": "email"},
    "gender":         {"required": True,  "type": "picklist", "values": ["M","F","N","U"]},
    "employmentType": {"required": True,  "type": "picklist", "values": ["Employee","Contractor","Contingent Worker"]},
    "contractType":   {"required": False, "type": "picklist", "values": ["Permanent","Fixed-Term","Temporary"]},
    "payFrequency":   {"required": False, "type": "picklist", "values": ["Monthly","Weekly","Bi-Weekly","Semi-Monthly"]},
    "managerId":      {"required": False, "type": "string",   "max_len": 100},
    "costCenter":     {"required": False, "type": "string",   "max_len": 64},
}

def validate_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return None, None
    s = str(value).strip()
    for fmt in ["%Y-%m-%d","%d/%m/%Y","%m/%d/%Y","%d-%m-%Y","%Y/%m/%d"]:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d"), fmt
        except ValueError:
            continue
    return False, None

def validate_file(df):
    errors = []
    corrected = df.copy()

    if "userId" in df.columns:
        dupes = df[df.duplicated("userId", keep=False)]["userId"].dropna().unique()
        for uid in dupes:
            rows = df[df["userId"] == uid].index.tolist()
            errors.append({
                "row": str([r+2 for r in rows]),
                "field": "userId",
                "bad_value": str(uid),
                "error_type": "Duplicate ID",
                "description": f"userId '{uid}' appears {len(rows)} times. Every employee must have a unique identifier in SAP EC.",
            })

    for field, rules in SAP_EC_SCHEMA.items():
        if field not in df.columns:
            if rules["required"]:
                errors.append({
                    "row": "ALL",
                    "field": field,
                    "bad_value": "Column missing",
                    "error_type": "Missing Column",
                    "description": f"Required column '{field}' does not exist in the file at all.",
                })
            continue

        for idx, raw_val in df[field].items():
            row_num = idx + 2
            val = str(raw_val).strip() if not pd.isna(raw_val) else ""

            if rules["required"] and (pd.isna(raw_val) or val == "" or val.lower() == "nan"):
                errors.append({
                    "row": row_num,
                    "field": field,
                    "bad_value": "(empty)",
                    "error_type": "Missing Required Value",
                    "description": f"'{field}' is a mandatory field in SAP EC. Row {row_num} has no value.",
                })
                continue

            if val == "" or val.lower() == "nan":
                continue

            if rules["type"] == "date":
                result, fmt = validate_date(raw_val)
                if result is False:
                    errors.append({
                        "row": row_num, "field": field, "bad_value": val,
                        "error_type": "Invalid Date Format",
                        "description": f"SAP EC requires dates as YYYY-MM-DD. '{val}' cannot be understood.",
                    })
                elif fmt and fmt != "%Y-%m-%d":
                    corrected.at[idx, field] = result
                    errors.append({
                        "row": row_num, "field": field, "bad_value": val,
                        "error_type": "Date Format (Auto-fixed)",
                        "description": f"Reformatted '{val}' → '{result}' to match SAP EC standard YYYY-MM-DD.",
                    })

            elif rules["type"] == "picklist":
                if val not in rules["values"]:
                    errors.append({
                        "row": row_num, "field": field, "bad_value": val,
                        "error_type": "Invalid Picklist Value",
                        "description": f"'{val}' is not accepted for '{field}'. Valid options: {', '.join(rules['values'])}.",
                    })

            if rules.get("max_len") and len(val) > rules["max_len"]:
                errors.append({
                    "row": row_num, "field": field,
                    "bad_value": val[:25] + "...",
                    "error_type": "Exceeds Max Length",
                    "description": f"'{field}' allows max {rules['max_len']} characters. This value has {len(val)}.",
                })

            if rules["type"] == "email" and "@" not in val:
                errors.append({
                    "row": row_num, "field": field, "bad_value": val,
                    "error_type": "Invalid Email",
                    "description": f"'{val}' is not a valid email. SAP EC uses email as login identifier.",
                })

    return errors, corrected
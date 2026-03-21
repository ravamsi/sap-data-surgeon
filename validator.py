import pandas as pd
from datetime import datetime

# ── SAP EC Field Schema ──
SAP_EC_SCHEMA = {
    "userId":         {"required": True,  "type": "string",   "max_len": 100},
    "firstName":      {"required": True,  "type": "string",   "max_len": 128},
    "lastName":       {"required": True,  "type": "string",   "max_len": 128},
    "hireDate":       {"required": True,  "type": "date"},
    "startDate":      {"required": True,  "type": "date"},
    "country":        {"required": True,  "type": "picklist", "values": [
        "ITA","DEU","GBR","FRA","ESP","NLD","USA","IND","CHE","BEL",
        "AUT","SWE","NOR","DNK","FIN","PRT","GRC","POL","CZE","HUN",
        "ROU","BGR","HRV","SVK","SVN","EST","LVA","LTU","LUX","MLT",
        "CYP","IRL","CHN","JPN","KOR","AUS","NZL","CAN","MEX","BRA",
        "ARG","ZAF","SGP","HKG","ARE","SAU","TUR","ISR","EGY","NGA",
        "PHL","IDN","MYS","THA","VNM","PAK","BGD","LKA","NPL","MMR",
    ]},
    "company":        {"required": True,  "type": "string",   "max_len": 128},
    "businessUnit":   {"required": False, "type": "string",   "max_len": 128},
    "department":     {"required": True,  "type": "string",   "max_len": 128},
    "division":       {"required": False, "type": "string",   "max_len": 128},
    "jobCode":        {"required": True,  "type": "string",   "max_len": 32},
    "payGroup":       {"required": True,  "type": "string",   "max_len": 32},
    "email":          {"required": True,  "type": "email"},
    "gender":         {"required": True,  "type": "picklist", "values": ["M","F","N","U"]},
    "employmentType": {"required": True,  "type": "picklist", "values": [
        "Employee","Contractor","Contingent Worker"
    ]},
    "contractType":   {"required": False, "type": "picklist", "values": [
        "Permanent","Fixed-Term","Temporary"
    ]},
    "payFrequency":   {"required": False, "type": "picklist", "values": [
        "Monthly","Weekly","Bi-Weekly","Semi-Monthly"
    ]},
    "managerId":      {"required": False, "type": "string",   "max_len": 100},
    "costCenter":     {"required": False, "type": "string",   "max_len": 64},
}

# ── Column name variations → SAP EC standard ──
COLUMN_MAPPING = {
    # userId
    "employee id":       "userId",
    "employee_id":       "userId",
    "emp id":            "userId",
    "emp_id":            "userId",
    "staff id":          "userId",
    "staff_id":          "userId",
    "personnel number":  "userId",
    "person id":         "userId",
    "person_id":         "userId",
    "user id":           "userId",
    "worker id":         "userId",
    "id":                "userId",

    # firstName
    "first name":        "firstName",
    "first_name":        "firstName",
    "firstname":         "firstName",
    "given name":        "firstName",
    "given_name":        "firstName",
    "forename":          "firstName",
    "vorname":           "firstName",
    "prénom":            "firstName",

    # lastName
    "last name":         "lastName",
    "last_name":         "lastName",
    "lastname":          "lastName",
    "surname":           "lastName",
    "family name":       "lastName",
    "family_name":       "lastName",
    "nachname":          "lastName",
    "nom":               "lastName",

    # hireDate
    "hire date":         "hireDate",
    "hire_date":         "hireDate",
    "hiredate":          "hireDate",
    "date of hire":      "hireDate",
    "joining date":      "hireDate",
    "joining_date":      "hireDate",
    "date joined":       "hireDate",
    "employment date":   "hireDate",
    "start of employment": "hireDate",

    # startDate
    "start date":        "startDate",
    "start_date":        "startDate",
    "startdate":         "startDate",
    "employment start":  "startDate",
    "position start":    "startDate",
    "effective date":    "startDate",

    # country
    "country":           "country",
    "country code":      "country",
    "nation":            "country",
    "land":              "country",
    "pays":              "country",

    # company
    "company":           "company",
    "company name":      "company",
    "legal entity":      "company",
    "organisation":      "company",
    "organization":      "company",
    "employer":          "company",
    "firm":              "company",

    # businessUnit
    "business unit":     "businessUnit",
    "business_unit":     "businessUnit",
    "businessunit":      "businessUnit",
    "bu":                "businessUnit",
    "business area":     "businessUnit",

    # department
    "department":        "department",
    "dept":              "department",
    "team":              "department",
    "abteilung":         "department",
    "service":           "department",

    # division
    "division":          "division",
    "div":               "division",
    "segment":           "division",
    "group":             "division",

    # jobCode
    "job code":          "jobCode",
    "job_code":          "jobCode",
    "jobcode":           "jobCode",
    "job title":         "jobCode",
    "job_title":         "jobCode",
    "jobtitle":          "jobCode",
    "position":          "jobCode",
    "position code":     "jobCode",
    "role":              "jobCode",
    "title":             "jobCode",
    "function":          "jobCode",

    # payGroup
    "pay group":         "payGroup",
    "pay_group":         "payGroup",
    "paygroup":          "payGroup",
    "payroll group":     "payGroup",
    "payroll_group":     "payGroup",
    "salary group":      "payGroup",

    # email
    "email":             "email",
    "email address":     "email",
    "email_address":     "email",
    "emailaddress":      "email",
    "work email":        "email",
    "corporate email":   "email",
    "business email":    "email",
    "e-mail":            "email",

    # gender
    "gender":            "gender",
    "sex":               "gender",
    "geschlecht":        "gender",
    "genre":             "gender",

    # employmentType
    "employment type":   "employmentType",
    "employment_type":   "employmentType",
    "employmenttype":    "employmentType",
    "emp type":          "employmentType",
    "worker type":       "employmentType",
    "worker_type":       "employmentType",
    "contract category": "employmentType",

    # contractType
    "contract type":     "contractType",
    "contract_type":     "contractType",
    "contracttype":      "contractType",
    "employment contract": "contractType",

    # payFrequency
    "pay frequency":     "payFrequency",
    "pay_frequency":     "payFrequency",
    "payfrequency":      "payFrequency",
    "payment frequency": "payFrequency",
    "salary frequency":  "payFrequency",

    # managerId
    "manager id":        "managerId",
    "manager_id":        "managerId",
    "managerid":         "managerId",
    "reports to":        "managerId",
    "reports_to":        "managerId",
    "supervisor id":     "managerId",
    "supervisor_id":     "managerId",
    "line manager":      "managerId",
    "direct manager":    "managerId",

    # costCenter
    "cost center":       "costCenter",
    "cost_center":       "costCenter",
    "costcenter":        "costCenter",
    "cc":                "costCenter",
    "cost centre":       "costCenter",
    "profit center":     "costCenter",
}

# ── Picklist value normalisation ──
PICKLIST_NORMALISATION = {
    "country": {
        "italy": "ITA", "italia": "ITA",
        "germany": "DEU", "deutschland": "DEU",
        "france": "FRA",
        "spain": "ESP", "españa": "ESP",
        "uk": "GBR", "united kingdom": "GBR",
        "great britain": "GBR", "england": "GBR",
        "netherlands": "NLD", "holland": "NLD",
        "usa": "USA", "united states": "USA",
        "united states of america": "USA", "us": "USA",
        "india": "IND",
        "switzerland": "CHE", "schweiz": "CHE",
        "suisse": "CHE",
        "belgium": "BEL", "belgique": "BEL",
        "belgië": "BEL",
        "austria": "AUT", "österreich": "AUT",
        "sweden": "SWE", "sverige": "SWE",
        "norway": "NOR", "norge": "NOR",
        "denmark": "DNK", "danmark": "DNK",
        "finland": "FIN", "suomi": "FIN",
        "portugal": "PRT",
        "greece": "GRC", "griechenland": "GRC",
        "poland": "POL", "polska": "POL",
        "czech republic": "CZE", "czechia": "CZE",
        "hungary": "HUN", "ungarn": "HUN",
        "romania": "ROU", "rumänien": "ROU",
        "croatia": "HRV",
        "ireland": "IRL", "irland": "IRL",
        "australia": "AUS",
        "new zealand": "NZL",
        "canada": "CAN",
        "mexico": "MEX", "méxico": "MEX",
        "brazil": "BRA", "brasil": "BRA",
        "argentina": "ARG",
        "south africa": "ZAF",
        "singapore": "SGP",
        "china": "CHN",
        "japan": "JPN",
        "south korea": "KOR", "korea": "KOR",
        "hong kong": "HKG",
        "uae": "ARE", "united arab emirates": "ARE",
        "saudi arabia": "SAU",
        "turkey": "TUR", "türkiye": "TUR",
        "israel": "ISR",
        "philippines": "PHL",
        "indonesia": "IDN",
        "malaysia": "MYS",
        "thailand": "THA",
        "vietnam": "VNM",
    },
    "gender": {
        "male": "M", "man": "M", "mann": "M",
        "m": "M", "masculin": "M",
        "female": "F", "woman": "F", "frau": "F",
        "f": "F", "féminin": "F",
        "non-binary": "N", "nonbinary": "N",
        "non binary": "N", "diverse": "N",
        "divers": "N",
        "undisclosed": "U", "prefer not to say": "U",
        "not disclosed": "U", "unknown": "U",
        "unspecified": "U",
    },
    "employmentType": {
        "full-time": "Employee",
        "full time": "Employee",
        "fulltime": "Employee",
        "permanent": "Employee",
        "regular": "Employee",
        "staff": "Employee",
        "part-time": "Employee",
        "part time": "Employee",
        "parttime": "Employee",
        "freelance": "Contractor",
        "consultant": "Contractor",
        "self-employed": "Contractor",
        "contractor": "Contractor",
        "temp": "Contingent Worker",
        "temporary": "Contingent Worker",
        "intern": "Contingent Worker",
        "internship": "Contingent Worker",
        "trainee": "Contingent Worker",
        "apprentice": "Contingent Worker",
    },
    "contractType": {
        "permanent": "Permanent",
        "indefinite": "Permanent",
        "open-ended": "Permanent",
        "fixed term": "Fixed-Term",
        "fixed-term": "Fixed-Term",
        "fixedterm": "Fixed-Term",
        "limited": "Fixed-Term",
        "temporary": "Temporary",
        "temp": "Temporary",
    },
    "payFrequency": {
        "monthly": "Monthly",
        "month": "Monthly",
        "weekly": "Weekly",
        "week": "Weekly",
        "bi-weekly": "Bi-Weekly",
        "biweekly": "Bi-Weekly",
        "every two weeks": "Bi-Weekly",
        "fortnightly": "Bi-Weekly",
        "semi-monthly": "Semi-Monthly",
        "semi monthly": "Semi-Monthly",
        "twice a month": "Semi-Monthly",
        "twice monthly": "Semi-Monthly",
    },
}


def validate_date(value):
    """Check if value is a valid date. Returns (standardised_string, original_format) or (False, None)."""
    if pd.isna(value) or str(value).strip() == "":
        return None, None
    s = str(value).strip()
    for fmt in [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
        "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y",
        "%Y.%m.%d", "%d %b %Y", "%d %B %Y",
        "%b %d %Y", "%B %d %Y",
    ]:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d"), fmt
        except ValueError:
            continue
    return False, None


def normalise_columns(df):
    """
    Remap common column name variations to SAP EC standard names.
    Returns (normalised_df, dict_of_changes).
    """
    original_cols = list(df.columns)
    new_cols = []
    changes = {}

    for col in original_cols:
        normalised = col.lower().strip()
        # Remove common noise characters
        normalised = normalised.replace("*", "").replace("(required)", "").strip()
        mapped = COLUMN_MAPPING.get(normalised, col)
        new_cols.append(mapped)
        if mapped != col:
            changes[col] = mapped

    df.columns = new_cols
    return df, changes


def normalise_picklists(df):
    """
    Auto-correct common picklist value variations to SAP EC accepted values.
    Returns (normalised_df, dict_of_corrections).
    """
    corrections = {}
    for field, mapping in PICKLIST_NORMALISATION.items():
        if field not in df.columns:
            continue
        for idx, val in df[field].items():
            if pd.isna(val):
                continue
            val_str = str(val).lower().strip()
            if val_str in mapping:
                corrected = mapping[val_str]
                if corrected != str(val):
                    if field not in corrections:
                        corrections[field] = []
                    corrections[field].append(
                        {"row": idx + 2, "original": str(val), "corrected": corrected}
                    )
                    df.at[idx, field] = corrected
    return df, corrections


def validate_file(df):
    """
    Main validation function.
    Returns (list_of_errors, corrected_dataframe).
    """
    errors = []

    # Step 1 — Normalise column names
    df, col_changes = normalise_columns(df)

    # Step 2 — Normalise picklist values
    df, picklist_fixes = normalise_picklists(df)

    # Add picklist auto-corrections to error log as "Auto-fixed"
    for field, fix_list in picklist_fixes.items():
        for fix in fix_list:
            errors.append({
                "row": fix["row"],
                "field": field,
                "bad_value": fix["original"],
                "error_type": "Picklist Value (Auto-fixed)",
                "description": (
                    f"'{fix['original']}' auto-corrected to "
                    f"'{fix['corrected']}' — SAP EC standard value."
                ),
            })

    corrected = df.copy()

    # Step 3 — Duplicate userId check
    if "userId" in df.columns:
        dupes = df[df.duplicated("userId", keep=False)]["userId"].dropna().unique()
        for uid in dupes:
            rows = df[df["userId"] == uid].index.tolist()
            errors.append({
                "row": str([r + 2 for r in rows]),
                "field": "userId",
                "bad_value": str(uid),
                "error_type": "Duplicate ID",
                "description": (
                    f"userId '{uid}' appears {len(rows)} times. "
                    "Every employee must have a unique identifier in SAP EC."
                ),
            })

    # Step 4 — Field-by-field validation
    for field, rules in SAP_EC_SCHEMA.items():
        if field not in df.columns:
            if rules["required"]:
                errors.append({
                    "row": "ALL",
                    "field": field,
                    "bad_value": "Column missing",
                    "error_type": "Missing Column",
                    "description": (
                        f"Required column '{field}' does not exist in the file."
                    ),
                })
            continue

        for idx, raw_val in df[field].items():
            row_num = idx + 2
            val = str(raw_val).strip() if not pd.isna(raw_val) else ""

            # Required check
            if rules["required"] and (
                pd.isna(raw_val) or val == "" or val.lower() == "nan"
            ):
                errors.append({
                    "row": row_num,
                    "field": field,
                    "bad_value": "(empty)",
                    "error_type": "Missing Required Value",
                    "description": (
                        f"'{field}' is mandatory in SAP EC. Row {row_num} is empty."
                    ),
                })
                continue

            if val == "" or val.lower() == "nan":
                continue

            # Date validation + auto-correction
            if rules["type"] == "date":
                result, fmt = validate_date(raw_val)
                if result is False:
                    errors.append({
                        "row": row_num,
                        "field": field,
                        "bad_value": val,
                        "error_type": "Invalid Date Format",
                        "description": (
                            f"SAP EC requires dates as YYYY-MM-DD. "
                            f"'{val}' cannot be parsed."
                        ),
                    })
                elif fmt and fmt != "%Y-%m-%d":
                    corrected.at[idx, field] = result
                    errors.append({
                        "row": row_num,
                        "field": field,
                        "bad_value": val,
                        "error_type": "Date Format (Auto-fixed)",
                        "description": (
                            f"Reformatted '{val}' → '{result}' "
                            f"to match SAP EC standard YYYY-MM-DD."
                        ),
                    })

            # Picklist validation
            elif rules["type"] == "picklist":
                if val not in rules["values"]:
                    errors.append({
                        "row": row_num,
                        "field": field,
                        "bad_value": val,
                        "error_type": "Invalid Picklist Value",
                        "description": (
                            f"'{val}' is not accepted for '{field}'. "
                            f"Valid values: {', '.join(rules['values'])}."
                        ),
                    })

            # Max length
            if rules.get("max_len") and len(val) > rules["max_len"]:
                errors.append({
                    "row": row_num,
                    "field": field,
                    "bad_value": val[:30] + "...",
                    "error_type": "Exceeds Max Length",
                    "description": (
                        f"'{field}' max is {rules['max_len']} characters. "
                        f"This value has {len(val)}."
                    ),
                })

            # Email format
            if rules["type"] == "email" and "@" not in val:
                errors.append({
                    "row": row_num,
                    "field": field,
                    "bad_value": val,
                    "error_type": "Invalid Email",
                    "description": (
                        f"'{val}' is not a valid email. "
                        "SAP EC uses email as the unique login identifier."
                    ),
                })

    # Step 5 — Cross-field validation

    # Rule 1: hireDate must not be after startDate
    if "hireDate" in df.columns and "startDate" in df.columns:
        for idx, row in df.iterrows():
            row_num = idx + 2
            hire  = str(row.get("hireDate",  "")).strip()
            start = str(row.get("startDate", "")).strip()
            if hire and start and hire != "nan" and start != "nan":
                h_result, _ = validate_date(hire)
                s_result, _ = validate_date(start)
                if h_result and s_result and h_result > s_result:
                    errors.append({
                        "row": row_num,
                        "field": "hireDate / startDate",
                        "bad_value": f"hireDate: {hire}, startDate: {start}",
                        "error_type": "Cross-Field Logic Error",
                        "description": (
                            f"hireDate ({hire}) is after startDate ({start}). "
                            "In SAP EC, hireDate must be on or before startDate."
                        ),
                    })

    # Rule 2: managerId must not equal userId
    if "managerId" in df.columns and "userId" in df.columns:
        for idx, row in df.iterrows():
            row_num = idx + 2
            uid = str(row.get("userId",    "")).strip()
            mid = str(row.get("managerId", "")).strip()
            if uid and mid and uid != "nan" and mid != "nan" and uid == mid:
                errors.append({
                    "row": row_num,
                    "field": "managerId / userId",
                    "bad_value": uid,
                    "error_type": "Cross-Field Logic Error",
                    "description": (
                        f"managerId equals userId ({uid}). "
                        "An employee cannot be their own manager in SAP EC."
                    ),
                })

    # Rule 3: Fixed-Term contract should have an endDate warning
    if "contractType" in df.columns:
        for idx, row in df.iterrows():
            row_num = idx + 2
            ct = str(row.get("contractType", "")).strip()
            if ct == "Fixed-Term":
                errors.append({
                    "row": row_num,
                    "field": "contractType",
                    "bad_value": "Fixed-Term",
                    "error_type": "Cross-Field Warning",
                    "description": (
                        "Fixed-Term contracts require an endDate in SAP EC. "
                        "Ensure endDate is populated before import."
                    ),
                })

    # Rule 4: Duplicate emails
    if "email" in df.columns:
        email_dupes = (
            df[df.duplicated("email", keep=False)]["email"].dropna().unique()
        )
        for email in email_dupes:
            rows = df[df["email"] == email].index.tolist()
            errors.append({
                "row": str([r + 2 for r in rows]),
                "field": "email",
                "bad_value": email,
                "error_type": "Duplicate Email",
                "description": (
                    f"Email '{email}' appears {len(rows)} times. "
                    "SAP EC uses email as a unique login identifier."
                ),
            })

    # Rule 5: payGroup / country mismatch warning
    if "payGroup" in df.columns and "country" in df.columns:
        for idx, row in df.iterrows():
            row_num = idx + 2
            country   = str(row.get("country",  "")).strip()
            pay_group = str(row.get("payGroup", "")).strip()
            if (country and pay_group
                    and country != "nan" and pay_group != "nan"):
                if (not pay_group.endswith(country)
                        and not pay_group.startswith("PG-" + country)):
                    errors.append({
                        "row": row_num,
                        "field": "payGroup / country",
                        "bad_value": f"payGroup: {pay_group}, country: {country}",
                        "error_type": "Cross-Field Warning",
                        "description": (
                            f"payGroup '{pay_group}' may not match "
                            f"country '{country}'. Verify this payGroup "
                            f"is configured for {country} in your SAP system."
                        ),
                    })

    return errors, corrected
import os
import re
import json
import pandas as pd
import pdfplumber

PDF_PATH = r"c:\\Users\\17868\\OneDrive\\Desktop\\0析出相\\Database\\Alan J. Ardell_2023JPED\\The Equilibrium α (Al-Li Solid Solution) and Metastable δ′ (Al3Li) Phase Boundaries in Aluminum–Lithium Alloys.pdf"
OUT_DIR = os.path.dirname(PDF_PATH)
RAW_TABLE_CSV = os.path.join(OUT_DIR, "table1_raw.csv")
RAW_TABLE_XLSX = os.path.join(OUT_DIR, "table1_raw.xlsx")
COEFFS_JSON = os.path.join(OUT_DIR, "table1_coeffs.json")

# Regex patterns for formulas commonly used in Table 1
# Polynomial: X(Li) = a0 + a1*T + a2*T^2 + a3*T^3
poly_pattern = re.compile(
    r"X\s*\(?Li\)?\s*=\s*([\-\d\.]+)\s*\+\s*([\-\d\.Ee]+)\s*\*?\s*T\s*\+\s*([\-\d\.Ee]+)\s*\*?\s*T\s*\^\s*2\s*\+\s*([\-\d\.Ee]+)\s*\*?\s*T\s*\^\s*3",
    re.IGNORECASE,
)

# Exponential: X_ae = A * exp(-B / (R*T)) or exp{-B/RT}
exp_pattern = re.compile(
    r"X\s*[_\-]?\s*ae\s*=\s*([\d\.]+)\s*\*?\s*exp\s*\{?\s*\-?\s*([\d\.,]+)\s*/\s*(?:R\s*\*?\s*T|RT)\s*\}?",
    re.IGNORECASE,
)

# Optional: capture model labels preceding formulas (e.g., author names)
label_pattern = re.compile(r"([A-Z][A-Za-z&\.\s]+):", re.IGNORECASE)

coeffs = []
all_tables = []

with pdfplumber.open(PDF_PATH) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        # Collect tables on this page
        try:
            tables = page.extract_tables() or []
        except Exception:
            tables = []
        for tbl in tables:
            # Normalize rows length by padding shorter rows
            max_len = max(len(r) for r in tbl) if tbl else 0
            normalized = [r + [None] * (max_len - len(r)) for r in tbl]
            df = pd.DataFrame(normalized)
            df["page"] = page_num
            all_tables.append(df)
        
        # Parse formulas directly from text
        # Find labels near formulas (best-effort)
        labels = label_pattern.findall(text)
        poly_matches = list(poly_pattern.finditer(text))
        exp_matches = list(exp_pattern.finditer(text))
        
        # Attach labels if count matches; otherwise generate generic labels
        for i, m in enumerate(poly_matches):
            a0, a1, a2, a3 = m.groups()
            try:
                label = labels[i] if i < len(labels) else f"Model_{len(coeffs)+1}"
            except Exception:
                label = f"Model_{len(coeffs)+1}"
            coeffs.append({
                "label": label.strip(),
                "type": "poly",
                "page": page_num,
                "a0": float(a0.replace(",", "")),
                "a1": float(a1.replace(",", "")),
                "a2": float(a2.replace(",", "")),
                "a3": float(a3.replace(",", "")),
            })
        
        for i, m in enumerate(exp_matches):
            A, B = m.groups()
            try:
                label = labels[i] if i < len(labels) else f"Model_{len(coeffs)+1}"
            except Exception:
                label = f"Model_{len(coeffs)+1}"
            coeffs.append({
                "label": label.strip(),
                "type": "exp",
                "page": page_num,
                "A": float(A.replace(",", "")),
                "B": float(B.replace(",", "")),
            })

# Save raw tables if any
if all_tables:
    big = pd.concat(all_tables, ignore_index=True)
    big.to_csv(RAW_TABLE_CSV, index=False, encoding="utf-8-sig")
    # Try to make a nicer Excel with one sheet per page
    with pd.ExcelWriter(RAW_TABLE_XLSX, engine="openpyxl") as writer:
        for page_num in sorted(set(big["page"])):
            sub = big[big["page"] == page_num].drop(columns=["page"]) 
            # Give a default header
            sub.columns = [f"col_{i+1}" for i in range(sub.shape[1])] 
            sub.to_excel(writer, index=False, sheet_name=f"page_{page_num}")

# Save parsed coefficients
with open(COEFFS_JSON, "w", encoding="utf-8") as f:
    json.dump({"coeffs": coeffs}, f, ensure_ascii=False, indent=2)

print(f"Saved raw tables to: {RAW_TABLE_CSV} / {RAW_TABLE_XLSX}")
print(f"Parsed {len(coeffs)} formulas; saved to: {COEFFS_JSON}")
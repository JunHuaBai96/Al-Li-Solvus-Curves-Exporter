import pdfplumber, os
PDF_PATH = r"c:\\Users\\17868\\OneDrive\\Desktop\\0析出相\\Database\\Alan J. Ardell_2023JPED\\The Equilibrium α (Al-Li Solid Solution) and Metastable δ′ (Al3Li) Phase Boundaries in Aluminum–Lithium Alloys.pdf"
OUT_TXT = os.path.join(os.path.dirname(PDF_PATH), "pdf_full_text.txt")
all_text = []
with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        txt = page.extract_text() or ""
        all_text.append(f"===== PAGE {i} =====\n" + txt + "\n")
open(OUT_TXT, "w", encoding="utf-8").write("\n".join(all_text))
print("Saved:", OUT_TXT)
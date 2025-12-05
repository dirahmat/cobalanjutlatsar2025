# ===============================================================
# 1_Kekurangan_Upah.py  —  Refactored Multi-Page Version
# ===============================================================

import streamlit as st
import pandas as pd
import re

from utils.constants import MIN_UPAH, BULAN, BULAN_BY_TAHUN, ROWS_PER_PAGE
from utils.state_utils import init_page_state, get, set, clear_other_states
from utils.formatters import sanitize_number, format_with_dots
from utils.exporters import export_excel, export_word

# ---------------------------------------------------------------
# PAGE INITIALIZATION
# ---------------------------------------------------------------
PREFIX = "upah_"
clear_other_states(PREFIX)

init_page_state(PREFIX, {
    "num_rows": 1,
    "page": 1,
    "imported": False,
    "data": [],          # Raw imported rows
    "Upah": {},          # Upah per row
    "Nama": {},
    "Tahun": {},
    "Bulan": {},
})


# ---------------------------------------------------------------
# VALIDATION OF IMPORTED FILE
# ---------------------------------------------------------------
def validate_import(df: pd.DataFrame):
    errors = []
    required = ["Nama", "Tahun", "Bulan", "Upah"]

    # Missing columns
    for col in required:
        if col not in df.columns:
            errors.append(f"❌ Kolom '{col}' tidak ditemukan.")

    if errors:
        return errors, None

    df = df[required].copy()

    # Tahun tidak valid
    invalid_years = df[~df["Tahun"].isin(MIN_UPAH.keys())]
    if not invalid_years.empty:
        errors.append(
            f"Salah Tahun: {', '.join(map(str, invalid_years['Tahun'].unique()))}"
        )

    # Bulan tidak valid
    invalid_months = df[~df["Bulan"].isin(BULAN)]
    if not invalid_months.empty:
        errors.append(
            f"Salah Bulan: {', '.join(map(str, invalid_months['Bulan'].unique()))}"
        )

    # Kosong
    if df.isna().any().any():
        errors.append("❌ Ada nilai kosong.")

    # Duplicate rows
    df["key"] = (
        df["Nama"].astype(str).str.lower().str.strip()
        + "_"
        + df["Tahun"].astype(str)
        + "_"
        + df["Bulan"]
    )
    dups = df[df.duplicated("key", keep=False)]
    if not dups.empty:
        errors.append("❌ Ada data duplikat pada file.")

    df.drop(columns=["key"], inplace=True)

    # Format Upah
    df["Upah"] = df["Upah"].astype(str)

    return errors, df


# ---------------------------------------------------------------
# COMPUTATION LOGIC
# ---------------------------------------------------------------
def compute_row(nama, tahun, bulan, upah):
    upah_val = sanitize_number(upah)
    ump_val = MIN_UPAH[tahun]

    if upah_val == 0:
        return {
            "Nama": nama,
            "Tahun": tahun,
            "Bulan": bulan,
            "Upah": "-",
            "UMP": format_with_dots(ump_val),
            "Selisih": "-",
            "DiffNumeric": 0,
        }

    diff = upah_val - ump_val
    if diff > 0:  # No positive diff allowed
        diff = 0

    return {
        "Nama": nama,
        "Tahun": tahun,
        "Bulan": bulan,
        "Upah": format_with_dots(upah_val),
        "UMP": format_with_dots(ump_val),
        "Selisih": format_with_dots(diff),
        "DiffNumeric": diff,
    }


def compute_all():
    results = []
    n = get(PREFIX, "num_rows")

    seen = set()
    for i in range(n):
        nama = get(PREFIX, f"Nama_{i}") or ""
        tahun = get(PREFIX, f"Tahun_{i}") or 2023
        bulan = get(PREFIX, f"Bulan_{i}") or "Januari"
        upah = get(PREFIX, f"Upah_{i}") or ""

        key = (nama.lower(), tahun, bulan)
        if key in seen:
            continue
        seen.add(key)

        results.append(compute_row(nama, tahun, bulan, upah))

    return pd.DataFrame(results)


# ---------------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------------
st.title("📊 Penghitungan Kekurangan Upah Terhadap UMP Jakarta (Refactored)")


# ---------------------------------------------------------------
# IMPORT EXCEL SECTION
# ---------------------------------------------------------------
st.subheader("📂 Impor File Excel")

file = st.file_uploader("Unggah file (kolom: Nama, Tahun, Bulan, Upah)", type=["xlsx", "xls"])

if file:
    try:
        df_import = pd.read_excel(file)
        errors, df_valid = validate_import(df_import)

        if errors:
            st.error("File memiliki masalah:")
            for e in errors:
                st.write(e)
        else:
            st.success("File berhasil diimpor!")

            set(PREFIX, "imported", True)
            set(PREFIX, "data", df_valid.to_dict(orient="records"))
            set(PREFIX, "num_rows", len(df_valid))

            # Load into session state
            for i, row in enumerate(df_valid.to_dict(orient="records")):
                set(PREFIX, f"Nama_{i}", row["Nama"])
                set(PREFIX, f"Tahun_{i}", row["Tahun"])
                set(PREFIX, f"Bulan_{i}", row["Bulan"])
                set(PREFIX, f"Upah_{i}", row["Upah"])

    except Exception as e:
        st.error(f"❌ Tidak bisa membaca file: {e}")


# ---------------------------------------------------------------
# MANUAL INPUT ROW COUNT
# ---------------------------------------------------------------
st.subheader("🔢 Jumlah Baris Data")

num_rows = st.number_input(
    "Jumlah baris yang ingin dihitung:",
    min_value=1,
    max_value=200,
    value=get(PREFIX, "num_rows"),
)

set(PREFIX, "num_rows", num_rows)


# ---------------------------------------------------------------
# PAGINATION
# ---------------------------------------------------------------
total_pages = (num_rows - 1) // ROWS_PER_PAGE + 1
page = get(PREFIX, "page")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Sebelumnya", disabled=page <= 1):
        set(PREFIX, "page", page - 1)
        st.experimental_rerun()

with col3:
    if st.button("Berikutnya ➡️", disabled=page >= total_pages):
        set(PREFIX, "page", page + 1)
        st.experimental_rerun()

with col2:
    st.markdown(f"<div style='text-align:center;'>Halaman {page} dari {total_pages}</div>", unsafe_allow_html=True)


start = (page - 1) * ROWS_PER_PAGE
end = min(start + ROWS_PER_PAGE, num_rows)


# ---------------------------------------------------------------
# INPUT TABLE
# ---------------------------------------------------------------
st.subheader("✏️ Input Data")

cols = st.columns([2, 1, 1, 2])

headers = ["Nama", "Tahun", "Bulan", "Upah"]
for c, h in zip(cols, headers):
    c.markdown(f"**{h}**")

for i in range(start, end):
    # Nama
    with cols[0]:
        set(PREFIX, f"Nama_{i}",
            st.text_input(f"Nama_{i}", get(PREFIX, f"Nama_{i}") or ""))

    # Tahun
    with cols[1]:
        tahun_val = st.selectbox(
            f"Tahun_{i}",
            list(MIN_UPAH.keys()),
            index=list(MIN_UPAH.keys()).index(
                get(PREFIX, f"Tahun_{i}") or 2023
            ),
        )
        set(PREFIX, f"Tahun_{i}", tahun_val)

    # Bulan (depends on year)
    valid_months = BULAN_BY_TAHUN.get(tahun_val, BULAN)
    cur_month = get(PREFIX, f"Bulan_{i}") or valid_months[0]
    if cur_month not in valid_months:
        cur_month = valid_months[0]

    with cols[2]:
        set(PREFIX, f"Bulan_{i}", st.selectbox(f"Bulan_{i}", valid_months, index=valid_months.index(cur_month)))

    # Upah
    with cols[3]:
        raw = st.text_input(f"Upah_{i}", get(PREFIX, f"Upah_{i}") or "")
        set(PREFIX, f"Upah_{i}", raw)


# ---------------------------------------------------------------
# OUTPUT TABLE
# ---------------------------------------------------------------
st.subheader("📄 Hasil Perhitungan")

df_result = compute_all()

if len(df_result) > 0:
    total = df_result["DiffNumeric"].sum()
    df_display = df_result.drop(columns=["DiffNumeric"]).copy()

    # Add total row
    df_display.loc[len(df_display)] = {
        "Nama": "",
        "Tahun": "",
        "Bulan": "Total",
        "Upah": "",
        "UMP": "",
        "Selisih": format_with_dots(total),
    }

    st.dataframe(df_display)

    # Export buttons
    st.download_button(
        "📥 Ekspor Excel",
        data=export_excel(df_display),
        file_name="Kekurangan_Upah.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.download_button(
        "📄 Ekspor Word",
        data=export_word(df_display),
        file_name="Kekurangan_Upah.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
else:
    st.info("Tidak ada data untuk ditampilkan.")

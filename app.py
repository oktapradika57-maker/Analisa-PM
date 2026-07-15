import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Konfigurasi Halaman agar lebar (wide) menyerupai dashboard
st.set_page_config(page_title="Dashboard PM Kalimantan", layout="wide")

# Judul Dashboard
st.title("Progress PMS & PMG KUT KALIMANTAN JULI 2026")
st.text(datetime.now().strftime("%d/%m/%Y %H:%M"))

st.markdown("---")

# 1. Kolom Drop File / Uploader
uploaded_file = st.file_uploader("Drop file Excel analisa di sini (.xlsx)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Membaca file excel menggunakan Pandas
    xls = pd.ExcelFile(uploaded_file)
    
    with st.spinner('Membaca dan menganalisa data...'):
        # ==========================================
        # A. TARIK DATA DARI SHEET 'Dasboard'
        # ==========================================
        try:
            df_dash = pd.read_excel(xls, sheet_name='Dasboard', header=None)
            
            # Tabel Kanan Atas (Status SWFM)
            # Berdasarkan struktur file excel, ambil baris 7 s.d 23 dan kolom yang relevan
            tabel_swfm = df_dash.iloc[8:24, [11, 12, 13, 14, 15, 17]].copy()
            tabel_swfm.columns = ["NOP", "PM Status", "Count of Site", "Total Closed", "% Ach", "Rank"]
            tabel_swfm = tabel_swfm.dropna(subset=['Count of Site']) # Bersihkan baris kosong
            tabel_swfm['% Ach'] = pd.to_numeric(tabel_swfm['% Ach'], errors='coerce')
            
            # Tabel Kanan Bawah (Daily Achievement)
            tabel_daily = df_dash.iloc[29:45, [11, 12, 13, 14, 15, 17, 18]].copy()
            tabel_daily.columns = ["NOP", "PM Status", "Count of Site", "Close", "Open", "Done", "Ach/Day"]
            tabel_daily = tabel_daily.dropna(subset=['Count of Site'])
            
            # Tabel Kiri Bawah (Highlight)
            highlight_df = df_dash.iloc[47:58, 0:1].dropna().rename(columns={0: "Highlight"})
            
        except Exception as e:
            st.error(f"Gagal membaca sheet 'Dasboard': {e}")
            tabel_swfm, tabel_daily, highlight_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # ==========================================
        # B. TARIK DATA DARI SHEET 'Update data'
        # ==========================================
        try:
            df_update = pd.read_excel(xls, sheet_name='Update data', header=None)
            
            # Ambil deret tanggal (Row 31, mulai kolom 1)
            raw_dates = df_update.iloc[31, 1:32].dropna().tolist() 
            dates = [pd.to_datetime(d).strftime('%d-%b-%y') for d in raw_dates if pd.notnull(d)]
            
            # Data Grafik 1: PM SITE (PMS) - Baris 48 (Plan), 50 (Actual), 51 (Ach %)
            pms_plan = df_update.iloc[48, 1:len(dates)+1].tolist()
            pms_actual = df_update.iloc[50, 1:len(dates)+1].tolist()
            pms_ach = df_update.iloc[51, 1:len(dates)+1].tolist()
            
            # Data Grafik 2: PM GENSET (PMG) - Baris 40 (Plan), 42 (Actual), 43 (Ach %)
            pmg_plan = df_update.iloc[40, 1:len(dates)+1].tolist()
            pmg_actual = df_update.iloc[42, 1:len(dates)+1].tolist()
            pmg_ach = df_update.iloc[43, 1:len(dates)+1].tolist()
            
        except Exception as e:
            st.error(f"Gagal membaca sheet 'Update data': {e}")
            dates, pms_plan, pms_actual, pms_ach = [], [], [], []
            pmg_plan, pmg_actual, pmg_ach = [], [], []

        # ==========================================
        # C. TATA LETAK TAMPILAN DASHBOARD (2 Kolom)
        # ==========================================
        col_left, col_right = st.columns([1.2, 1], gap="large")

        with col_left:
            # Fungsi bantuan untuk membuat Grafik Dual-Axis
            def create_chart(title, plan, actual, ach):
                fig = go.Figure()
                # Garis Plan Cumm
                fig.add_trace(go.Scatter(x=dates, y=plan, mode='lines+markers', name='Plan Cumm', line=dict(color='#ff7f0e', width=3)))
                # Garis Actual Cumm
                fig.add_trace(go.Scatter(x=dates, y=actual, mode='lines+markers', name='Actual Cumm', line=dict(color='#ffbb78', width=3)))
                # Garis Ach % (Sumbu Y ke-2)
                fig.add_trace(go.Scatter(x=dates, y=ach, mode='lines+markers', name='Cumm Ach %', yaxis='y2', line=dict(color='#1f77b4', width=3)))
                
                fig.update_layout(
                    title=dict(text=title, x=0.5), # Judul di tengah
                    yaxis=dict(title='', range=[0, max(max(plan), max(actual))*1.2]),
                    yaxis2=dict(title='', overlaying='y', side='right', tickformat='.0%', range=[0, 1]),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=300
                )
                return fig

            # Tampilkan Grafik
            if dates:
                st.plotly_chart(create_chart("PM SITE DAILY PROGRESS KALIMANTAN_KUT", pms_plan, pms_actual, pms_ach), use_container_width=True)
                st.plotly_chart(create_chart("PM GENSET DAILY PROGRESS", pmg_plan, pmg_actual, pmg_ach), use_container_width=True)
            
            # Tampilkan Highlight Box
            st.markdown("### Highlight : 14 Juli 2026")
            st.dataframe(highlight_df, use_container_width=True, hide_index=True)

        with col_right:
            st.markdown("### Status SWFM")
            # Tampilkan tabel pertama dengan format persentase di kolom % Ach
            st.dataframe(
                tabel_swfm.style.format({'% Ach': '{:.0%}', 'Rank': '{:.0f}'}, na_rep="-"), 
                use_container_width=True, 
                hide_index=True
            )
            
            st.markdown("<br><br>", unsafe_allow_html=True) # Jarak
            
            st.markdown(f"### Update: {datetime.now().strftime('%m/%d/%Y')}")
            # Tampilkan tabel kedua dengan format data numerik yang rapi
            st.dataframe(
                tabel_daily.style.format({'Count of Site': '{:.0f}', 'Close': '{:.0f}', 'Open': '{:.0f}', 'Done': '{:.0f}', 'Ach/Day': '{:.0%}'}, na_rep="-"), 
                use_container_width=True, 
                hide_index=True
            )
else:
    st.info("Silakan unggah (drop) file Excel Anda pada uploader di atas untuk memunculkan analisa Dashboard.")

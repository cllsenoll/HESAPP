import streamlit as st
import pandas as pd
import io
import re
import streamlit.components.v1 as components

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Görükle Acente", layout="wide")

# 2. OTURUM DURUMU
if 'active_tab' not in st.session_state: st.session_state.active_tab = "HESAP"
if 'f4_df' not in st.session_state: st.session_state.f4_df = None
if 'editable_f4_df' not in st.session_state: st.session_state.editable_f4_df = None

# CSS
st.markdown("<style>.stApp { background-color: #0B192C; color: white; }</style>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    uploaded_file = st.file_uploader("📂 Rapor Yükle", type=['csv', 'xlsx'])
    if st.button("💰 HESAP"): st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"): st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# DOSYA İŞLEME (Örnek mantık - mevcut mantığınızı buraya koruyabilirsiniz)
if uploaded_file and "F4" in uploaded_file.name.upper():
    # Mevcut dosya okuma mantığınızı buraya yerleştirin
    st.session_state.f4_df = pd.DataFrame({"Müşteri Adı": ["Örnek A.Ş."], "Fatura Borcu": [1500.0], "Personel": ["ATANMAMIŞ"]})

# TABLAR
if st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.markdown("### 📋 F4 Ödeme Listesi")
    if st.session_state.f4_df is not None:
        # Yazdır butonu
        if st.button("🖨️ Listeyi Yazdır"):
            components.html("<script>window.print();</script>", height=0)
        
        # Yazdırılacak alanı izole eden CSS ve HTML
        st.markdown(
            """
            <style>
                @media print {
                    body * { visibility: hidden; }
                    #f4-print-area, #f4-print-area * { visibility: visible; }
                    #f4-print-area { position: absolute; left: 0; top: 0; width: 100%; }
                }
            </style>
            <div id='f4-print-area'>
            """, unsafe_allow_html=True
        )

        # Düzenlenebilir tablo
        if st.session_state.editable_f4_df is None:
            st.session_state.editable_f4_df = st.session_state.f4_df.copy()

        edited_df = st.data_editor(st.session_state.editable_f4_df, use_container_width=True)
        st.session_state.editable_f4_df = edited_df
        
        # Yazdırma alanı sonu
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Lütfen bir F4 dosyası yükleyin.")

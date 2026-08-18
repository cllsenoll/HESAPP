import streamlit as st
import pandas as pd
import io
import re
import urllib.parse
import streamlit.components.v1 as components
from weasyprint import HTML # PDF oluşturmak için gereklidir

# --- ÖNCEKİ TÜM AYARLAR VE FONKSİYONLARINIZ AYNEN KORUNMUŞTUR ---
# (Önceki kodunuzdaki get_github_avatar, clean_string, parse_turkish_float, process_... fonksiyonlarını buraya eklediğinizi varsayıyorum)

# PDF OLUŞTURMA FONKSİYONU
def generate_pdf_from_df(df, personel_adi):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
            th {{ background-color: #0B192C; color: white; }}
            h2 {{ color: #0B192C; }}
        </style>
    </head>
    <body>
        <h2>Personel Ödeme Listesi: {personel_adi}</h2>
        <table>
            <thead><tr><th>Müşteri Adı</th><th>Fatura Borcu</th><th>Açıklama</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td>{row['Müşteri Adı']}</td><td>{row['Fatura Borcu']}</td><td>{row['Açıklama']}</td></tr>" for _, row in df.iterrows()])}
            </tbody>
        </table>
    </body>
    </html>
    """
    return HTML(string=html_content).write_pdf()

# ... [Mevcut kodunuzdaki diğer tüm tanımlamalar, CSS ve Sidebar yapısı burada yer almalı] ...

# F4 SEKMESİ (GÜNCELLENMİŞ HALİ)
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.markdown("### 📋 F4 Ödeme ve Kişisel Tahsilat Listesi")
    
    f4_df = st.session_state.get('f4_df', None)
    
    if f4_df is not None and not f4_df.empty:
        # 1. PERSONEL SEÇİMİ VE FİLTRELEME
        secili_personel = st.selectbox("Yazdırılacak Personeli Seçin:", PERSONEL_LISTESI)
        
        # Düzenlenebilir tablo
        if st.session_state.editable_f4_df is None:
            st.session_state.editable_f4_df = f4_df.copy()

        edited_df = st.data_editor(st.session_state.editable_f4_df, use_container_width=True)
        st.session_state.editable_f4_df = edited_df
        
        # 2. PDF İNDİRME ÖZELLİĞİ
        filtered_df = edited_df[edited_df['Personel'] == secili_personel]
        
        if not filtered_df.empty:
            pdf_data = generate_pdf_from_df(filtered_df, secili_personel)
            st.download_button(
                label=f"📥 {secili_personel} Listesini PDF İndir",
                data=pdf_data,
                file_name=f"{secili_personel}_Odeme_Listesi.pdf",
                mime="application/pdf"
            )
        else:
            st.warning(f"{secili_personel} adına kayıtlı ödeme bulunamadı.")
            
    else:
        st.info("ℹ️ Lütfen sol panelden F4 ödeme listesi içeren bir dosya yükleyin.")

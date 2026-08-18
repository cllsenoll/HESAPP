import streamlit as st
import pandas as pd
import io
import re
import urllib.parse
import streamlit.components.v1 as components

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Görükle Acente - Hesap & F4 Paneli",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU (Session State)
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "HESAP"
if 'account_df' not in st.session_state:
    st.session_state.account_df = None
if 'hesap_df' not in st.session_state:
    st.session_state.hesap_df = None
if 'kasa_miktari' not in st.session_state:
    st.session_state.kasa_miktari = 0.0
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'f4_df' not in st.session_state:
    st.session_state.f4_df = None
if 'editable_f4_df' not in st.session_state:
    st.session_state.editable_f4_df = None

KULLANICI_ISIM = "CELAL ŞENOL"
KULLANICI_GOREV = "(Şube Şefi)"

# ==========================================
# GİTHUB PERSONEL FOTOĞRAF HARİTASI
# ==========================================
def get_github_avatar(personel_adi):
    clean_name = str(personel_adi).strip()
    encoded_name = urllib.parse.quote(clean_name)
    return f"https://raw.githubusercontent.com/cllsenoll/F4-HESAP/main/{encoded_name}.png"

# ==========================================
# MÜŞTERİ - PERSONEL EŞLEŞTİRME SÖZLÜĞÜ
# ==========================================
MUSTERI_PERSONEL_MAP = {
    "KÜBRA AYDEMİR": "AHMET BERKAN ÖKSÜZ",
    "SERKAN KUYUMCU": "AHMET BERKAN ÖKSÜZ",
    "AKSUN AĞAÇ AMBALAJ KERESTE SAN. TİC.LTD.ŞTİ": "ALATTİN CEBECİ",
    "ARTEA DIŞ TİCARET MAKİNA SANAYİ LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "BAYAGRO TARIM İLAÇLARI SANAYİ VE TİCARETLTD. ŞTİ.": "ALATTİN CEBECİ",
    "BEREKET İLAÇ KOZMETİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "BURMOD TEKSTİL SAN.TİC.A.Ş.-BURSA ŞB.": "ALATTİN CEBECİ",
    "DEMİRCİOĞLU ŞASE ENDÜSTRİYEL YAĞ OTOMOTİV TEKSTİL GIDA İNŞAAT SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
    "EDDA MAKİNE AMBALAJ NAKLİYE İNŞAAT KİMYA SANAYİ TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "FLY MOBİLYA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "KOLİSAN AMBALAJ SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
    "M-BEND METAL ÇELİK MAKİNA İNŞAAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "MAVİFORM METAL KALIPFİKSTÜR VE APARAT SAN.VE TİC.LTD": "ALATTİN CEBECİ",
    "MERZE MOBİLYA TASARIM İNŞAAT SANAYİ TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "MNC BİTKİSEL VE SAĞLIK ÜRÜNLERİ REKLAM VE ORGANİZASYON BİLİŞİM TEKNOLOJİLERİ İNŞAAT SAN.TİC.LTD.ŞTİ.": "ALATTİN CEBECİ",
    "SOMBURSA BAĞLANTI ELEMANLARI TİCARET VESAN.VE A.Ş.": "ALATTİN CEBECİ",
    "ÖZBEYAZ DIŞ TİCARET TAŞIMACILIK ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "ALPER ŞEN": "BURCU DÜREN",
    "ALSTOM RAYLI SİSTEM SANAYİ ANONİM ŞİRKETİ": "BURCU DÜREN",
    "AMPHENOL TURKEY BAĞLANTI ÇÖZÜMLERİ LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "BAŞATLAR ORMAN ÜRÜNLERİ VE AMBALAJ SAN.TİC.LTD.ŞTİ.": "BURCU DÜREN",
    "D.K.C TEKNİK KAPLAMA APRE TEKSTİL KONFEKSİYON SERVİS TAŞIMACILIĞI SAN.VE TİC.LTD.ŞTİ.": "BURCU DÜREN",
    "DEBSA TASARIM KONFEKSİYON TEKSTİL SANAYİ TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "DEVSAN ENDÜSTRİYEL OTOMASYON MAKİNA SANAYİ VE TİCARET A.Ş.": "BURCU DÜREN",
    "DOĞANYİĞİTLER ORGANİK GIDA SANAYİ TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "DİLAN YILDIRIM - OLİNA BUTİK": "BURCU DÜREN",
    "ESAUTOMOTION MEKATRONİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "GENÇ GÖZDE TARIM MAKİNALARI SANAYİ VE TİC.LTD.ŞTİ.": "BURCU DÜREN",
    "GÜMÜŞ ARSLAN GENEL MAKİNE İMALATI ENERJİ VE ISI SİSTEMLERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "HMT MAKİNA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "JACQUARD FASHİON KONFEKSİYON TEKSTİL SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "KCL LOJİSTİK OTOMOTİV SANAYİ TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "MATAY OTOMOTİV YAN SANAYİ VE TİCARET A .Ş.": "BURCU DÜREN",
    "MİNTEKS TEKSTİL SAN VE TİC. LTD.ŞTİ. İŞLETME ADI:MİNTEKS": "BURCU DÜREN",
    "MS MOTION OTOMOTİV ANONİM ŞİRKETİ": "BURCU DÜREN",
    "NOBEL TEKNİK OTO YANSANAYİ VE TİCARET A.Ş.": "BURCU DÜREN",
    "ORCA HOME TEKSTİL İTHALAT İHRACATSANAYİ VE TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "OTEKSO MÜHENDİSLİK TASARIM MAKİNE SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "PROLİFT ASANSÖR SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "S.S.MARMARA ZEYTİN TARIM SAT.KOOP.BİR.MARMARABİRLİK": "BURCU DÜREN",
    "T-BİYOTEKNOLOJİ LABORATUVAR ESTETİK MEDİKAL KOZMETİK SANAYİVE TİCARET LTD.ŞTİ.": "BURCU DÜREN",
    "UĞURLU FİNİSAJ SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "VARNA DERİ SANAYİ VE TİCARET A.Ş.": "BURCU DÜREN",
    "VETABİL GIDA TARIM HAYVANCILIK LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "ÖZGÜR ULUS - MARANGOZ": "BURCU DÜREN",
    "İLK-SEZ ENDÜSTRİYEL OTOMASYON SİSTEMLERİ ELEKTRİK ELEKTRONİK MAKİNA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "ALTINSOY MADENCİLİKVE TİCARET A.Ş.": "CELAL ŞENOL",
    "ENDER DURSAK": "CELAL ŞENOL",
    "KAPLANLAR SOĞUTMA SAN.VE TİC.AŞ.": "CELAL ŞENOL",
    "NARVİN TEKSTİL EMLAK KOZMETİK SOSYAL MEDYA İHRACAT İTHALAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "SELFİE TARIMSAL TEDARİK SERACILIK DEPOCULUK DANIŞMANLIK SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "SERGEN GÖRÜROĞLU": "CELAL ŞENOL",
    "ARMENDUS OPERATÖR KOL VE PANO SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "BAROMAK MAKİNE SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "BİLEKLER İNŞAAT MAKİNALARI SANAYİ VETİCARET LTD.ŞTİ.": "HASAN SAĞLAM",
    "BURKON MOBİLYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "DICHERSEAL ELASTOMER TEKNOLOJİLERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "DİGİTORİUM ELEKTRONİK TEKNOLOJİLERİ ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA KABLOSİSTEMLERİ SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA GRUP MÜHENDİSLİK ELEKTRİK TAAHHÜT MEKANİK PANO İMALAT İTHALAT İHRACAT SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA PROJE ELEKTRİK MÜHENDİSLİK TAAHHÜT İNŞAAT ARAÇ KİRALAMA İTHALAT İHRACAT VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "F.S.K.MAKİNE İMALATTAAH.VE GIDA TEKN.SAN.T.LTD.ŞTİ.": "HASAN SAĞLAM",
    "IPM GALVANO YÜZEY KAPLAMA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "LİGNUM AĞAÇ MAKİNELERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "TEMPOLİFT ASANSÖR ELEKTRİK ELEKTRONİK SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "TURKAUTO MOTORLU ARAÇLAR SANAYİ VE TİCARET LİMİTED ŞİRKETİ.": "HASAN SAĞLAM",
    "VİYA OTOMOTİV CAM TURİZM DENİZCİLİK SANAYİ VE TİCARET LTD. ŞTİ.": "HASAN SAĞLAM",
    "YSL OTOMOTİV YAN SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ÖZGÖZDE OTOMOTİV İNŞAAT İŞ MAKİNALARI PETROL NAKLİYE VE TURİZM HİZMETLERİ SANAYİ TİCARET A.Ş.": "HASAN SAĞLAM",
    "ACH DIŞ TİCARET SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "AKEL DERİ TEKS.SAN.VE DIŞ TİC.LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "AYDEMİR DERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "BURSA DERİ İHTİSAS VE KARMA ORGANİZE SANAYİ BÖLGESİ": "SERGEN GÖRÜROĞLU",
    "BURSA JELATİN GIDA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "CİVAN GERİ DÖNÜŞÜM İZOLASYON PLASTİK METAL,İNŞAAT TAAH.SAN.VE TİC.LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "EMRE DERELİ - DERELİ MARİNE": "SERGEN GÖRÜROĞLU",
    "ERBA FİNİSAJ DERİ SANAYİ VE TİCARET LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "GESU ARITMA SİSTEMLERİ SANAYİ VE TİCARET LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "LAS-SAN LASTİK PLASTİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MECANICA CNC MAKİNE VE SERVİS LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MET-RİN DERİ MAKİNELERİ VE METAL SANAYİ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MORKİM KİMYA İNŞAAT İTHALAT İHRACAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MURSAN FİBERGLASS VE DENİZ ARAÇLARI TURİZM SANAYİ TİCARET PAZARLAMA LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "NOVMA KİMYA SANAYİ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "VAKETA DERİCİLİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "YILDIZ GRUBU DERİ KİMYA İNŞAAT TARIM SANAYİ VE DIŞ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "İDEA ENDÜSTRİYEL KİMYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "İNVENTA GIDA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "ERKAN DEMİRCAN": "SUAT ARI",
    "NUR ALUÇLUOĞLU - NUR TERZİ": "SUAT ARI",
    "YERLİYURT MARİN DENİZ ARAÇ KAB.TUR.SVE P.LTD.ŞTİ.": "SUAT ARI",
    "ÖZBAYRAK KIZAK KORUMA SİSTEMLERİ ENDÜSTRİ MAKİNE SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SUAT ARI"
}

PERSONEL_LISTESI = [
    "HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN",
    "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ",
    "SUAT ARI", "SERGEN GÖRÜROĞLU", "CELAL ŞENOL", "ATANMAMIŞ"
]

# ==========================================
# CSS VE TEMA KODLARI
# ==========================================
custom_css = """
<style>
    .notranslate {
        translate: no !important;
    }
    .stApp {
        background-color: #0B192C !important;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #1E3E62 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stSidebar"] div.stButton > button, div.stButton > button {
        width: 100% !important;
        height: 48px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #90E0EF !important;
        box-shadow: 0 6px 0 #03045E, 0 8px 10px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(0);
        transition: all 0.1s ease;
        margin-bottom: 10px !important;
        text-align: left !important;
        padding-left: 15px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover, div.stButton > button:hover {
        background: linear-gradient(135deg, #48CAE4 0%, #00B4D8 100%) !important;
        box-shadow: 0 4px 0 #03045E, 0 6px 8px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(2px);
    }
    [data-testid="stSidebar"] div.stButton > button:active, div.stButton > button:active {
        box-shadow: 0 0 0 #03045E, 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(6px);
    }

    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #FFD166 0%, #FFB703) !important;
        border: 2px dashed #FB8500 !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #000000 !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #FFB703 0%, #FB8500) !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 0 #9E2A2B, 0 6px 8px rgba(0,0,0,0.3) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# TÜRKÇE TEMİZLEME VE PARS FONKSİYONLARI
# ==========================================
def clean_string(text):
    if pd.isna(text) or not text:
        return ""
    text = str(text).upper().strip()
    replacements = {'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def parse_turkish_float(val):
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ['NAN', 'NONE', '-', '0', '0.0', '0,0']:
        return 0.0
    s = s.replace(' ', '').replace('₺', '').replace('TL', '')
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

# ==========================================
# GÜÇLÜ DOSYA OKUMA MOTORU
# ==========================================
def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    encodings = ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']
    separators = [';', ',', '\t', None]

    for enc in encodings:
        for sep in separators:
            try:
                engine_type = 'python' if sep is None else None
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, engine=engine_type, on_bad_lines='skip')
                if df is not None and len(df.columns) > 1 and len(df) > 0:
                    return df
            except Exception:
                continue

    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except Exception:
        pass

    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
    except Exception:
        pass

    for enc in ['utf-8', 'cp1254', 'latin1']:
        try:
            dfs = pd.read_html(io.BytesIO(file_bytes), encoding=enc)
            if dfs and len(dfs) > 0:
                return dfs[0]
        except Exception:
            continue

    raise Exception("Dosya yapısı çözümlenemedi.")

# ==========================================
# PERSONEL HESAP ALIMI EKRANI PARSER
# ==========================================
def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKİT" in row_str or "FT" in row_str or "ÖDEME" in row_str:
            header_idx = idx
            break
            
    if header_idx > 0:
        df.columns = df.iloc[header_idx].astype(str).str.strip()
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = df.columns.astype(str).str.strip()

    cols_to_drop = [c for c in df.columns if "AÇIKLAMA" in str(c).upper() or "ACIKLAMA" in str(c).upper()]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    p_col, ft_col, odeme_col = None, None, None

    for col in df.columns:
        c_upper = str(col).upper()
        if ("PERSONEL" in c_upper or "AD" in c_upper or "KURYE" in c_upper) and not p_col:
            p_col = col
        elif (("FT" in c_upper or "FATURA" in c_upper) and not ("AD" in c_upper or "ADET" in c_upper)) and not ft_col:
            ft_col = col
        elif ("ÖDEME" in c_upper or "ODEME" in c_upper) and not odeme_col:
            odeme_col = col

    cols_list = list(df.columns)
    if not p_col and len(cols_list) > 0: p_col = cols_list[0]
    if not ft_col and len(cols_list) > 1: ft_col = cols_list[1]
    if not odeme_col and len(cols_list) > 2: odeme_col = cols_list[2]

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p_name = str(row[p_col]).strip() if p_col else ""
        c_p_name = clean_string(raw_p_name)
        
        if not c_p_name or c_p_name in ["NAN", "NONE", "TOTAL", "TOPLAM", "GENELTOPLAM"]:
            continue
            
        ft_val = parse_turkish_float(row[ft_col]) if ft_col else 0.0
        odeme_val = parse_turkish_float(row[odeme_col]) if odeme_col else 0.0

        parsed_rows.append({
            "Raw_Name": raw_p_name,
            "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": ft_val,
            "Nakit Ödeme Tutarı Topl": odeme_val,
            "Banka/ATM": 0.0
        })

    temp_df = pd.DataFrame(parsed_rows)

    priority_list = [
        "HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN",
        "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ",
        "SUAT ARI", "SERGEN GÖRÜROĞLU", "CELAL ŞENOL"
    ]

    final_rows = []
    processed_clean_names = set()

    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched_row = None
        
        if not temp_df.empty:
            exact_match = temp_df[temp_df["Clean_Name"] == clean_fixed]
            if not exact_match.empty:
                matched_row = exact_match.iloc[0]
            else:
                contains_match = temp_df[temp_df["Clean_Name"].apply(lambda x: clean_fixed in x or x in clean_fixed)]
                if not contains_match.empty:
                    matched_row = contains_match.iloc[0]

        if matched_row is not None:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": float(matched_row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(matched_row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": 0.0,
            })
            processed_clean_names.add(matched_row["Clean_Name"])
        else:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": 0.0,
                "Nakit Ödeme Tutarı Topl": 0.0,
                "Banka/ATM": 0.0,
            })

    result_df = pd.DataFrame(final_rows)
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False
    result_df.reset_index(drop=True, inplace=True)
    result_df.index = range(1, len(result_df) + 1)

    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]

# ==========================================
# F4 ÖDEME LİSTESİ İŞLEME MOTORU
# ==========================================
def process_f4_payment_data(df):
    df.columns = df.columns.astype(str).str.strip()
    
    musteri_col, borc_col, aciklama_col = None, None, None
    for col in df.columns:
        c_upper = str(col).upper()
        if ("MÜŞTERİ" in c_upper or "MUSTERI" in c_upper or "FIRMA" in c_upper or "UNVAN" in c_upper) and not musteri_col:
            musteri_col = col
        elif ("BORÇ" in c_upper or "BORC" in c_upper or "BAKİYE" in c_upper or "BAKIYE" in c_upper or "TUTAR" in c_upper) and not borc_col:
            borc_col = col
        elif "AÇIKLAMA" in c_upper or "ACIKLAMA" in c_upper:
            aciklama_col = col

    cols_list = list(df.columns)
    if not musteri_col and len(cols_list) > 0: musteri_col = cols_list[0]
    if not borc_col and len(cols_list) > 1: borc_col = cols_list[1]
    if not aciklama_col and len(cols_list) > 2: aciklama_col = cols_list[2]

    processed_rows = []
    for _, row in df.iterrows():
        m_adi = str(row[aciklama_col]).strip() if aciklama_col and not pd.isna(row[aciklama_col]) else ""
        if not m_adi or m_adi.upper() in ["NAN", "NONE", "TOPLAM", "TOTAL"]:
            m_adi = str(row[musteri_col]).strip() if musteri_col else ""
            
        if not m_adi or m_adi.upper() in ["NAN", "NONE", "TOPLAM", "TOTAL"]:
            continue
            
        borc_val = parse_turkish_float(row[borc_col]) if borc_col else 0.0
        
        if borc_val == 0.0:
            continue

        assigned_personel = "ATANMAMIŞ"
        m_upper = m_adi.upper()
        m_clean = clean_string(m_adi)

        if m_upper in MUSTERI_PERSONEL_MAP:
            assigned_personel = MUSTERI_PERSONEL_MAP[m_upper]
        else:
            found = False
            for k, v in MUSTERI_PERSONEL_MAP.items():
                if clean_string(k) == m_clean:
                    assigned_personel = v
                    found = True
                    break
            
            if not found:
                for k, v in MUSTERI_PERSONEL_MAP.items():
                    k_clean = clean_string(k)
                    if k_clean and (k_clean in m_clean or m_clean in k_clean):
                        assigned_personel = v
                        break

        processed_rows.append({
            "Müşteri Adı": m_adi,
            "Fatura Borcu": borc_val,
            "Açıklama": "",
            "Personel": assigned_personel
        })

    res_df = pd.DataFrame(processed_rows)
    if not res_df.empty:
        res_df.reset_index(drop=True, inplace=True)
        res_df.index = range(1, len(res_df) + 1)
    return res_df

# ==========================================
# SIDEBAR VE GEZİNTİ MENÜSÜ
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="notranslate" style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; color: #FFFFFF;">Yurtiçi Kargo</h2>
        <h4 style="margin: 0; color: #F57C00;">Görükle Acente KOYS</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="notranslate" style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <small style="color: #F57C00;">Aktif Kullanıcı:</small><br>
        <strong>{KULLANICI_ISIM}</strong> ({KULLANICI_GOREV})
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=['csv', 'xlsx', 'xls', 'html'])
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📊 Ana Panel"):
        st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"
    if st.button("💰 HESAP"):
        st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"):
        st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# ==========================================
# AKILLI VERİ DAĞITIM VE İŞLEME MİMARİSİ
# ==========================================
if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        st.session_state.raw_df = raw_df
        
        cols_str = " ".join([str(c).upper() for c in raw_df.columns])
        if "AT ZIMMET" in cols_str or "TESLIM EDEN PERSONEL" in cols_str or "KARGO TESLIMAT KANALI" in cols_str:
            perf_res, _ = process_excel_data(raw_df)
            st.session_state.perf_df = perf_res
            
        elif "NAKIT" in cols_str or "FT" in cols_str or "ODEME" in cols_str or "BANKA" in cols_str or "PERSONEL" in cols_str:
            processed_acc = process_personnel_account_data(raw_df)
            st.session_state.account_df = processed_acc
            st.session_state.hesap_df = processed_acc.copy()
            
        if "MÜŞTERİ" in cols_str or "MUSTERI" in cols_str or "BORÇ" in cols_str or "BORC" in cols_str or "FATURA BORCU" in cols_str or "F4" in uploaded_file.name.upper():
            f4_res = process_f4_payment_data(raw_df)
            st.session_state.f4_df = f4_res
            
    except Exception as e:
        st.error(f"❌ Dosya Okuma/İşleme Hatası: {e}")

# ==========================================
# TAB 1: ANA PANEL
# ==========================================
if st.session_state.active_tab == "Ana Panel":
    st.title("📊 Görükle Acente - Genel Performans Özeti")
    
    perf_df = st.session_state.perf_df
    if perf_df is not None and not perf_df.empty:
        total_zimmet = perf_df["Zimmet"].sum()
        total_teslim = perf_df["Teslim Edilen"].sum()
        total_devir = perf_df["Teslim Edilemeyen"].sum()
        avg_rate = round((total_teslim / total_zimmet) * 100, 1) if total_zimmet > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 Toplam Zimmet", f"{total_zimmet:,}")
        c2.metric("✅ Teslim Edilen", f"{total_teslim:,}")
        c3.metric("🚨 Devir / Teslim Edilemeyen", f"{total_devir:,}")
        c4.metric("🎯 Genel Başarı Oranı", f"%{avg_rate}")
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Kurye Başarı Oranları (%)")
            fig_bar = px.bar(
                perf_df, 
                x="Personel", 
                y="Başarı Oranı", 
                color="Başarı Oranı",
                color_continuous_scale="RdYlGn",
                text="Başarı Oranı"
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("📲 Teslimat Kanalları Dağılımı")
            channel_totals = {
                "SMS": perf_df["SMS"].sum(),
                "İmza": perf_df["İmza"].sum(),
                "KS-PE": perf_df["KS-PE"].sum()
            }
            fig_pie = px.pie(
                names=list(channel_totals.keys()),
                values=list(channel_totals.values()),
                hole=0.5,
                color_discrete_sequence=['#0D6EFD', '#F57C00', '#2E7D32']
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Genel Performans Tablosu")
        st.dataframe(perf_df, use_container_width=True)
        
    else:
        st.info("💡 Sol menüden **AT ZİMMET İZLEME** dosyanızı yükleyerek ana paneli görüntüleyebilirsiniz.")

# ==========================================
# TAB 1: HESAP
# ==========================================
if st.session_state.active_tab == "HESAP":
    account_df = st.session_state.account_df

    if account_df is not None:
        current_df = st.session_state.hesap_df.copy()
        
        temp_hesap_toplam = 0.0
        for idx, row in current_df.iterrows():
            ft_val = float(row["Nakit Ft Tutarı Topl"])
            odeme_val = float(row["Nakit Ödeme Tutarı Topl"])
            curr_b = st.session_state.get(f"banka_{idx}", float(row["Banka/ATM"]))
            temp_hesap_toplam += (ft_val + odeme_val - curr_b)

        def update_kasa():
            st.session_state.kasa_miktari = st.session_state.ust_kasa_input

        top_col1, top_col2 = st.columns([2.5, 2.5])
        with top_col1:
            st.title("📋 Günlük Personel Hesap Takip Paneli")
        with top_col2:
            st.markdown("<div style='background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border: 2px solid #FFA200; border-radius: 12px; padding: 12px; margin-top: 5px; box-shadow: 0 4px 8px rgba(255, 123, 0, 0.3);'>", unsafe_allow_html=True)
            
            kasa_input_col1, kasa_input_col2 = st.columns(2)
            with kasa_input_col1:
                st.number_input(
                    "🏦 MANÜEL KASA GİR", 
                    value=float(st.session_state.kasa_miktari), 
                    step=100.0, 
                    format="%.2f", 
                    key="ust_kasa_input",
                    on_change=update_kasa
                )
            with kasa_input_col2:
                st.markdown(f"<div style='padding-top: 28px;'><span style='font-size: 13px; color: #FFFFFF;'>📊 Toplam: <strong>{temp_hesap_toplam:,.2f} ₺</strong></span></div>", unsafe_allow_html=True)
            
            GuncelKasa = float(st.session_state.ust_kasa_input if "ust_kasa_input" in st.session_state else st.session_state.kasa_miktari)
            
            if GuncelKasa > temp_hesap_toplam:
                durum_metni = f"🔴 AÇIK {abs(GuncelKasa - temp_hesap_toplam):,.2f} ₺"
                renk_kodu = "#FFE5D9"
            elif GuncelKasa < temp_hesap_toplam:
                durum_metni = f"🟢 FAZLA {abs(temp_hesap_toplam - GuncelKasa):,.2f} ₺"
                renk_kodu = "#D8F3DC"
            else:
                durum_metni = "✅ KASA TAM (0.00 ₺)"
                renk_kodu = "#FFFFFF"
            
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: bold; font-size: 15px; color: {renk_kodu};'>{durum_metni}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        updated_rows = []
        for idx, row in current_df.iterrows():
            p_name = row["Personel Adı"]
            ft_val = float(row["Nakit Ft Tutarı Topl"])
            odeme_val = float(row["Nakit Ödeme Tutarı Topl"])
            current_banka = float(row["Banka/ATM"])
            current_islem = bool(row["İşlem"])

            foto_url = get_github_avatar(p_name)
            fallback_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={p_name.replace(' ', '')}"

            bg_style = "background: rgba(46, 125, 50, 0.35); border: 1px solid #2E7D32;" if current_islem else "background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border: 1px solid #FFA200; box-shadow: 0 4px 8px rgba(255, 123, 0, 0.2);"
            
            st.markdown(f"""
            <div style="{bg_style} border-radius: 12px; padding: 12px 15px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <img src="{foto_url}" width="40" height="40" style="border-radius: 50%; object-fit: cover; border: 2px solid #00B4D8; background: #fff;" onerror="this.onerror=null; this.src='{fallback_url}';" />
                    <span style="font-weight: bold; font-size: 16px; color: #FFFFFF;">{p_name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1.5])
            with c1: st.metric("Nakit Ft Topl", f"{ft_val:,.2f} ₺")
            with c2: st.metric("Nakit Ödeme Topl", f"{odeme_val:,.2f} ₺")
            with c3: new_banka = st.number_input("Banka/ATM", value=current_banka, step=10.0, format="%.2f", key=f"banka_{idx}", label_visibility="collapsed")
            with c4: 
                hesap_sonuc = ft_val + odeme_val - new_banka
                st.metric("Hesap", f"{hesap_sonuc:,.2f} ₺")
            with c5: new_islem = st.checkbox("Tamam", value=current_islem, key=f"islem_{idx}")

            updated_rows.append({
                "Personel Adı": p_name, "Nakit Ft Tutarı Topl": ft_val, 
                "Nakit Ödeme Tutarı Topl": odeme_val, "Banka/ATM": new_banka, 
                "Hesap": hesap_sonuc, "İşlem": new_islem
            })
        st.session_state.hesap_df = pd.DataFrame(updated_rows)
    else:
        st.info("ℹ️ Lütfen sol panelden personel hesap raporunu yükleyin.")

# ==========================================
# TAB 2: F4 ÖDEME LİSTESİ
# ==========================================
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.markdown("### 📋 F4 Ödeme ve Kişisel Tahsilat Listesi")
    st.caption("Tablo üzerinden 'Sorumlu Personel' sütununa tıklayarak eksik veya atanmamış kişisel isimlerini manuel olarak yazabilir veya değiştirebilirsiniz.")
    
    f4_df = st.session_state.get('f4_df', None)
    
    if f4_df is not None and not f4_df.empty:
        if st.session_state.editable_f4_df is None:
            st.session_state.editable_f4_df = f4_df.copy()

        tum_personel_secenekleri = sorted(list(set(PERSONEL_LISTESI + list(st.session_state.editable_f4_df["Personel"].unique()))))
        
        edited_df = st.data_editor(
            st.session_state.editable_f4_df,
            column_config={
                "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺", disabled=True),
                "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                "Personel": st.column_config.SelectboxColumn(
                    "Sorumlu Personel (Düzenlenebilir)",
                    options=tum_personel_secenekleri,
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key="f4_editor"
        )
        
        st.session_state.editable_f4_df = edited_df

        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)

        st.markdown("🔍 **Sorumlu Personele Göre Süzgekleme:**")
        
        filtre_secenekleri = ["Tümü"] + sorted(list(edited_df["Personel"].unique()))
        secilen_filtre = st.selectbox("Personel Filtrele", options=filtre_secenekleri, label_visibility="collapsed")
        
        if secilen_filtre == "Tümü":
            filtrelenmis_df = edited_df.copy()
            gorunum_adi = f"Tümü (Toplam {len(filtrelenmis_df)} Kayıt)"
        else:
            filtrelenmis_df = edited_df[edited_df["Personel"] == secilen_filtre].copy()
            gorunum_adi = f"{secilen_filtre} - Müşteri Ödeme Listesi (Toplam {len(filtrelenmis_df)} Kayıt)"

        st.markdown(f"📌 **Seçilen Görünüm:** {gorunum_adi}")
        
        if not filtrelenmis_df.empty:
            st.markdown(f"Toplam Borç: **{filtrelenmis_df['Fatura Borcu'].sum():,.2f} ₺**")
            st.dataframe(filtrelenmis_df[["Müşteri Adı", "Fatura Borcu", "Açıklama", "Personel"]], use_container_width=True, hide_index=True)
            
            html_icerik = f"""
            <html>
            <head>
                <title>{secilen_filtre} - F4 Ödeme Listesi</title>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #000; padding: 20px; }}
                    h2 {{ text-align: center; color: #333; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; font-size: 14px; }}
                    th {{ background-color: #f2f2f2; }}
                    .total {{ font-weight: bold; margin-top: 15px; font-size: 16px; text-align: right; }}
                </style>
            </head>
            <body>
                <h2>Görükle Acente - F4 Ödeme Listesi</h2>
                <p><strong>Filtre / Sorumlu:</strong> {secilen_filtre}</p>
                <p><strong>Tarih:</strong> {pd.Timestamp.now().strftime('%d.%m.%Y')}</p>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Müşteri Adı</th>
                            <th>Fatura Borcu (₺)</th>
                            <th>Açıklama</th>
                            <th>Personel</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for row_idx, row in enumerate(filtrelenmis_df.itertuples(), 1):
                html_icerik += f"""
                        <tr>
                            <td>{row_idx}</td>
                            <td>{row.Müşteri_Adı}</td>
                            <td style="text-align: right;">{row.Fatura_Borcu:,.2f} ₺</td>
                            <td>{row.Açıklama}</td>
                            <td>{row.Personel}</td>
                        </tr>
                """
            
            toplam_tutar = filtrelenmis_df['Fatura Borcu'].sum()
            html_icerik += f"""
                    </tbody>
                </table>
                <div class="total">Toplam Borç: {toplam_tutar:,.2f} ₺</div>
                <script>window.print();</script>
            </body>
            </html>
            """
            
            encoded_html = urllib.parse.quote(html_icerik)
            data_url = f"data:text/html;charset=utf-8,{encoded_html}"
            
            col_p1, _ = st.columns([1, 4])
            with col_p1:
                st.markdown(f"""
                    <a href="{data_url}" target="_blank" style="text-decoration: none;">
                        <button style="width: 100%; height: 40px; background-color: #00B4D8; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                            🖨️ PDF / Yazdır
                        </button>
                    </a>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Bu filtreye uygun herhangi bir kayıt bulunamadı.")
    else:
        st.info("ℹ️ Lütfen sol panelden F4 Ödeme / Müşteri Borç listesini içeren dosyayı yükleyin.")

import streamlit as st
import pandas as pd
import io
import re
import urllib.parse

# PDF Oluşturma Kütüphanesi (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Görükle Acente - F4/HESAP",
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

KULLANICI_ISIM = "CELAL ŞENOL"
KULLANICI_GOREV = "(Şube Şefi)"

# ==========================================
# GİTHUB PERSONEL FOTOĞRAF HARİTASI ('HESAPP')
# ==========================================
GITHUB_USER = "cllsenoll"
GITHUB_REPO = "HESAPP"
GITHUB_BRANCH = "main"

def get_github_avatar(personel_adi):
    if not personel_adi:
        return ""
    
    tr_map = {'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'}
    clean_name = str(personel_adi).strip()
    for k, v in tr_map.items():
        clean_name = clean_name.replace(k, v)
    clean_name = clean_name.upper()
    
    encoded_name = urllib.parse.quote(clean_name)
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{encoded_name}.png"

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
    "S.S.MARMARA ZEYTİN TARIM SAT.KOOP.BİR.MARMARABİRKİK": "BURCU DÜREN",
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

# ==========================================
# ÖZEL CSS VE MAVİ-TURUNCU TEMA STİLLERİ
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
        background: linear-gradient(135deg, #00B4D8 0%, #FF8500 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #FFB703 !important;
        box-shadow: 0 6px 0 #03045E, 0 8px 10px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(0);
        transition: all 0.1s ease;
        margin-bottom: 10px !important;
        text-align: left !important;
        padding-left: 15px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover, div.stButton > button:hover {
        background: linear-gradient(135deg, #48CAE4 0%, #FB8500 100%) !important;
        box-shadow: 0 4px 0 #03045E, 0 6px 8px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(2px);
    }

    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #FFD166 0%, #FFB703) !important;
        border: 2px dashed #FB8500 !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #000000 !important;
    }
    
    .avatar-card {
        position: relative;
        background: linear-gradient(145deg, #162B48 0%, #1E3E62 100%);
        border: 2px solid #FF8500;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(255, 133, 0, 0.15);
        margin-bottom: 18px;
        transition: transform 0.2s ease;
    }
    .avatar-card-completed {
        position: relative;
        background: linear-gradient(145deg, #133824 0%, #1B4D33 100%);
        border: 2px solid #00FF66;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0, 255, 102, 0.2);
        margin-bottom: 18px;
        transition: transform 0.2s ease;
    }
    .avatar-img {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #00B4D8;
        margin-bottom: 8px;
        background-color: #0B192C;
    }
    .avatar-img-completed {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #00FF66;
        margin-bottom: 8px;
        background-color: #0B192C;
    }
    .personel-isim {
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 6px;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }
    .personel-hesap {
        color: #FFB703;
        font-size: 19px;
        font-weight: 800;
        margin-bottom: 6px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .personel-hesap-completed {
        color: #00FF66;
        font-size: 19px;
        font-weight: 800;
        margin-bottom: 6px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .modern-table-container {
        background: #132238;
        border: 1px solid #1E3E62;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
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

def tr_fix(text):
    if not text:
        return ""
    mapping = {
        'İ': 'I', 'ı': 'i',
        'Ş': 'S', 'ş': 's',
        'Ğ': 'G', 'ğ': 'g',
        'Ü': 'U', 'ü': 'u',
        'Ö': 'O', 'ö': 'o',
        'Ç': 'C', 'ç': 'c'
    }
    for k, v in mapping.items():
        text = str(text).replace(k, v)
    return text

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
        
        if not raw_p_name or raw_p_name.upper() in ["NAN", "NONE", "-", "TOTAL", "TOPLAM", "GENELTOPLAM"]:
            continue
            
        ft_val = parse_turkish_float(row[ft_col]) if ft_col else 0.0
        odeme_val = parse_turkish_float(row[odeme_col]) if odeme_col else 0.0

        parsed_rows.append({
            "Personel Adı": raw_p_name,
            "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": ft_val,
            "Nakit Ödeme Tutarı Topl": odeme_val,
            "Banka/ATM": 0.0
        })

    temp_df = pd.DataFrame(parsed_rows)

    final_rows = []
    seen_names = set()
    
    if not temp_df.empty:
        for _, row in temp_df.iterrows():
            p_name = row["Personel Adı"]
            c_name = row["Clean_Name"]
            if c_name not in seen_names:
                seen_names.add(c_name)
                final_rows.append({
                    "Personel Adı": p_name,
                    "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                    "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                    "Banka/ATM": 0.0,
                })

    result_df = pd.DataFrame(final_rows)
    if not result_df.empty:
        result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
        result_df["İşlem"] = False
        result_df.reset_index(drop=True, inplace=True)
    
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
# HESAP ÖZETİ PDF OLUŞTURMA MOTORU
# ==========================================
def generate_hesap_pdf(df_hesap, kasa_miktari):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0B192C"),
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E3E62"),
        alignment=1
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#111111"),
        alignment=0
    )

    table_body_num_style = ParagraphStyle(
        'TableBodyNum',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#111111"),
        alignment=2
    )

    elements = []

    elements.append(Paragraph(tr_fix("YURTICI KARGO GORUKLE ACENTESI"), title_style))
    elements.append(Paragraph(tr_fix("GUNLUK PERSONEL HESAP VE KASA TAKIP RAPORU"), subtitle_style))
    elements.append(Spacer(1, 15))

    table_data = [
        [
            Paragraph(tr_fix("S.No"), table_header_style),
            Paragraph(tr_fix("Personel Adi"), table_header_style),
            Paragraph(tr_fix("Nakit FT (TL)"), table_header_style),
            Paragraph(tr_fix("Nakit Odeme (TL)"), table_header_style),
            Paragraph(tr_fix("Banka/ATM (TL)"), table_header_style),
            Paragraph(tr_fix("Hesap Tutar (TL)"), table_header_style)
        ]
    ]

    total_ft = 0.0
    total_odeme = 0.0
    total_banka = 0.0
    total_hesap = 0.0

    for idx, (_, row) in enumerate(df_hesap.iterrows(), 1):
        ft = float(row["Nakit Ft Tutarı Topl"])
        odeme = float(row["Nakit Ödeme Tutarı Topl"])
        banka = float(row["Banka/ATM"])
        hesap = float(row["Hesap"])

        total_ft += ft
        total_odeme += odeme
        total_banka += banka
        total_hesap += hesap

        table_data.append([
            Paragraph(tr_fix(str(idx)), table_body_style),
            Paragraph(tr_fix(str(row["Personel Adı"])), table_body_style),
            Paragraph(f"{ft:,.2f}", table_body_num_style),
            Paragraph(f"{odeme:,.2f}", table_body_num_style),
            Paragraph(f"{banka:,.2f}", table_body_num_style),
            Paragraph(f"{hesap:,.2f}", table_body_num_style)
        ])

    table_data.append([
        Paragraph("<b>TOPLAM</b>", table_body_style),
        Paragraph("", table_body_style),
        Paragraph(f"<b>{total_ft:,.2f}</b>", table_body_num_style),
        Paragraph(f"<b>{total_odeme:,.2f}</b>", table_body_num_style),
        Paragraph(f"<b>{total_banka:,.2f}</b>", table_body_num_style),
        Paragraph(f"<b>{total_hesap:,.2f}</b>", table_body_num_style)
    ])

    col_widths = [35, 175, 75, 75, 75, 80]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3E62")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor("#F1F3F5")]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E9ECEF")),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#1E3E62")),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 15))

    fark = float(kasa_miktari) - total_hesap
    if fark > 0:
        durum_str = f"ACIK: {abs(fark):,.2f} TL"
    elif fark < 0:
        durum_str = f"FAZLA: {abs(fark):,.2f} TL"
    else:
        durum_str = "KASA TAM (0.00 TL)"

    ozet_data = [
        [Paragraph(tr_fix(f"<b>Kasa Miktari:</b> {float(kasa_miktari):,.2f} TL"), table_body_style),
         Paragraph(tr_fix(f"<b>Toplam Hesap:</b> {total_hesap:,.2f} TL"), table_body_style),
         Paragraph(tr_fix(f"<b>Durum:</b> {durum_str}"), table_body_style)]
    ]
    ozet_table = Table(ozet_data, colWidths=[175, 175, 165])
    ozet_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3E62")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(ozet_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# SIDEBAR VE GEZİNTİ MENÜSÜ
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="notranslate" style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; color: #FFFFFF;">F4 / HESAP</h2>
        <h4 style="margin: 0; color: #FFB703;">Görükle Acente</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="notranslate" style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <small style="color: #FFB703;">Aktif Kullanıcı:</small><br>
        <strong>{KULLANICI_ISIM}</strong> {KULLANICI_GOREV}
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=['csv', 'xlsx', 'xls', 'html'])
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
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
        
        if "NAKIT" in cols_str or "PERSONEL" in cols_str or "FT" in cols_str or "ODEME" in cols_str:
            st.session_state.hesap_df = process_personnel_account_data(raw_df)
        else:
            st.session_state.f4_df = process_f4_payment_data(raw_df)
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")

# ==========================================
# ANA EKRAN / HESAP TABI GÖSTERİMİ
# ==========================================
if st.session_state.active_tab == "HESAP":
    st.title("💰 Günlük Personel Hesap ve Kasa Takibi")
    
    if st.session_state.hesap_df is not None:
        df_hesap = st.session_state.hesap_df
        
        st.subheader("Personel Durum Kartları")
        
        if "İşlem" not in df_hesap.columns:
            df_hesap["İşlem"] = False

        cols = st.columns(4)
        
        for i, (idx_row, row) in enumerate(df_hesap.iterrows()):
            p_name = row["Personel Adı"]
            avatar_url = get_github_avatar(p_name)
            current_islem = bool(row["İşlem"])
            
            with cols[i % len(cols)]:
                new_islem_val = st.checkbox(
                    "İşlem Tamam", 
                    value=current_islem, 
                    key=f"chk_card_{idx_row}_{p_name}"
                )
                df_hesap.at[idx_row, "İşlem"] = new_islem_val
                
                if new_islem_val:
                    card_class = "avatar-card-completed"
                    img_class = "avatar-img-completed"
                    hesap_class = "personel-hesap-completed"
                    status_badge = '<span style="color: #00FF66; font-size: 13px; font-weight: bold;">✔ Tamamlandı</span>'
                else:
                    card_class = "avatar-card"
                    img_class = "avatar-img"
                    hesap_class = "personel-hesap"
                    status_badge = '<span style="color: #FF8500; font-size: 13px; font-weight: bold;">⏳ Bekliyor</span>'

                st.markdown(f"""
                <div class="{card_class}">
                    <img src="{avatar_url}" class="{img_class}" onerror="this.onerror=null;this.src='https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/DEFAULT.png';">
                    <div class="personel-isim">{p_name}</div>
                    <div class="{hesap_class}">{row['Hesap']:,.2f} TL</div>
                    <div>{status_badge}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Personel Hesap Detay Tablosu (Banka/ATM Girişi & Düzenleme)")
        
        st.info("💡 **Banka/ATM** sütununa personelin banka ya da ATM üzerinden yatırdığı tutarları yazabilirsiniz. **Hesap** tutarı anlık olarak güncellenecektir.")

        # Tablo gösterilmeden önce mevcut değerler üzerinden hesaplamayı garanti et
        df_hesap["Hesap"] = df_hesap["Nakit Ft Tutarı Topl"] + df_hesap["Nakit Ödeme Tutarı Topl"] - df_hesap["Banka/ATM"]

        edited_df = st.data_editor(
            df_hesap,
            column_config={
                "Personel Adı": st.column_config.TextColumn("Personel Adı", disabled=True),
                "Nakit Ft Tutarı Topl": st.column_config.NumberColumn("Nakit Ft Tutarı Topl", format="%.2f TL", disabled=True),
                "Nakit Ödeme Tutarı Topl": st.column_config.NumberColumn("Nakit Ödeme Tutarı Topl", format="%.2f TL", disabled=True),
                "Banka/ATM": st.column_config.NumberColumn("Banka/ATM (Düzenlenebilir)", format="%.2f TL", min_value=0.0, step=1.0),
                "Hesap": st.column_config.NumberColumn("Hesap (Otomatik)", format="%.2f TL", disabled=True),
                "İşlem": st.column_config.CheckboxColumn("İşlem Tamam", default=False)
            },
            hide_index=True,
            use_container_width=True,
            key="account_data_editor"
        )

        # st.data_editor döndükten sonra anlık güncellemeyi yakalamak ve Hesap sütununu yeniden hesaplamak için:
        edited_df["Hesap"] = edited_df["Nakit Ft Tutarı Topl"] + edited_df["Nakit Ödeme Tutarı Topl"] - edited_df["Banka/ATM"]
        st.session_state.hesap_df = edited_df

        st.markdown("---")
        st.subheader("Kasa Kontrol ve Raporlama")
        
        col_kasa1, col_kasa2 = st.columns([1, 1])
        with col_kasa1:
            st.session_state.kasa_miktari = st.number_input(
                "Fiziki Kasa Miktarı (TL)", 
                min_value=0.0, 
                value=float(st.session_state.kasa_miktari), 
                step=10.0,
                format="%.2f"
            )
            
        toplam_hesap_tutar = edited_df["Hesap"].sum()
        kasa_farki = float(st.session_state.kasa_miktari) - toplam_hesap_tutar

        with col_kasa2:
            st.markdown(f"""
            <div class="modern-table-container">
                <h4 style="margin-top:0; color: #00B4D8;">Özet Bilgiler</h4>
                <p><b>Toplam Hesap:</b> {toplam_hesap_tutar:,.2f} TL</p>
                <p><b>Girilen Kasa:</b> {float(st.session_state.kasa_miktari):,.2f} TL</p>
            """, unsafe_allow_html=True)
            
            if kasa_farki > 0:
                st.markdown(f'<p style="color: #00FF66; font-weight: bold; font-size: 16px;">Kasa Fazlası: {abs(kasa_farki):,.2f} TL</p>', unsafe_allow_html=True)
            elif kasa_farki < 0:
                st.markdown(f'<p style="color: #FF4B4B; font-weight: bold; font-size: 16px;">Kasa Açığı: {abs(kasa_farki):,.2f} TL</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #00FF66; font-weight: bold; font-size: 16px;">Kasa Tam Matrah (0.00 TL)</p>', unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

        pdf_bytes = generate_hesap_pdf(edited_df, st.session_state.kasa_miktari)
        st.download_button(
            label="📄 Günlük Hesap Özetini PDF İndir",
            data=pdf_bytes,
            file_name="Gorusle_Acente_Gunluk_Hesap_Raporu.pdf",
            mime="application/pdf"
        )
    else:
        st.info("👈 Lütfen sol menüden ilgili rapor/liste dosyasını yükleyin.")

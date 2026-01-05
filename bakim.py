import streamlit as st
import pandas as pd
import datetime
import os

# 1. KURUMSAL KİMLİK AYARLARI (SEKME BAŞLIĞI)
st.set_page_config(
    page_title="Maintor | Dijital Bakım Sistemi", 
    page_icon="⚙️", 
    layout="wide"
)

# 2. VERİ DOSYASI YÖNETİMİ
DATA_FILE = "maintor_veritabani.csv"

def verileri_yukle():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE).to_dict('records')
    return []

def verileri_kaydet(liste):
    pd.DataFrame(liste).to_csv(DATA_FILE, index=False)

if 'is_emirleri' not in st.session_state:
    st.session_state.is_emirleri = verileri_yukle()

# 3. GÜVENLİK (MAINTOR GİRİŞ PANELİ)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_ekrani():
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #007BFF;'>🚀 MAINTOR</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>Akıllı Fabrika Yönetim Sistemi</h4>", unsafe_allow_html=True)
        st.write("---")
        kullanici = st.text_input("Yönetici Kimliği")
        sifre = st.text_input("Giriş Şifresi", type="password")
        if st.button("SİSTEME GİRİŞ YAP", use_container_width=True):
            # Şifreyi buradan istediğin gibi güncelle
            if kullanici == "admin" and sifre == "maintor2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Giriş başarısız! Lütfen bilgilerinizi kontrol edin.")

# 4. ANA PROGRAM PANELİ
if not st.session_state.authenticated:
    login_ekrani()
else:
    # Sol Menü (SideBar)
    st.sidebar.markdown("<h2 style='color: #007BFF;'>⚙️ MAINTOR</h2>", unsafe_allow_html=True)
    st.sidebar.write(f"**Yetkili:** Admin")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "YÖNETİM MENÜSÜ", 
        ["📊 Dashboard", "🔧 Yeni Arıza Bildirimi", "📂 Bakım Kayıtları"]
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.authenticated = False
        st.rerun()

    # MODÜL 1: DASHBOARD (ÖZET EKRANI)
    if menu == "📊 Dashboard":
        st.title("📈 Maintor Analiz Paneli")
        if st.session_state.is_emirleri:
            df = pd.DataFrame(st.session_state.is_emirleri)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam İş Emri", len(df))
            m2.metric("Toplam Bakım Gideri", f"{df['Maliyet'].sum()} ₺")
            m3.metric("Aktif Arızalar", len(df[df['Durum'] == 'Açık']))
            
            st.divider()
            st.subheader("Makine Arıza Yoğunluğu")
            st.bar_chart(df['Makine'].value_counts())
        else:
            st.info("Sistemde henüz kayıtlı veri bulunmuyor. Lütfen yeni arıza bildirimi yapın.")

    # MODÜL 2: YENİ KAYIT
    elif menu == "🔧 Yeni Arıza Bildirimi":
        st.title("📝 Yeni Kayıt Oluştur")
        with st.form("maintor_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                makine = st.selectbox("Arızalı Makine / Hat", ["Pres-01", "CNC-Yatay", "Robot Kol-A", "Paketleme Hattı", "Kompresör"])
                oncelik = st.selectbox("Kritiklik Seviyesi", ["Düşük", "Normal", "Yüksek", "⚠️ ACİL"])
            with col_b:
                maliyet = st.number_input("Tahmini Onarım Maliyeti (₺)", min_value=0)
                durum = st.selectbox("İş Emri Durumu", ["Açık", "Beklemede", "Tamamlandı"])
            
            detay = st.text_area("Arıza Detayı ve Yapılan İşlem")
            
            if st.form_submit_button("KAYDI TAMAMLA"):
                yeni_kayit = {
                    "Tarih": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Makine": makine,
                    "Oncelik": oncelik,
                    "Maliyet": maliyet,
                    "Detay": detay,
                    "Durum": durum
                }
                st.session_state.is_emirleri.append(yeni_kayit)
                verileri_kaydet(

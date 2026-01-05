import streamlit as st
import pandas as pd
import datetime
import os

# 1. SAYFA VE MARKA AYARLARI (MAINTOR)
st.set_page_config(page_title="Maintor | Akıllı Bakım", page_icon="🛠️", layout="wide")

# 2. VERİ TABANI SİSTEMİ (Excel Dosyası)
DATA_FILE = "maintor_verileri.csv"

def verileri_yukle():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE).to_dict('records')
    return []

def verileri_kaydet(liste):
    pd.DataFrame(liste).to_csv(DATA_FILE, index=False)

# Hafızayı kontrol et
if 'is_emirleri' not in st.session_state:
    st.session_state.is_emirleri = verileri_yukle()

# 3. GÜVENLİK (GİRİŞ EKRANI)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_ekrani():
    st.container()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🚀 MAINTOR")
        st.subheader("Dijital Bakım Yönetim Paneli")
        kullanici = st.text_input("Yönetici Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş"):
            if kullanici == "admin" and sifre == "maintor2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

# 4. ANA PROGRAM (EĞER GİRİŞ YAPILDIYSA)
if not st.session_state.authenticated:
    login_ekrani()
else:
    # Sol Menü
    st.sidebar.title("🛠️ MAINTOR v1.0")
    st.sidebar.write(f"Kullanıcı: Admin")
    menu = st.sidebar.radio("Menü", ["📊 Genel Durum", "➕ Yeni Arıza Kaydı", "📋 Arıza Listesi"])
    
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.authenticated = False
        st.rerun()

    # MODÜL 1: DASHBOARD
    if menu == "📊 Genel Durum":
        st.title("Fabrika Genel Analizi")
        if st.session_state.is_emirleri:
            df = pd.DataFrame(st.session_state.is_emirleri)
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam İş Emri", len(df))
            c2.metric("Toplam Bakım Maliyeti", f"{df['Maliyet'].sum()} TL")
            c3.metric("Aktif Arıza", len(df[df['Durum'] == 'Açık']))
            st.divider()
            st.write("### Makine Bazlı Arıza Dağılımı")
            st.bar_chart(df['Makine'].value_counts())
        else:
            st.info("Henüz veri girişi yapılmadı.")

    # MODÜL 2: YENİ KAYIT
    elif menu == "➕ Yeni Arıza Kaydı":
        st.title("Yeni Arıza Bildirimi")
        with st.form("yeni_kayit_formu"):
            makine = st.selectbox("Makine Seçin", ["Pres 01", "CNC 02", "Robot 03", "Konveyör A"])
            oncelik = st.select_slider("Kritiklik", ["Düşük", "Normal", "Yüksek", "ACİL"])
            maliyet = st.number_input("Tahmini Maliyet (TL)", min_value=0)
            detay = st.text_area("Arıza Açıklaması")
            
            if st.form_submit_button("Sisteme Kaydet"):
                yeni = {
                    "Tarih": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                    "Makine": makine,
                    "Oncelik": oncelik,
                    "Maliyet": maliyet,
                    "Detay": detay,
                    "Durum": "Açık"
                }
                st.session_state.is_emirleri.append(yeni)
                verileri_kaydet(st.session_state.is_emirleri)
                st.success("Arıza başarıyla Maintor'a kaydedildi!")

    # MODÜL 3: LİSTELEME
    elif menu == "📋 Arıza Listesi":
        st.title("Tüm Kayıtlar")
        if st.session_state.is_emirleri:
            df = pd.DataFrame(st.session_state.is_emirleri)
            st.dataframe(df, use_container_width=True)
            if st.button("Listeyi Sıfırla (Dikkat!)"):
                st.session_state.is_emirleri = []
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.rerun()
        else:
            st.write("Gösterilecek veri yok.")

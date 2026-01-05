import streamlit as st
import pandas as pd
import datetime
import os

# --- AYARLAR ---
DATA_FILE = "bakim_verileri_v3.csv"
st.set_page_config(page_title="ProBakim CMMS", layout="wide")

# Veri Yükleme Fonksiyonu
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Tarih", "Makine", "Oncelik", "Detay", "Durum", "Maliyet"])

# --- ARAYÜZ ---
st.title("🛡️ ProBakim | Bakım & Maliyet Yönetimi")

menu = st.sidebar.selectbox("Menü", ["📊 Dashboard", "➕ Arıza Bildir", "⚙️ Ayarlar"])

df = load_data()

if menu == "📊 Dashboard":
    st.subheader("Fabrika Genel Analizi")
    
    if not df.empty:
        # Özet Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam İş Emri", len(df))
        c2.metric("Toplam Bakım Maliyeti", f"{df['Maliyet'].sum()} TL")
        c3.metric("En Çok Arıza Yapan", df['Makine'].value_counts().idxmax())
        
        # Grafik Hatasını Gidermiş Hali (Bar Chart her sürümde çalışır)
        st.write("### Makine Bazlı Arıza Dağılımı")
        st.bar_chart(df['Makine'].value_counts())
        
        st.write("### Tüm Kayıtlar")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz veri girişi yapılmadı.")

elif menu == "➕ Arıza Bildir":
    st.subheader("Yeni İş Emri ve Maliyet Girişi")
    
    with st.form("ariza_form"):
        col1, col2 = st.columns(2)
        makine = col1.selectbox("Makine", ["Pres 01", "CNC 02", "Robot 03", "Fırın 04"])
        maliyet = col2.number_input("Tahmini Tamir/Parça Maliyeti (TL)", min_value=0)
        oncelik = st.select_slider("Öncelik", ["Düşük", "Normal", "Acil", "KRİTİK"])
        detay = st.text_area("Arıza Tanımı")
        
        if st.form_submit_button("Sisteme Kaydet"):
            yeni_satir = pd.DataFrame([{
                "Tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Makine": makine,
                "Oncelik": oncelik,
                "Detay": detay,
                "Durum": "Açık",
                "Maliyet": maliyet
            }])
            df = pd.concat([df, yeni_satir], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Kayıt Başarıyla Eklendi!")
            st.rerun()

elif menu == "⚙️ Ayarlar":
    st.subheader("Sistem Ayarları")
    if st.button("Tüm Verileri Sıfırla"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.warning("Tüm veriler silindi!")
            st.rerun()
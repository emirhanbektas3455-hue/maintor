import streamlit as st
import pandas as pd
import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Maintor PRO | Bakım Yönetimi", layout="wide")

# --- VERİ DOSYALARI ---
DATA_FILE = "maintor_data.csv"
USER_FILE = "maintor_users.csv"

# --- YARDIMCI FONKSİYONLAR ---
def load_data(file, default_cols):
    if os.path.exists(file):
        return pd.read_csv(file).to_dict('records')
    return []

def save_data(file, data):
    pd.DataFrame(data).to_csv(file, index=False)

# --- VERİLERİ YÜKLE ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data(DATA_FILE, [])
if 'users' not in st.session_state:
    # Varsayılan Admin hesabı
    users = load_data(USER_FILE, [])
    if not users:
        users = [{"user": "admin", "pass": "123", "role": "Admin"}]
    st.session_state.users = users

# --- GİRİŞ SİSTEMİ ---
if "auth" not in st.session_state:
    st.session_state.auth = None

def login():
    st.title("🚀 MAINTOR PRO")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        user_match = next((x for x in st.session_state.users if x['user'] == u and x['pass'] == p), None)
        if user_match:
            st.session_state.auth = user_match
            st.rerun()
        else:
            st.error("Hatalı bilgiler!")

if not st.session_state.auth:
    login()
else:
    role = st.session_state.auth['role']
    name = st.session_state.auth['user']
    
    st.sidebar.title(f"Maintor {role}")
    st.sidebar.write(f"Hoş geldin: {name}")
    
    # --- MENÜLER ---
    if role == "Admin":
        menu = st.sidebar.radio("Menü", ["📊 Dashboard", "👥 Kullanıcı Yönetimi", "📋 Tüm Kayıtlar"])
    elif role == "Bakımcı":
        menu = st.sidebar.radio("Menü", ["🔧 Üzerimdeki İşler", "📂 Geçmiş İşlerim"])
    else: # Operatör
        menu = st.sidebar.radio("Menü", ["⚠️ Arıza Bildir", "🕒 Taleplerim"])

    if st.sidebar.button("Çıkış"):
        st.session_state.auth = None
        st.rerun()

    # --- OPERATÖR: ARIZA BİLDİR ---
    if menu == "⚠️ Arıza Bildir":
        st.header("Yeni Arıza Bildirimi")
        with st.form("op_form"):
            makine = st.selectbox("Makine", ["Pres 01", "CNC 02", "Robot A", "Konveyör B"])
            arıza = st.text_area("Arıza Nedir?")
            if st.form_submit_button("Kaydı Aç"):
                new_task = {
                    "id": len(st.session_state.tasks) + 1,
                    "tarih": datetime.datetime.now().strftime("%d/%m %H:%M"),
                    "makine": makine, "arıza": arıza, "op": name,
                    "durum": "Açık", "bakımcı": "", "islem": "", "parca": "", "maliyet": 0
                }
                st.session_state.tasks.append(new_task)
                save_data(DATA_FILE, st.session_state.tasks)
                st.success("Arıza bildirildi, bakım ekibine iletildi!")

    # --- BAKIMCI: İŞLEME GİRİŞ VE BİTİRME ---
    elif menu == "🔧 Üzerimdeki İşler":
        st.header("Açık Arızalar")
        acik_isler = [t for t in st.session_state.tasks if t['durum'] == "Açık"]
        if not acik_isler:
            st.info("Şu an açık arıza yok.")
        for t in acik_isler:
            with st.expander(f"İŞ #{t['id']} - {t['makine']} ({t['tarih']})"):
                st.write(f"**Arıza:** {t['arıza']}")
                with st.form(f"form_{t['id']}"):
                    islem = st.text_area("Yapılan İşlem")
                    parca_var = st.checkbox("Yedek parça kullandım")
                    parca_detay = st.text_input("Kullanılan Parça (Kullanmadıysanız boş bırakın)")
                    maliyet = st.number_input("Parça Maliyeti (TL)", min_value=0)
                    if st.form_submit_button("Arızayı Kapat"):
                        t['durum'] = "Tamamlandı"
                        t['bakımcı'] = name
                        t['islem'] = islem
                        t['parca'] = parca_detay if parca_var else "Kullanılmadı"
                        t['maliyet'] = maliyet
                        save_data(DATA_FILE, st.session_state.tasks)
                        st.success("İş başarıyla kapatıldı!")
                        st.rerun()

    # --- ADMIN: KULLANICI YÖNETİMİ ---
    elif menu == "👥 Kullanıcı Yönetimi":
        st.header("Sistem Kullanıcıları")
        st.table(pd.DataFrame(st.session_state.users))
        with st.form("yeni_user"):
            new_u = st.text_input("Yeni Kullanıcı Adı")
            new_p = st.text_input("Şifre")
            new_r = st.selectbox("Rol", ["Operatör", "Bakımcı", "Admin"])
            if st.form_submit_button("Kullanıcı Ekle"):
                st.session_state.users.append({"user": new_u, "pass": new_p, "role": new_r})
                save_data(USER_FILE, st.session_state.users)
                st.success("Kullanıcı eklendi!")
                st.rerun()

    # --- ADMIN: DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.header("Genel Durum Analizi")
        if st.session_state.tasks:
            df = pd.DataFrame(st.session_state.tasks)
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Arıza", len(df))
            c2.metric("Tamamlanan", len(df[df['durum']=="Tamamlandı"]))
            c3.metric("Toplam Maliyet", f"{df['maliyet'].sum()} TL")
            st.bar_chart(df['makine'].value_counts())
        else:
            st.write("Veri yok.")

    elif menu == "📋 Tüm Kayıtlar":
        st.header("Arıza Arşivi")
        st.dataframe(pd.DataFrame(st.session_state.tasks))

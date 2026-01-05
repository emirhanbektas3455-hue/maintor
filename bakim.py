import streamlit as st
import pandas as pd
import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Maintor PRO | Kurumsal Bakım Yönetimi", layout="wide", page_icon="⚙️")

# --- VERİ DOSYALARI ---
DATA_FILE = "maintor_data.csv"
USER_FILE = "maintor_users.csv"
MACHINE_FILE = "maintor_machines.csv"

# --- YARDIMCI FONKSİYONLAR ---
def load_data(file, default_data):
    if os.path.exists(file):
        return pd.read_csv(file).to_dict('records')
    return default_data

def save_data(file, data):
    pd.DataFrame(data).to_csv(file, index=False)

# --- VERİLERİ YÜKLE ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data(DATA_FILE, [])
if 'users' not in st.session_state:
    st.session_state.users = load_data(USER_FILE, [{"user": "admin", "pass": "123", "role": "Admin"}])
if 'machines' not in st.session_state:
    st.session_state.machines = load_data(MACHINE_FILE, [{"name": "Pres 01"}, {"name": "CNC 02"}])

# --- GİRİŞ SİSTEMİ ---
if "auth" not in st.session_state:
    st.session_state.auth = None

if not st.session_state.auth:
    st.title("🚀 MAINTOR PRO")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        user_match = next((x for x in st.session_state.users if x['user'] == u and str(x['pass']) == p), None)
        if user_match:
            st.session_state.auth = user_match
            st.rerun()
        else:
            st.error("Hatalı kullanıcı bilgileri!")
else:
    role = st.session_state.auth['role']
    name = st.session_state.auth['user']
    st.sidebar.title(f"Maintor {role}")
    st.sidebar.write(f"Kullanıcı: {name}")

    # --- MENÜ YÖNETİMİ ---
    if role == "Admin":
        menu = st.sidebar.radio("Yönetim", ["📊 Dashboard", "🏭 Makine Yönetimi", "👥 Kullanıcılar", "📋 Tüm Kayıtlar"])
    elif role == "Bakımcı":
        menu = st.sidebar.radio("Bakım Paneli", ["🔧 Açık Arızalar", "📂 Kapatılan İşler"])
    else: # Operatör
        menu = st.sidebar.radio("Operatör Paneli", ["⚠️ Arıza Bildir", "🕒 Taleplerim"])

    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.auth = None
        st.rerun()

    # --- ADMIN: MAKİNE YÖNETİMİ (YENİ!) ---
    if role == "Admin" and menu == "🏭 Makine Yönetimi":
        st.header("Fabrika Makine Listesi")
        
        # Makine Ekleme
        with st.form("add_machine"):
            new_m = st.text_input("Yeni Makine/Hat Adı")
            if st.form_submit_button("Makineyi Sisteme Ekle"):
                if new_m and not any(d['name'] == new_m for d in st.session_state.machines):
                    st.session_state.machines.append({"name": new_m})
                    save_data(MACHINE_FILE, st.session_state.machines)
                    st.success(f"{new_m} başarıyla eklendi.")
                    st.rerun()

        # Mevcut Makineleri Listele ve Sil
        st.subheader("Mevcut Makineler")
        for i, m in enumerate(st.session_state.machines):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🔹 {m['name']}")
            if col2.button("Sil", key=f"del_{i}"):
                st.session_state.machines.pop(i)
                save_data(MACHINE_FILE, st.session_state.machines)
                st.rerun()

    # --- OPERATÖR: ARIZA BİLDİR (Dinamik Liste) ---
    elif menu == "⚠️ Arıza Bildir":
        st.header("Arıza Kaydı Oluştur")
        with st.form("op_form"):
            machine_list = [m['name'] for m in st.session_state.machines]
            makine = st.selectbox("Makine Seçin", machine_list if machine_list else ["Lütfen makine ekleyin"])
            arıza = st.text_area("Arıza Açıklaması")
            if st.form_submit_button("Bildirimi Gönder"):
                new_task = {
                    "id": len(st.session_state.tasks) + 1,
                    "tarih": datetime.datetime.now().strftime("%d/%m %H:%M"),
                    "makine": makine, "arıza": arıza, "op": name,
                    "durum": "Açık", "bakımcı": "", "islem": "", "parca": "", "maliyet": 0
                }
                st.session_state.tasks.append(new_task)
                save_data(DATA_FILE, st.session_state.tasks)
                st.success("Arıza bildirildi.")

    # --- BAKIMCI: ARIZA KAPATMA ---
    elif menu == "🔧 Açık Arızalar":
        st.header("Müdahale Bekleyen İşler")
        acik_isler = [t for t in st.session_state.tasks if t['durum'] == "Açık"]
        for t in acik_isler:
            with st.expander(f"İŞ #{t['id']} - {t['makine']}"):
                st.write(f"**Operatör Notu:** {t['arıza']}")
                with st.form(f"f_{t['id']}"):
                    islem = st.text_area("Yapılan Müdahale")
                    p_kullanildi = st.checkbox("Yedek Parça Kullanıldı")
                    p_detay = st.text_input("Parça Adı/Kodu")
                    ucret = st.number_input("Maliyet", min_value=0)
                    if st.form_submit_button("Arızayı Onarımı Bitir"):
                        t['durum'] = "Tamamlandı"
                        t['bakımcı'] = name
                        t['islem'] = islem
                        t['parca'] = p_detay if p_kullanildi else "Kullanılmadı"
                        t['maliyet'] = ucret
                        save_data(DATA_FILE, st.session_state.tasks)
                        st.success("İş kapatıldı.")
                        st.rerun()

    # --- DİĞER MENÜLER (Kullanıcı, Dashboard) ---
    elif role == "Admin" and menu == "👥 Kullanıcılar":
        st.header("Kullanıcı Yönetimi")
        with st.form("add_u"):
            nu, np, nr = st.text_input("Ad"), st.text_input("Şifre"), st.selectbox("Rol", ["Operatör", "Bakımcı", "Admin"])
            if st.form_submit_button("Ekle"):
                st.session_state.users.append({"user": nu, "pass": np, "role": nr})
                save_data(USER_FILE, st.session_state.users)
                st.rerun()
        st.table(pd.DataFrame(st.session_state.users))

    elif menu == "📊 Dashboard" or menu == "📋 Tüm Kayıtlar":
        if st.session_state.tasks:
            df = pd.DataFrame(st.session_state.tasks)
            if menu == "📊 Dashboard":
                st.header("Analiz")
                st.metric("Toplam Harcama", f"{df['maliyet'].sum()} TL")
                st.bar_chart(df['makine'].value_counts())
            else:
                st.header("Arşiv")
                st.dataframe(df)

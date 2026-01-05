import streamlit as st
import pandas as pd
import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Maintor PRO", layout="wide", page_icon="⚙️")

# --- VERİ YÖNETİMİ ---
DATA_FILE = "maintor_data.csv"
USER_FILE = "maintor_users.csv"
MACHINE_FILE = "maintor_machines.csv"

def load_data(file, default_data):
    if os.path.exists(file): return pd.read_csv(file).to_dict('records')
    return default_data

def save_data(file, data): pd.DataFrame(data).to_csv(file, index=False)

# Verileri Başlat
if 'tasks' not in st.session_state: st.session_state.tasks = load_data(DATA_FILE, [])
if 'users' not in st.session_state: st.session_state.users = load_data(USER_FILE, [{"user": "admin", "pass": "123", "role": "Admin"}])
if 'machines' not in st.session_state: st.session_state.machines = load_data(MACHINE_FILE, [{"name": "Pres 01"}, {"name": "CNC 02"}])

# --- GİRİŞ KONTROLÜ ---
if "auth" not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    st.title("🚀 MAINTOR PRO GİRİŞ")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş"):
        user_match = next((x for x in st.session_state.users if x['user'] == u and str(x['pass']) == p), None)
        if user_match:
            st.session_state.auth = user_match
            st.rerun()
        else: st.error("Hatalı kullanıcı bilgileri!")
else:
    role = st.session_state.auth['role']
    name = st.session_state.auth['user']
    st.sidebar.title("⚙️ MAINTOR")
    st.sidebar.write(f"Kullanıcı: **{name}**")
    st.sidebar.write(f"Yetki: **{role}**")

    # Menüler
    if role == "Admin":
        menu = st.sidebar.radio("Yönetim Paneli", ["📊 Dashboard", "🏭 Makine Yönetimi", "👥 Kullanıcı Yönetimi", "📋 Arıza Arşivi"])
    elif role == "Bakımcı":
        menu = st.sidebar.radio("Bakım Menüsü", ["🔧 Açık Arızalar", "📂 Geçmiş İşler"])
    else:
        menu = st.sidebar.radio("Operatör Menüsü", ["⚠️ Arıza Bildir", "🕒 Taleplerim"])

    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.auth = None
        st.rerun()

    # --- DASHBOARD (GÜNCELLENDİ: MALİYET KALDIRILDI) ---
    if menu == "📊 Dashboard":
        st.header("📊 Fabrika Genel Durumu")
        df = pd.DataFrame(st.session_state.tasks)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div style="background-color:#ff4b4b; padding:20px; border-radius:10px; text-align:center; color:white;"><h3>🔴 AÇIK</h3><h1>{len(df[df["durum"]=="Açık"])}</h1></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="background-color:#ffa500; padding:20px; border-radius:10px; text-align:center; color:white;"><h3>🟡 BEKLEYEN</h3><h1>{len(df[df["durum"]=="Beklemede"])}</h1></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div style="background-color:#28a745; padding:20px; border-radius:10px; text-align:center; color:white;"><h3>🟢 TAMAMLANAN</h3><h1>{len(df[df["durum"]=="Tamamlandı"])}</h1></div>', unsafe_allow_html=True)
            st.divider()
            st.subheader("Makine Bazlı Arıza Dağılımı")
            st.bar_chart(df['makine'].value_counts())
        else:
            st.info("Henüz kayıtlı arıza bulunmuyor.")

    # --- KULLANICI YÖNETİMİ (TAMİR EDİLDİ) ---
    elif menu == "👥 Kullanıcı Yönetimi":
        st.header("👥 Kullanıcı Yönetimi")
        
        # Kullanıcı Ekleme Formu
        with st.expander("➕ Yeni Kullanıcı Ekle"):
            with st.form("user_add_form"):
                new_u = st.text_input("Kullanıcı Adı")
                new_p = st.text_input("Şifre")
                new_r = st.selectbox("Yetki Rolü", ["Operatör", "Bakımcı", "Admin"])
                if st.form_submit_button("Kullanıcıyı Kaydet"):
                    if new_u and new_p:
                        st.session_state.users.append({"user": new_u, "pass": new_p, "role": new_r})
                        save_data(USER_FILE, st.session_state.users)
                        st.success(f"{new_u} sisteme eklendi!")
                        st.rerun()
                    else: st.warning("Lütfen tüm alanları doldurun.")

        # Kullanıcı Listeleme ve Silme
        st.subheader("Mevcut Kullanıcılar")
        for i, u in enumerate(st.session_state.users):
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(f"👤 {u['user']}")
            col2.write(f"🔑 {u['role']}")
            if u['user'] != "admin": # Ana admin silinemesin
                if col3.button("Sil", key=f"user_del_{i}"):
                    st.session_state.users.pop(i)
                    save_data(USER_FILE, st.session_state.users)
                    st.rerun()

    # --- MAKİNE YÖNETİMİ ---
    elif menu == "🏭 Makine Yönetimi":
        st.header("🏭 Makine Yönetimi")
        with st.form("m_add"):
            m_name = st.text_input("Yeni Makine Adı")
            if st.form_submit_button("Ekle"):
                st.session_state.machines.append({"name": m_name})
                save_data(MACHINE_FILE, st.session_state.machines)
                st.rerun()
        for i, m in enumerate(st.session_state.machines):
            c1, c2 = st.columns([4,1])
            c1.write(f"⚙️ {m['name']}")
            if c2.button("Sil", key=f"m_del_{i}"):
                st.session_state.machines.pop(i)
                save_data(MACHINE_FILE, st.session_state.machines)
                st.rerun()

    # --- OPERATÖR VE BAKIMCI EKRANLARI (MALİYET KALDIRILDI) ---
    elif menu == "⚠️ Arıza Bildir":
        st.header("Arıza Bildirimi")
        with st.form("op_form"):
            makine = st.selectbox("Makine", [m['name'] for m in st.session_state.machines])
            detay = st.text_area("Arıza Açıklaması")
            if st.form_submit_button("Kaydı Aç"):
                st.session_state.tasks.append({
                    "id": len(st.session_state.tasks)+1, "tarih": datetime.datetime.now().strftime("%d/%m %H:%M"),
                    "makine": makine, "arıza": detay, "op": name, "durum": "Açık", "islem": "", "parca": ""
                })
                save_data(DATA_FILE, st.session_state.tasks)
                st.success("Arıza bildirildi!")

    elif menu == "🔧 Açık Arızalar":
        st.header("Açık Arıza İşleri")
        isler = [t for t in st.session_state.tasks if t['durum'] != "Tamamlandı"]
        for t in isler:
            with st.expander(f"İŞ #{t['id']} - {t['makine']}"):
                st.write(f"**Operatör:** {t['op']} | **Açıklama:** {t['arıza']}")
                with st.form(f"fix_{t['id']}"):
                    y_durum = st.selectbox("Durum", ["Açık", "Beklemede", "Tamamlandı"])
                    islem = st.text_area("Yapılan İşlem")
                    p_kullandim = st.checkbox("Yedek parça kullandım")
                    p_notu = st.text_input("Hangi parça kullanıldı?")
                    if st.form_submit_button("Güncelle"):
                        t['durum'] = y_durum
                        t['islem'] = islem
                        t['parca'] = p_notu if p_kullandim else "Kullanılmadı"
                        save_data(DATA_FILE, st.session_state.tasks)
                        st.rerun()

    elif menu == "📋 Arıza Arşivi" or menu == "📂 Geçmiş İşler":
        st.header("Arıza Kayıtları")
        st.dataframe(pd.DataFrame(st.session_state.tasks))

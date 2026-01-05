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
    if os.path.exists(file):
        try:
            return pd.read_csv(file).to_dict('records')
        except:
            return default_data
    return default_data

def save_data(file, data):
    pd.DataFrame(data).to_csv(file, index=False)

# Verileri Session State'e Yükle
if 'tasks' not in st.session_state: st.session_state.tasks = load_data(DATA_FILE, [])
if 'users' not in st.session_state: st.session_state.users = load_data(USER_FILE, [{"user": "admin", "pass": "123", "role": "Admin"}])
if 'machines' not in st.session_state: st.session_state.machines = load_data(MACHINE_FILE, [{"name": "Pres 01"}])

# --- GİRİŞ KONTROLÜ ---
if "auth" not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    st.title("🚀 MAINTOR PRO GİRİŞ")
    u = st.text_input("Kullanıcı Adı", key="login_u")
    p = st.text_input("Şifre", type="password", key="login_p")
    if st.button("Sisteme Giriş"):
        user_match = next((x for x in st.session_state.users if x['user'] == u and str(x['pass']) == p), None)
        if user_match:
            st.session_state.auth = user_match
            st.rerun()
        else: st.error("Hatalı bilgiler!")
else:
    role = st.session_state.auth['role']
    name = st.session_state.auth['user']
    st.sidebar.title("⚙️ MAINTOR")
    st.sidebar.info(f"Kullanıcı: {name}\nYetki: {role}")

    if role == "Admin":
        menu = st.sidebar.radio("Menü", ["📊 Dashboard", "🏭 Makine Yönetimi", "👥 Kullanıcılar", "📋 Arşiv"])
    elif role == "Bakımcı":
        menu = st.sidebar.radio("Menü", ["🔧 Açık Arızalar", "📂 Geçmiş İşler"])
    else:
        menu = st.sidebar.radio("Menü", ["⚠️ Arıza Bildir", "🕒 Taleplerim"])

    if st.sidebar.button("Çıkış Yap"):
        st.session_state.auth = None
        st.rerun()

    # --- BAKIMCI EKRANI (KESİN ÇÖZÜM MODÜLÜ) ---
    if menu == "🔧 Açık Arızalar":
        st.header("🔧 Onarım Bekleyen İşler")
        
        # Sadece Tamamlanmamışları listele
        # İndeksleri korumak için enumerate kullanıyoruz
        for idx, t in enumerate(st.session_state.tasks):
            if t['durum'] != "Tamamlandı":
                with st.expander(f"İŞ #{t.get('id', idx)} - {t['makine']} - {t['tarih']}", expanded=True):
                    st.error(f"**Arıza Detayı:** {t['arıza']}")
                    st.write(f"**Bildiren:** {t['op']}")
                    
                    # Form kullanmadan doğrudan giriş alanları (Daha stabil)
                    y_durum = st.selectbox("Durumu Değiştir", ["Açık", "Beklemede", "Tamamlandı"], key=f"status_{idx}")
                    y_islem = st.text_area("Yapılan İşlem", key=f"work_{idx}")
                    y_parca = st.text_input("Kullanılan Parça (Yoksa boş bırakın)", key=f"part_{idx}")
                    
                    if st.button("KAYDI GÜNCELLE / KAPAT", key=f"btn_{idx}"):
                        # Doğrudan session_state içindeki veriyi güncelle
                        st.session_state.tasks[idx]['durum'] = y_durum
                        st.session_state.tasks[idx]['islem'] = y_islem
                        st.session_state.tasks[idx]['parca'] = y_parca if y_parca else "Kullanılmadı"
                        st.session_state.tasks[idx]['bakimci'] = name
                        
                        # Dosyaya kaydet
                        save_data(DATA_FILE, st.session_state.tasks)
                        st.success("Kayıt başarıyla güncellendi!")
                        st.rerun()

    # --- OPERATÖR: ARIZA BİLDİR ---
    elif menu == "⚠️ Arıza Bildir":
        st.header("⚠️ Yeni Arıza Bildirimi")
        with st.form("op_form"):
            m_list = [m['name'] for m in st.session_state.machines]
            makine = st.selectbox("Makine Seçin", m_list)
            detay = st.text_area("Arıza nedir?")
            if st.form_submit_button("Sisteme Gönder"):
                new_id = len(st.session_state.tasks) + 1
                st.session_state.tasks.append({
                    "id": new_id, "tarih": datetime.datetime.now().strftime("%d/%m %H:%M"),
                    "makine": makine, "arıza": detay, "op": name, "durum": "Açık", "islem": "", "parca": "", "bakimci": ""
                })
                save_data(DATA_FILE, st.session_state.tasks)
                st.success("Arıza kaydı açıldı.")
                st.rerun()

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.header("📊 Fabrika Durumu")
        df = pd.DataFrame(st.session_state.tasks)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Açık Arıza", len(df[df['durum']=="Açık"]))
            c2.metric("Bekleyen", len(df[df['durum']=="Beklemede"]))
            c3.metric("Tamamlanan", len(df[df['durum']=="Tamamlandı"]))
            st.bar_chart(df['makine'].value_counts())
        else: st.info("Veri yok.")

    # --- DİĞER STANDART MODÜLLER ---
    elif menu == "🏭 Makine Yönetimi":
        st.header("🏭 Makine Yönetimi")
        m_ad = st.text_input("Makine Adı")
        if st.button("Ekle"):
            st.session_state.machines.append({"name": m_ad})
            save_data(MACHINE_FILE, st.session_state.machines)
            st.rerun()
        st.table(pd.DataFrame(st.session_state.machines))

    elif menu == "👥 Kullanıcılar":
        st.header("👥 Kullanıcı Yönetimi")
        with st.form("u_form"):
            un, up, ur = st.text_input("Ad"), st.text_input("Şifre"), st.selectbox("Rol", ["Operatör", "Bakımcı", "Admin"])
            if st.form_submit_button("Kullanıcıyı Ekle"):
                st.session_state.users.append({"user": un, "pass": up, "role": ur})
                save_data(USER_FILE, st.session_state.users)
                st.rerun()
        st.table(pd.DataFrame(st.session_state.users))

    elif menu == "📋 Arşiv" or menu == "📂 Geçmiş İşler":
        st.header("📋 Tüm Kayıtlar")
        if st.session_state.tasks:
            st.dataframe(pd.DataFrame(st.session_state.tasks))

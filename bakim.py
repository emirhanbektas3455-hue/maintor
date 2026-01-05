import streamlit as st
import pandas as pd
import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Maintor PRO | Dashboard", layout="wide", page_icon="📊")

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
    st.title("🚀 MAINTOR PRO")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        user_match = next((x for x in st.session_state.users if x['user'] == u and str(x['pass']) == p), None)
        if user_match:
            st.session_state.auth = user_match
            st.rerun()
        else: st.error("Hatalı bilgiler!")
else:
    role = st.session_state.auth['role']
    name = st.session_state.auth['user']
    
    st.sidebar.title("⚙️ MAINTOR")
    st.sidebar.write(f"Rol: {role}")
    
    # Menüler
    if role == "Admin":
        menu = st.sidebar.radio("Yönetim", ["📊 Dashboard", "🏭 Makine Yönetimi", "👥 Kullanıcılar", "📋 Tüm Kayıtlar"])
    elif role == "Bakımcı":
        menu = st.sidebar.radio("Bakım", ["🔧 Açık Arızalar", "📂 Kapatılan İşler"])
    else:
        menu = st.sidebar.radio("Operatör", ["⚠️ Arıza Bildir", "🕒 Taleplerim"])

    if st.sidebar.button("Çıkış Yap"):
        st.session_state.auth = None
        st.rerun()

    # --- DASHBOARD (RENKLİ KARTLAR SİSTEMİ) ---
    if menu == "📊 Dashboard":
        st.title("📈 Fabrika Durum Paneli")
        
        df = pd.DataFrame(st.session_state.tasks)
        
        if not df.empty:
            # Durumlara Göre Sayılar
            toplam_is = len(df)
            acik_is = len(df[df['durum'] == "Açık"])
            bekleyen_is = len(df[df['durum'] == "Beklemede"])
            tamamlanan_is = len(df[df['durum'] == "Tamamlandı"])
            toplam_maliyet = df['maliyet'].sum()

            # --- RENKLİ KARTLAR (CSS İLE) ---
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown(f"""<div style="background-color:#ff4b4b; padding:20px; border-radius:10px; text-align:center;">
                    <h3 style="color:white; margin:0;">🔴 AÇIK</h3>
                    <h1 style="color:white; margin:0;">{acik_is}</h1>
                    <p style="color:white; margin:0;">Müdahale Bekliyor</p>
                </div>""", unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""<div style="background-color:#ffa500; padding:20px; border-radius:10px; text-align:center;">
                    <h3 style="color:white; margin:0;">🟡 BEKLEYEN</h3>
                    <h1 style="color:white; margin:0;">{bekleyen_is}</h1>
                    <p style="color:white; margin:0;">Parça/Onay Bekliyor</p>
                </div>""", unsafe_allow_html=True)

            with c3:
                st.markdown(f"""<div style="background-color:#28a745; padding:20px; border-radius:10px; text-align:center;">
                    <h3 style="color:white; margin:0;">🟢 BİTEN</h3>
                    <h1 style="color:white; margin:0;">{tamamlanan_is}</h1>
                    <p style="color:white; margin:0;">Tamamlanan İşler</p>
                </div>""", unsafe_allow_html=True)

            with c4:
                st.markdown(f"""<div style="background-color:#1c83e1; padding:20px; border-radius:10px; text-align:center;">
                    <h3 style="color:white; margin:0;">💰 MALİYET</h3>
                    <h1 style="color:white; margin:0;">{int(toplam_maliyet)} ₺</h1>
                    <p style="color:white; margin:0;">Toplam Harcama</p>
                </div>""", unsafe_allow_html=True)

            st.write("---")
            
            # Alt Grafikler
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Makine Bazlı Arıza Sayıları")
                st.bar_chart(df['makine'].value_counts())
            with g2:
                st.subheader("İş Emri Dağılımı")
                st.write(df['durum'].value_counts())
        else:
            st.info("Sistemde henüz hiç veri yok. Operatör ekranından arıza kaydı açarak Dashboard'u canlandırabilirsiniz!")

    # --- MAKİNE YÖNETİMİ ---
    elif menu == "🏭 Makine Yönetimi":
        st.header("Makine Ekle / Sil")
        with st.form("m_ekle"):
            m_ad = st.text_input("Makine Adı")
            if st.form_submit_button("Ekle"):
                st.session_state.machines.append({"name": m_ad})
                save_data(MACHINE_FILE, st.session_state.machines)
                st.rerun()
        st.write("### Kayıtlı Makineler")
        for i, m in enumerate(st.session_state.machines):
            c_a, c_b = st.columns([3,1])
            c_a.write(f"⚙️ {m['name']}")
            if c_b.button("Sil", key=f"m_{i}"):
                st.session_state.machines.pop(i)
                save_data(MACHINE_FILE, st.session_state.machines)
                st.rerun()

    # --- OPERATÖR: ARIZA BİLDİR ---
    elif menu == "⚠️ Arıza Bildir":
        st.header("Yeni Arıza Kaydı")
        with st.form("op_f"):
            m_list = [m['name'] for m in st.session_state.machines]
            secilen = st.selectbox("Makine", m_list)
            notu = st.text_area("Arıza Nedir?")
            if st.form_submit_button("Sisteme Gönder"):
                st.session_state.tasks.append({
                    "id": len(st.session_state.tasks)+1, "tarih": datetime.datetime.now().strftime("%d/%m %H:%M"),
                    "makine": secilen, "arıza": notu, "op": name, "durum": "Açık", "maliyet": 0, "islem": "", "parca": ""
                })
                save_data(DATA_FILE, st.session_state.tasks)
                st.success("Kayıt açıldı!")

    # --- BAKIMCI: ARIZA KAPATMA ---
    elif menu == "🔧 Açık Arızalar":
        st.header("Müdahale Bekleyenler")
        isler = [t for t in st.session_state.tasks if t['durum'] != "Tamamlandı"]
        for t in isler:
            with st.expander(f"İŞ #{t['id']} - {t['makine']}"):
                st.write(f"**Açıklama:** {t['arıza']}")
                with st.form(f"f_{t['id']}"):
                    y_durum = st.selectbox("Durum Güncelle", ["Açık", "Beklemede", "Tamamlandı"])
                    islem = st.text_area("Yapılan İşlem")
                    para = st.number_input("Maliyet", min_value=0)
                    if st.form_submit_button("Kaydet"):
                        t['durum'] = y_durum
                        t['islem'] = islem
                        t['maliyet'] = para
                        save_data(DATA_FILE, st.session_state.tasks)
                        st.rerun()

    # --- KULLANICILAR VE TÜM KAYITLAR ---
    elif menu == "👥 Kullanıcılar":
        st.write("Admin Paneli - Kullanıcılar")
        st.table(pd.DataFrame(st.session_state.users))
    elif menu == "📋 Tüm Kayıtlar":
        st.write("Veritabanı")
        st.dataframe(pd.DataFrame(st.session_state.tasks))

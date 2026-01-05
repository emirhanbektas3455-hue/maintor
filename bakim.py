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
        try: return pd.read_csv(file).to_dict('records')
        except: return default_data
    return default_data

def save_data(file, data):
    pd.DataFrame(data).to_csv(file, index=False)

# Verileri Başlat
if 'tasks' not in st.session_state: st.session_state.tasks = load_data(DATA_FILE, [])
if 'users' not in st.session_state: st.session_state.users = load_data(USER_FILE, [{"user": "admin", "pass": "123", "role": "Admin"}])
if 'machines' not in st.session_state: st.session_state.machines = load_data(MACHINE_FILE, [{"name": "Pres 01"}])

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
        else: st.error("Hatalı bilgiler!")
else:
    role = st.session_state.auth['role']
    name = st.session_state.auth['user']
    st.sidebar.title("⚙️ MAINTOR")
    st.sidebar.info(f"Kullanıcı: {name}\n\nYetki: {role}")

    # Menüler
    if role == "Admin":
        menu = st.sidebar.radio("Yönetim", ["📊 Dashboard", "🏭 Makine Yönetimi", "👥 Kullanıcı Yönetimi", "📋 Arıza Arşivi"])
    elif role == "Bakımcı":
        menu = st.sidebar.radio("Bakım Menüsü", ["🔧 Açık Arızalar", "📂 Geçmiş İşler"])
    else:
        menu = st.sidebar.radio("Operatör Menüsü", ["⚠️ Arıza Bildir", "🕒 Taleplerim"])

    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.auth = None
        st.rerun()

    # --- BAKIMCI: ARIZA KAPATMA (TAMİR EDİLEN BÖLÜM) ---
    if menu == "🔧 Açık Arızalar":
        st.header("🔧 Müdahale Bekleyen Arızalar")
        # Sadece Tamamlanmamış işleri getir
        isler = [t for t in st.session_state.tasks if t['durum'] != "Tamamlandı"]
        
        if not isler:
            st.success("Tebrikler! Açıkta bekleyen arıza kaydı bulunmuyor.")
        
        for idx, t in enumerate(isler):
            with st.expander(f"İŞ #{t.get('id', idx)} - {t['makine']} ({t['tarih']})", expanded=True):
                st.warning(f"**Operatör Notu:** {t['arıza']}")
                
                # Her iş emri için benzersiz bir form
                with st.form(key=f"fix_form_{idx}"):
                    yeni_durum = st.selectbox("Durumu Güncelle", ["Açık", "Beklemede", "Tamamlandı"], index=0)
                    islem_notu = st.text_area("Yapılan İşlemler", value=t.get('islem', ''))
                    p_kullandim = st.checkbox("Yedek Parça Kullanıldı mı?")
                    p_notu = st.text_input("Kullanılan Parça Bilgisi")
                    
                    submit = st.form_submit_button("KAYDI GÜNCELLE / KAPAT")
                    
                    if submit:
                        # Ana listedeki doğru iş emrini bul ve güncelle
                        for real_task in st.session_state.tasks:
                            if real_task.get('id') == t.get('id'):
                                real_task['durum'] = yeni_durum
                                real_task['islem'] = islem_notu
                                real_task['parca'] = p_notu if p_kullandim else "Kullanılmadı"
                                real_task['bakimci'] = name
                                break
                        
                        save_data(DATA_FILE, st.session_state.tasks)
                        st.success("İşlem kaydedildi! Liste güncelleniyor...")
                        st.rerun()

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.header("📊 Fabrika Durum Paneli")
        df = pd.DataFrame(st.session_state.tasks)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div style="background-color:#ff4b4b; padding:20px; border-radius:10px; text-align:center; color:white;"><h3>AÇIK</h3><h1>{len(df[df["durum"]=="Açık"])}</h1></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div style="background-color:#ffa500; padding:20px; border-radius:10px; text-align:center; color:white;"><h3>BEKLEYEN</h3><h1>{len(df[df["durum"]=="Beklemede"])}</h1></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div style="background-color:#28a745; padding:20px; border-radius:10px; text-align:center; color:white;"><h3>TAMAMLANAN</h3><h1>{len(df[df["durum"]=="Tamamlandı"])}</h1></div>', unsafe_allow_html=True)
            st.bar_chart(df['makine'].value_counts())
        else: st.info("Veri bulunamadı.")

    # --- KULLANICI YÖNETİMİ ---
    elif menu == "👥 Kullanıcı Yönetimi":
        st.header("👥 Kullanıcı Yönetimi")
        with st.form("new_u"):
            nu, np, nr = st.text_input("Kullanıcı Adı"), st.text_input("Şifre"), st.selectbox("Rol", ["Operatör", "Bakımcı", "Admin"])
            if st.form_submit_button("Kullanıcı Ekle"):
                st.session_state.users.append({"user": nu, "pass": np, "role": nr})
                save_data(USER_FILE, st.session_state.users)
                st.rerun()
        st.table(pd.DataFrame(st.session_state.users))

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

    # --- OPERATÖR: ARIZA BİLDİR ---
    elif menu == "⚠️ Arıza Bildir":
        st.header("⚠️ Yeni Arıza Bildirimi")
        with st.form("op_form"):
            makine = st.selectbox("Makine", [m['name'] for m in st.session_state.machines])
            detay = st.text_area("Arıza Detayı")
            if st.form_submit_button("Kaydı Oluştur"):
                st.session_state.tasks.append({
                    "id": len(st.session_state.tasks)+1, "tarih": datetime.datetime.now().strftime("%d/%m %H:%M"),
                    "makine": makine, "arıza": detay, "op": name, "durum": "Açık", "islem": "", "parca": ""
                })
                save_data(DATA_FILE, st.session_state.tasks)
                st.success("Arıza bildirildi!")

    elif menu == "📋 Arıza Arşivi" or menu == "📂 Geçmiş İşler":
        st.header("Arıza Kayıtları")
        st.dataframe(pd.DataFrame(st.session_state.tasks))

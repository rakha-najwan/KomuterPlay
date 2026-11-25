import streamlit as st

# 1. Pengaturan dasar halaman web
st.set_page_config(page_title="KomuterPlay", page_icon="🚆", layout="centered")

# 2. Dummy data sementara (nanti diganti pakai data asli dari Anggota 1)
dummy_user = {
    "nama": "Budi Komuter",
    "saldo": 50000,
    "poin": 120,
    "level": "Level 1: Pejalan Pemula"
}

# 3. Header Aplikasi (Info Saldo & Poin di bagian atas)
st.title("🚆 KomuterPlay")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Saldo E-Money", value=f"Rp {dummy_user['saldo']:,}")
with col2:
    st.metric(label="Total Poin", value=f"{dummy_user['poin']} Poin")

st.divider()

# 4. Menu Navigasi Utama (5 Menu sesuai rancangan)
menu = st.sidebar.radio(
    "Navigasi Utama",
    ["Beranda", "Peta Interaktif", "Task & Event", "E-Money & Tiket", "Redeem Point"]
)

# 5. Isi Halaman (Masih Placeholder)
if menu == "Beranda":
    st.subheader(f"Halo, {dummy_user['nama']}! 👋")
    st.info(f"Status saat ini: **{dummy_user['level']}**")
    st.write("Selamat datang di KomuterPlay. Pilih menu di sebelah kiri untuk mulai perjalananmu.")

elif menu == "Peta Interaktif":
    st.subheader("🗺️ Peta Interaktif Jakarta")
    st.warning("Placeholder: Nanti di sini kita panggil fungsi render_map(user) buatan Anggota 2.")

elif menu == "Task & Event":
    st.subheader("🎯 Task & Event")
    st.info("Placeholder: Bagian ini nanti kamu isi dengan daftar misi harian & event.")

elif menu == "E-Money & Tiket":
    st.subheader("💳 E-Money & Tiket Terpadu")
    st.warning("Placeholder: Nanti di sini kita panggil fungsi render_wallet(user) buatan Anggota 1.")

elif menu == "Redeem Point":
    st.subheader("🎁 Katalog Redeem Point")
    st.info("Placeholder: Bagian ini nanti kamu isi dengan katalog voucher F&B & tiket.")
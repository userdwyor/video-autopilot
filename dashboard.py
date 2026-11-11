import streamlit as st
import requests
from datetime import datetime
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Studio Control Room", page_icon="🎬", layout="centered")

st.title("🎬 AI Studio Control Room")
st.write("Selamat datang, Bos! Dari sini lo bisa ngontrol pabrik video lo tanpa buka GitHub.")

# --- SETUP API ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception as e:
    st.error("⚠️ Token GitHub belum dimasukkan di Secrets.")
    st.stop()

headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# --- LOGIKA STATUS DARI GITHUB ---
st.divider()
st.subheader("📊 Status Pabrik Terakhir")

def get_latest_run():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        for run in runs:
            if run["name"] == "Daily Video Autopilot":
                return run
    return None

latest_run = get_latest_run()

if latest_run:
    status = latest_run["status"]
    conclusion = latest_run.get("conclusion")
    created_at = datetime.strptime(latest_run["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y, %H:%M")
    
    if status == "in_progress":
        st.info(f"🟡 **Lagi Produksi Video!** (Dimulai: {created_at})")
    elif conclusion == "success":
        st.success(f"🟢 **Sukses!** Video beres dibuat. (Waktu: {created_at})")
        st.markdown(f"[📥 Download Video Terbaru di Sini]({latest_run['html_url']})")
    elif conclusion == "failure":
        st.error(f"🔴 **Gagal.** Ada error di mesin. (Waktu: {created_at})")
        st.markdown(f"[🔍 Cek Log Error di Sini]({latest_run['html_url']})")
else:
    st.warning("Belum ada riwayat produksi.")

# --- TOMBOL PRODUKSI (DENGAN DROPDOWN) ---
st.divider()
st.subheader("🚀 Produksi Video Baru")

# Dropdown buat milih tema
channel_choice = st.selectbox(
    "Pilih Tema Konten:",
    ["horor_lucu", "motivation", "facts", "money"],
    help="Pastikan nama tema ini ada di config/channels.yaml"
)

# Checkbox buat dry run
is_dry_run = st.checkbox("Mode Tes (Dry Run - Jangan Upload ke Sosmed)", value=True)

if st.button("BUAT VIDEO SEKARANG!", use_container_width=True, type="primary"):
    dispatch_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/daily.yml/dispatches"
    
    payload = {
        "ref": "main",
        "inputs": {
            "dry_run": is_dry_run, 
            "channel": channel_choice
        }
    }
    
    response = requests.post(dispatch_url, headers=headers, json=payload)
    
    if response.status_code == 204:
        st.success(f"✅ Perintah diterima! Pabrik mulai bikin video tema **{channel_choice}**. Tunggu 15-20 menit.")
    else:
        st.error(f"❌ Gagal ngasih perintah. Error Code: {response.status_code}")
        st.write("**Pesan Error dari GitHub:**")
        st.code(response.text)

# --- LINK KANTOR VIRTUAL (OPSIONAL) ---
st.divider()
st.subheader("🏢 Kantor Virtual 3D")
st.write("Buka kantor 3D lo di tab baru (biar HP nggak berat).")

# Ganti link di bawah ini dengan link GitHub Pages lo atau link Hermes lo (kalau udah jalan)
st.link_button("🚀 Buka Kantor Virtual (Full Screen)", "http://localhost:3000/office", use_container_width=True)

st.caption("Dibuat dengan 💻 dan ☕ oleh Bos Besar.")

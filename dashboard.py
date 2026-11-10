import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="AI Studio Control Room", page_icon="🎬", layout="centered")

st.title("🎬 AI Studio Control Room")
st.write("Selamat datang, Bos! Dari sini lo bisa ngontrol pabrik video lo tanpa buka GitHub.")

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception as e:
    st.error("⚠️ Setup belum selesai. Token GitHub belum dimasukkan.")
    st.stop()

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_latest_run():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        for run in runs:
            if run["name"] == "Daily Video Autopilot":
                return run
    return None

st.divider()
st.subheader("📊 Status Pabrik Terakhir")
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

st.divider()
st.subheader("🚀 Produksi Video Baru")

if st.button("BUAT VIDEO SEKARANG!", use_container_width=True, type="primary"):
    dispatch_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/daily.yml/dispatches"
    
    # Kita kirim format yang paling aman (sesuai tipe data di YAML)
    payload = {
        "ref": "main",
        "inputs": {
            "dry_run": True, 
            "channel": ""
        }
    }
    
    response = requests.post(dispatch_url, headers=headers, json=payload)
    
    if response.status_code == 204:
        st.success("✅ Perintah diterima! Pabrik mulai bekerja. Tunggu 15-20 menit, terus refresh halaman ini buat cek status.")
    else:
        st.error(f"❌ Gagal ngasih perintah. Error Code: {response.status_code}")
        st.write("**Pesan Error dari GitHub:**")
        st.code(response.text) # INI BAKAL NAMPILIN ERROR ASLINYA

st.divider()
st.divider()
st.subheader("🏢 Kantor Virtual 3D")
st.write("Geser layar pakai jari buat muter ruangannya!")

# Baca file office.html dan tampilin di dalam dashboard
import streamlit.components.v1 as components
import os

components.iframe("https://userdwyor.github.io/video-autopilot/office.html", height=500, scrolling=True)
st.caption("Dibuat dengan 💻 dan ☕ oleh Bos Besar.")

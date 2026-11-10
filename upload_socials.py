import os
import requests
import glob

api_key = os.environ.get("UPLOAD_POST_API_KEY")
# GANTI "nama-profil-lo" sesuai nama profil yang lo bikin di Upload-Post tadi
profile_name = "my" 

if not api_key:
    print("❌ API Key Upload-Post nggak ketemu!")
    exit(1)

# Nyari video paling baru yang selesai di-render
videos = glob.glob("output/**/final.mp4", recursive=True)
if not videos:
    print("❌ Nggak ada video yang jadi di folder output.")
    exit(0)

latest_video = max(videos, key=os.path.getctime)
print(f"🎬 Ketemu video: {latest_video}. Lagi di-upload...")

url = "https://api.upload-post.com/api/upload"
headers = {
    "Authorization": f"Apikey {api_key}"
}

# Buka videonya
with open(latest_video, 'rb') as video_file:
    files = {'video': video_file}
    data = {
        'user': profile_name,
        'platform[]': ['youtube', 'tiktok', 'instagram'], # Platform tujuan
        'title': 'Daily AI Video'
    }
    
    response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code in [200, 201]:
        print("✅ Sukses upload ke sosmed!")
        print(response.text)
    else:
        print(f"❌ Gagal upload. Status: {response.status_code}")
        print(response.text)

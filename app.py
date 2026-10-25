import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# Temporary Download Folder
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Standard Browser User-Agent header for bypassing bot detection
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def download_media():
    data = request.json or {}
    url = data.get("url")
    download_type = data.get("type", "no_wm") # no_wm, hd, mp3

    if not url or ("tiktok.com" not in url and "vt.tiktok.com" not in url):
        return jsonify({"status": "error", "message": "Please enter a valid TikTok link."}), 400

    file_id = str(uuid.uuid4())
    
    if download_type == "mp3":
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path,
            'http_headers': COMMON_HEADERS,
        }
    elif download_type == "hd":
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': file_path,
            'http_headers': COMMON_HEADERS,
        }
    else: # normal / no_wm
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'http_headers': COMMON_HEADERS,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        return jsonify({
            "status": "success",
            "download_url": f"/get-file/{os.path.basename(file_path)}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500


@app.route("/get-file/<filename>", methods=["GET"])
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        def generate():
            with open(file_path, "rb") as f:
                yield from f
            # Download complete howar sate sate Render server theke file delete hoye jabe
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
                
        return app.response_class(
            generate(), 
            mimetype="application/octet-stream", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    return "File not found", 404


if __name__ == "__main__":
    print("✅ Web App Server is Running...")
    app.run(debug=True, port=5000)

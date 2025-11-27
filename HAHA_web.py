import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from docx import Document
import pandas as pd
from pptx import Presentation
import io
import os
import glob
import yt_dlp  # Thư viện tải âm thanh YouTube mới

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="HAHA Chatbot", page_icon="🌿", layout="wide")

# --- 2. GIAO DIỆN (CSS - MESSENGER STYLE) ---
st.markdown("""
<style>
    /* Hình nền */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?q=80&w=2074&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    
    /* Thanh chat input */
    .stChatInputInput {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1e3a1e !important;
        padding-left: 50px !important; 
        border-radius: 20px !important;
    }
    
    /* Nút cộng (+) */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 35px !important; 
        left: 30px !important;   
        z-index: 100000 !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
    }

    /* Trang trí nút cộng */
    [data-testid="stPopover"] > button {
        background-color: transparent !important; 
        border: none !important;
        color: #555555 !important; 
        font-size: 30px !important; 
        font-weight: bold !important;
        padding: 0 !important;
        line-height: 1 !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    [data-testid="stPopover"] > button:hover {
        color: #4CAF50 !important;
        background-color: rgba(0,0,0,0.05) !important;
        border-radius: 50%;
    }

    /* Ẩn thành phần thừa */
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    h1 { color: #ffffff !important; text-shadow: 2px 2px 8px #000000; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ & LỜI CHÀO ---
st.title("🌿 HAHA - Trợ lý AI")
st.write("Chúc bạn một ngày tốt lành!")

# --- 4. CẤU HÌNH BỘ NÃO (KEY MỚI CỦA BẠN) ---
genai.configure(api_key='AIzaSyACQ5HcozNFRXoRGpov4MgQJIKRGp-sjOk')

tinh_cach = """
Bạn tên là HAHA.
Bạn là trợ lý AI được tạo ra bởi Hoàng Anh.
Bạn có khả năng Đa phương thức: Nghe, Nhìn, Đọc.
Đặc biệt: Bạn có thể NGHE âm thanh từ video YouTube để tóm tắt nội dung.
Phong cách trả lời: Thân thiện, thông minh, dùng icon thiên nhiên (🌿, 🍃).
"""
model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=tinh_cach)

# --- 5. QUẢN LÝ LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Chào bạn! Gửi link YouTube tôi sẽ 'nghe' và tóm tắt cho bạn! 🌿"]}
    ]

# --- 6. HÀM XỬ LÝ FILE ĐA NĂNG ---
def read_any_file(uploaded_file):
    try:
        filename = uploaded_file.name.lower()
        if uploaded_file.type.startswith("audio/") or filename.endswith((".mp3", ".wav", ".m4a")):
            mime = "audio/mp4" if filename.endswith(".m4a") else uploaded_file.type
            return uploaded_file.getvalue(), "audio", mime
        elif uploaded_file.type.startswith("image/"):
            return Image.open(uploaded_file), "image", uploaded_file.type
        elif uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            return text, "doc", "text/plain"
        elif filename.endswith(".docx"):
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text, "doc", "text/plain"
        elif filename.endswith((".xlsx", ".csv", ".pptx", ".txt", ".py", ".js")):
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8", errors='ignore'))
            return stringio.read(), "doc", "text/plain"
        else:
            return None, "error", None
    except Exception as e: return str(e), "error", None

# --- 7. HÀM TẢI ÂM THANH TỪ YOUTUBE (SỬ DỤNG YT-DLP) ---
def extract_youtube_id(url):
    # Regex nhận diện link youtube
    if "youtube.com" in url or "youtu.be" in url:
        return url # Trả về nguyên link để yt-dlp xử lý
    return None

def download_audio_from_youtube(url):
    try:
        # Cấu hình: Tải audio m4a (nhẹ nhất)
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': 'temp_audio_%(id)s.%(ext)s',
            'quiet': True,
            'noplaylist': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            ext = info['ext']
            # Trả về tên file đã tải
            return f"temp_audio_{video_id}.{ext}", None
            
    except Exception as e:
        return None, str(e)

# --- 8. NÚT CÔNG CỤ (+) ---
with st.popover("➕", use_container_width=False):
    tab1, tab2 = st.tabs(["🎙️ Thu âm", "📂 Tải file"])
    
    file_content = None
    file_type = ""
    mime_type = ""
    
    with tab1:
        audio_value = st.audio_input("Microphone") 
        if audio_value is not None:
            file_type = "audio"
            file_content = audio_value.read()
            mime_type = "audio/wav"
            st.success("✅ Đã thu âm!")

    with tab2:
        uploaded_file = st.file_uploader("", type=["jpg", "png", "pdf", "docx", "txt", "mp3", "wav", "m4a"])
        if uploaded_file is not None:
            data, type_detected, mime = read_any_file(uploaded_file)
            if type_detected == "error": st.error(f"Lỗi: {data}")
            else:
                file_type = type_detected
                file_content = data
                mime_type = mime
                st.success(f"✅ Đã nhận: {uploaded_file.name}")

# --- 9. HIỂN THỊ TIN NHẮN ---
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "🧑‍💻" if role == "user" else "🌳"
    with st.chat_message(role, avatar=avatar):
        content = message["parts"]
        if isinstance(content, list):
            for part in content:
                if isinstance(part, str): st.markdown(part)
                elif isinstance(part, Image.Image): st.image(part, width=200)
                elif isinstance(part, dict) and "mime_type" in part:
                    st.audio(part["data"], format=part["mime_type"])
        else: st.markdown(content[0])

# --- 10. XỬ LÝ CHAT ---
def loi_giai_stream(response):
    for chunk in response:
        if chunk.text: yield chunk.text

if prompt := st.chat_input("Nhập câu hỏi hoặc dán link YouTube..."):
    youtube_url = extract_youtube_id(prompt)

    # HIỂN THỊ USER
    with st.chat_message("user", avatar="🧑‍💻"):
        if youtube_url:
            st.markdown(f"📺 **[YouTube]** {prompt}")
            st.video(prompt)
            st.session_state.messages.append({"role": "user", "parts": [f"Link YouTube: {prompt}"]})
        elif file_type == "image":
            st.image(file_content, width=200)
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "parts": [file_content, prompt]})
        elif file_type == "audio":
            st.audio(file_content, format=mime_type)
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "parts": [{"mime_type": mime_type, "data": file_content}, prompt]})
        elif file_type == "doc":
            st.markdown(f"📄 **[File]**\n\n{prompt}")
            st.session_state.messages.append({"role": "user", "parts": [f"📄 [File]: {prompt}"]})
        else:
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # GỬI LÊN AI
    try:
        with st.chat_message("assistant", avatar="🌳"):
            # TRƯỜNG HỢP: YOUTUBE (TẢI AUDIO VÀ NGHE)
            if youtube_url:
                with st.spinner("🎧 Đang tải âm thanh từ YouTube... (Đợi chút nhé!)"):
                    audio_path, err = download_audio_from_youtube(youtube_url)
                
                if err:
                    st.error(f"Lỗi tải video: {err}")
                elif audio_path:
                    with st.spinner("🤖 Đang nghe và phân tích..."):
                        # Đọc file âm thanh
                        with open(audio_path, "rb") as f:
                            audio_bytes = f.read()
                        
                        # Gửi lên Gemini
                        req = [
                            "Hãy nghe kỹ đoạn âm thanh này và tóm tắt nội dung chính bằng tiếng Việt.",
                            {"mime_type": "audio/mp4", "data": audio_bytes}
                        ]
                        response = model.generate_content(req, stream=True)
                        full_response = st.write_stream(loi_giai_stream(response))
                        st.session_state.messages.append({"role": "model", "parts": [full_response]})
                        
                        # Xóa file tạm
                        try: os.remove(audio_path)
                        except: pass

            # TRƯỜNG HỢP: ẢNH
            elif file_type == "image":
                with st.spinner("HAHA đang suy nghĩ... 💭"):
                    response = model.generate_content([prompt, file_content], stream=True)
                    full_response = st.write_stream(loi_giai_stream(response))
                    st.session_state.messages.append({"role": "model", "parts": [full_response]})
            
            # TRƯỜNG HỢP: ÂM THANH
            elif file_type == "audio":
                with st.spinner("HAHA đang suy nghĩ... 💭"):
                    response = model.generate_content([prompt, {"mime_type": mime_type, "data": file_content}], stream=True)
                    full_response = st.write_stream(loi_giai_stream(response))
                    st.session_state.messages.append({"role": "model", "parts": [full_response]})
            
            # TRƯỜNG HỢP: TÀI LIỆU
            elif file_type == "doc":
                with st.spinner("HAHA đang suy nghĩ... 💭"):
                    response = model.generate_content(f"Tài liệu:\n{file_content}\n\nCâu hỏi: {prompt}", stream=True)
                    full_response = st.write_stream(loi_giai_stream(response))
                    st.session_state.messages.append({"role": "model", "parts": [full_response]})
            
            # TRƯỜNG HỢP: CHAT THƯỜNG
            else:
                with st.spinner("HAHA đang suy nghĩ... 💭"):
                    chat_hist = []
                    for m in st.session_state.messages:
                        if isinstance(m["parts"][0], str): 
                             chat_hist.append({"role": m["role"], "parts": [m["parts"][0]]})
                    chat = model.start_chat(history=chat_hist)
                    response = chat.send_message(prompt, stream=True)
                    full_response = st.write_stream(loi_giai_stream(response))
                    st.session_state.messages.append({"role": "model", "parts": [full_response]})
    
    except Exception as e:
        st.error(f"Lỗi: {e}")
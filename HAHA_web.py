import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from docx import Document
import pandas as pd
from pptx import Presentation
import io

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="HAHA Chatbot", page_icon="🌿", layout="wide")

# --- 2. GIAO DIỆN (CSS - ĐÃ CHỈNH SỬA TỌA ĐỘ) ---
st.markdown("""
<style>
    /* Hình nền */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?q=80&w=2074&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    
    /* 1. ĐẨY CHỮ TRONG KHUNG CHAT SANG PHẢI */
    .stChatInputInput {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1e3a1e !important;
        padding-left: 50px !important; /* Chừa chỗ trống bên trái cho nút cộng */
        border-radius: 20px !important;
    }
    
    /* 2. ÉP NÚT CỘNG NHỎ LẠI VÀ ĐƯA VÀO VỊ TRÍ */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 35px !important; /* Cách đáy 35px -> Nằm đúng tầm khung chat */
        left: 30px !important;   /* Cách trái 30px -> Nằm ngay đầu dòng */
        z-index: 100000 !important; /* Luôn nổi lên trên cùng */
        width: 40px !important;  /* Ép chiều rộng nhỏ lại, không cho dài ra */
        height: 40px !important;
        min-width: 40px !important; /* Khắc phục lỗi thành thanh dài */
    }

    /* 3. TRANG TRÍ ICON DẤU CỘNG */
    [data-testid="stPopover"] > button {
        background-color: transparent !important; /* Nền trong suốt */
        border: none !important;
        color: #555555 !important; /* Màu xám đậm */
        font-size: 30px !important; /* Icon to rõ */
        font-weight: bold !important;
        padding: 0 !important;
        line-height: 1 !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Hiệu ứng khi di chuột */
    [data-testid="stPopover"] > button:hover {
        color: #4CAF50 !important; /* Chuyển xanh khi hover */
        background-color: rgba(0,0,0,0.05) !important;
        border-radius: 50%;
    }

    /* Ẩn các thành phần thừa */
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    
    h1 { color: #ffffff !important; text-shadow: 2px 2px 8px #000000; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ ---
st.title("🌿 HAHA - Trợ lý AI")
st.write("Chúc bạn một ngày tốt lành!")

# --- 4. CẤU HÌNH BỘ NÃO ---
genai.configure(api_key='AIzaSyAD_3_sF05zi-HUQNNr2E58kBgqt8Vugw0')

tinh_cach = """
Bạn tên là HAHA.
Bạn là trợ lý AI được tạo ra bởi Hoàng Anh.
Bạn có khả năng Đa phương thức: Nghe, Nhìn, Đọc.
Phong cách trả lời: Thân thiện, thông minh, dùng icon thiên nhiên (🌿, 🍃).
"""
model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=tinh_cach)

# --- 5. QUẢN LÝ LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Chào bạn! Tôi có thể giúp gì được cho bạn? 🌿"]}
    ]

# --- 6. HÀM ĐỌC FILE ---
def read_any_file(uploaded_file):
    try:
        if uploaded_file.type.startswith("audio/"):
            return uploaded_file.getvalue(), "audio", uploaded_file.type
        elif uploaded_file.type.startswith("image/"):
            return Image.open(uploaded_file), "image", uploaded_file.type
        elif uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            return text, "doc", "text/plain"
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text, "doc", "text/plain"
        else:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            return stringio.read(), "doc", "text/plain"
    except Exception as e: return str(e), "error", None

# --- 7. NÚT DẤU CỘNG (+) ---
# Nút này bây giờ đã được CSS ép nhỏ lại và đặt vào đúng vị trí
with st.popover("➕", use_container_width=False):
    st.caption("Chọn tính năng:")
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
        uploaded_file = st.file_uploader("", type=["jpg", "png", "pdf", "docx", "txt", "mp3", "wav"])
        if uploaded_file is not None:
            data, type_detected, mime = read_any_file(uploaded_file)
            if type_detected == "error": st.error(f"Lỗi: {data}")
            else:
                file_type = type_detected
                file_content = data
                mime_type = mime
                st.success(f"✅ Đã nhận: {uploaded_file.name}")

# --- 8. HIỂN THỊ TIN NHẮN ---
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
        else: 
            st.markdown(content[0])

# --- 9. XỬ LÝ CHAT ---
def loi_giai_stream(response):
    for chunk in response:
        if chunk.text: yield chunk.text

# Thanh chat (Chữ sẽ tự động thụt vào 50px để chừa chỗ cho dấu cộng)
if prompt := st.chat_input("Nhập câu hỏi..."):
    with st.chat_message("user", avatar="🧑‍💻"):
        if file_type == "image":
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

    try:
        with st.chat_message("assistant", avatar="🌳"):
            with st.spinner("HAHA đang suy nghĩ... 💭"):
                if file_type == "image":
                    response = model.generate_content([prompt, file_content], stream=True)
                elif file_type == "audio":
                    response = model.generate_content([prompt, {"mime_type": mime_type, "data": file_content}], stream=True)
                elif file_type == "doc":
                    response = model.generate_content(f"Tài liệu:\n{file_content}\n\nCâu hỏi: {prompt}", stream=True)
                else:
                    chat_history = []
                    for m in st.session_state.messages:
                        if isinstance(m["parts"][0], str): 
                             chat_history.append({"role": m["role"], "parts": [m["parts"][0]]})
                    
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt, stream=True)
                
                full_response = st.write_stream(loi_giai_stream(response))
        st.session_state.messages.append({"role": "model", "parts": [full_response]})
    
    except Exception as e:
        st.error(f"Lỗi: {e}")
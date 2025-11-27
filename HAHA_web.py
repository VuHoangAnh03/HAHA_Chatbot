import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="HAHA Chatbot", page_icon="🌿", layout="centered")

# --- 2. PHÉP THUẬT GIAO DIỆN (CSS) ---
st.markdown("""
<style>
    /* Đổi hình nền sang ảnh Rừng cây thiên nhiên */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?q=80&w=2074&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    /* Làm khung chat input đẹp hơn */
    .stChatInputInput {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #1e3a1e !important;
    }

    /* Tiêu đề chính */
    h1 {
        color: #ffffff !important;
        text-shadow: 2px 2px 8px #000000;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
    }

    /* Chữ mô tả dưới tiêu đề */
    .stMarkdown p {
        font-weight: bold;
        color: #e0f2f1 !important;
        text-shadow: 1px 1px 2px #000000;
    }

    /* --- MỚI: TÔ MÀU CHO VÒNG XOAY SUY NGHĨ --- */
    .stSpinner > div {
        border-color: #76ff03 !important; /* Màu xanh lá mạ sáng rực */
    }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ ---
st.title("🌿 HAHA - Trợ lý AI")
st.write("Chào bạn! Tôi là HAHA, một trợ lý ảo. Chúc bạn một ngày tốt lành!")

# --- 4. CẤU HÌNH BỘ NÃO ---
genai.configure(api_key='AIzaSyCP04lF0idqbAqGjTkFAp2-NEeQhpgC_50')

tinh_cach = """
Bạn tên là HAHA.
Bạn là trợ lý AI được tạo ra bởi Hoàng Anh.
Phong cách trả lời: Thân thiện, nhẹ nhàng như thiên nhiên, yêu đời.
Khi trả lời, hãy thỉnh thoảng dùng các icon cây cối (🌿, 🌱, 🍃, 🌳).
"""

model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=tinh_cach)

# --- 5. QUẢN LÝ LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Chào Hoàng Anh, hãy cho tôi biết bạn cần gì? 🌿"]}
    ]

# --- 6. HIỂN THỊ TIN NHẮN ---
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "🧑‍💻" if role == "user" else "🌳"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["parts"][0])

# --- 7. XỬ LÝ KHI NHẬP TIN NHẮN (ĐÃ CẬP NHẬT) ---
def loi_giai_stream(response):
    for chunk in response:
        if chunk.text:
            yield chunk.text

if prompt := st.chat_input("Nhập câu hỏi vào đây..."):
    # Hiện câu hỏi người dùng
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # Gửi lên AI
    try:
        # Tạo lịch sử sạch
        history_sach = [{"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages]
        chat = model.start_chat(history=history_sach)
        
        # --- PHẦN SỬA ĐỔI: HIỆN BIỂU TƯỢNG SUY NGHĨ ---
        with st.chat_message("assistant", avatar="🌳"):
            # Lệnh st.spinner sẽ hiện vòng xoay và chữ trong lúc chờ
            with st.spinner("HAZ đang suy nghĩ... 💭"):
                # Gửi tin nhắn lên Google (quá trình này mất 1-2 giây)
                response = chat.send_message(prompt, stream=True)
                
                # Khi có phản hồi, spinner tự mất và thay bằng chữ chạy ra
                full_response = st.write_stream(loi_giai_stream(response))
        
        st.session_state.messages.append({"role": "model", "parts": [full_response]})
        
    except Exception as e:
        st.error(f"Mất kết nối với rừng xanh rồi: {e}")
import streamlit as st
from google import genai
import os

# ----------------------------------------------------
# 1. THIẾT LẬP API KEY VÀ CLIENT
# ----------------------------------------------------
try:
    API_KEY = st.secrets.GEMINI_API_KEY
except AttributeError:
    st.error("Không tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ----------------------------------------------------
# 2. PROMPT HƯỚNG DẪN
# ----------------------------------------------------
pdf_system_instruction = """
Role: Bạn là chuyên gia chuyển đổi PDF sang văn bản và bảng Markdown...
(để nguyên phần mô tả của bạn ở đây)
"""

# ----------------------------------------------------
# 3. GIAO DIỆN STREAMLIT
# ----------------------------------------------------
st.title("📄 Trợ Lý Chuyển Đổi & Phân Tích PDF (VBI)")
st.caption("Chuyển đổi PDF thành văn bản và bảng Markdown tiêu chuẩn.")

uploaded_file = st.file_uploader("Tải lên file PDF", type=["pdf"])

if st.button("Chuyển Đổi và Phân Tích Tài Liệu"):

    if uploaded_file is None:
        st.warning("Vui lòng tải lên file PDF.")
        st.stop()

    with st.spinner("Đang xử lý..."):

        gem_file = None

        try:
            st.info("Đang tải file lên Gemini...")

            # ----------------------------------------------------
            # 🔥 PHẦN QUAN TRỌNG NHẤT: LƯU PDF THÀNH FILE TẠM
            # ----------------------------------------------------
            tmp_path = f"/tmp/{uploaded_file.name}"

            # Lưu file PDF vào đĩa để Gemini API sử dụng
            with open(tmp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ----------------------------------------------------
            # 🔥 UPLOAD LÊN GEMINI — KHÔNG CÓ mime_type
            # ----------------------------------------------------
            gem_file = client.files.upload(file=tmp_path)

            # ----------------------------------------------------
            # GỌI MODEL
            # ----------------------------------------------------
            contents = [
                pdf_system_instruction,
                gem_file,
                "Hãy chuyển đổi nội dung PDF theo đúng yêu cầu định dạng."
            ]

            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=contents,
                config={"temperature": 0.0}
            )

            st.subheader("✅ Dữ liệu đã chuyển đổi")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Lỗi xử lý: {e}")

        finally:
            if gem_file is not None:
                try:
                    client.files.delete(name=gem_file.name)
                    st.success("Đã dọn file tạm trên máy chủ Gemini.")
                except:
                    st.warning("Không thể xóa file tạm trên Gemini.")

import streamlit as st
from google import genai
import sys
import os

# ----------------------------------------------------
# 1. THIẾT LẬP API KEY VÀ CLIENT
# ----------------------------------------------------
# Đọc Key từ st.secrets (Cần thiết lập trong Streamlit Cloud)
try:
    API_KEY = st.secrets.GEMINI_API_KEY
except AttributeError:
    st.error("LỖI CẤU HÌNH: Không tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")
    st.stop() 

# Khởi tạo Client
client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------
# 2. PROMPT CHUYÊN GIA PDF (Role, Task, Context, Format)
# ----------------------------------------------------
pdf_system_instruction = """
Role: Bạn là chuyên gia trong lĩnh vực bảo hiểm Phi nhân thọ, bạn nắm vững các từ ngữ chuyên môn trong ngành. Bạn cũng có chuyên môn cao khi chuyển đổi PDF sang định dạng văn bản có thể chỉnh sửa, có kinh nghiệm nhận dạng bảng (OCR) và xử lý dữ liệu bảo hiểm. 
Task: Đọc file PDF tôi gửi và chuyển toàn bộ nội dung sang dạng văn bản có thể chỉnh sửa, giữ nguyên nội dung gốc 100%, không sửa chính tả, không suy diễn, không tự căn chỉnh lại bố cục. Khi có từ viết tắt không rõ bạn cần hỏi lại để ghi đúng, không chuyển đổi sang từ đầy đủ.
Context: File có thể chứa văn bản, biểu bảng, biểu phí, hoặc hợp đồng bảo hiểm phi nhân thọ.
Format:
 Giữ nguyên bố cục bảng, tiêu đề, dòng và cột.
 Nếu bảng quá phức tạp, hãy chuyển sang định dạng Markdown (| cột 1 | cột 2 | ... |) hoặc ghi chú tên bảng rồi trình bày dữ liệu theo từng dòng có dấu “|” phân cách.
 Dùng font Unicode để có thể dán trực tiếp sang Word hoặc Excel.
 Nếu có phần bị mờ, mất chữ hoặc không đọc được rõ, bỏ trống và hỏi lại tôi trước khi điền.
Toàn bộ dữ liệu, số liệu và nội dung trong file là bí mật nội bộ, không lưu trữ, sao chép hoặc chia sẻ dưới bất kỳ hình thức nào.
"""

# ----------------------------------------------------
# 3. GIAO DIỆN STREAMLIT VÀ GỌI API
# ----------------------------------------------------

st.title("📄 Trợ Lý Chuyển Đổi & Phân Tích PDF (VBI)")
st.caption("Chuyên gia chuyển đổi tài liệu bảo hiểm sang văn bản/bảng biểu có thể chỉnh sửa.")

# --- Hộp tải file PDF ---
uploaded_file = st.file_uploader(
    "Tải lên file PDF chứa dữ liệu", 
    type=["pdf"]
)

# Nút kích hoạt Bot
if st.button("Chuyển Đổi và Phân Tích Tài Liệu"):
    
    if uploaded_file is None:
        st.warning("Vui lòng tải lên một file PDF.")
        st.stop()
    
    # Khối logic chính
    with st.spinner("Đang tải file và xử lý nội dung..."):
        
        file = None
        
        try:
            st.info("Đang tải file lên máy chủ Gemini để phân tích...")
            
            # SỬA LỖI: Khắc phục lỗi 'Unknown mime type' bằng cách chỉ định rõ loại file
            file = client.files.upload(
                file=uploaded_file,
                mime_type="application/pdf" # <-- Khai báo rõ ràng loại file
            )
            
            # 2. Xây dựng nội dung (Prompt + File)
            full_prompt_contents = [
                pdf_system_instruction, 
                file, 
                "Bây giờ, hãy chuyển đổi toàn bộ nội dung trong file PDF này sang văn bản có cấu trúc theo đúng Format quy định."
            ]
            
            # 3. Gọi API (Dùng Pro cho tác vụ phân tích tài liệu phức tạp)
            response = client.models.generate_content(
                model='gemini-2.5-pro', 
                contents=full_prompt_contents,
                config={"temperature": 0.0}
            )
            
            # 4. Hiển thị kết quả trên giao diện web
            st.subheader("✅ Dữ Liệu Đã Chuyển Đổi (Sẵn sàng để Copy/Paste)")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Lỗi Kết Nối hoặc Xử Lý File: {e}")
            st.error("Vui lòng kiểm tra API Key hoặc thử lại với file nhỏ hơn.")
            
        finally:
            # Rất quan trọng: Xóa file khỏi máy chủ sau khi dùng
            if file is not None:
                client.files.delete(name=file.name)
                st.success("Đã dọn dẹp file tạm trên máy chủ Gemini.")


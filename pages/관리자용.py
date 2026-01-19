import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

st.set_page_config(page_title="관리자 페이지", page_icon="👮")
st.title("👮 자료 학습 및 관리")

# --- [1. 문지기: 비밀번호 확인] ---
# 비밀번호를 "1234"로 설정했습니다. 원하시는 번호로 바꾸세요.
admin_password = st.text_input("🔒 관리자 비밀번호를 입력하세요", type="password")

if admin_password != "2119":  # <-- 여기 "1234"를 원하는 비밀번호로 바꾸세요!
    st.error("비밀번호가 일치하지 않습니다. 관리자만 접근 가능합니다.")
    st.stop()  # ⛔ 비밀번호 틀리면 여기서 코드 실행을 멈춤! (밑에 내용 안 보여줌)

# --- [2. API 키 확인] ---
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ 메인 페이지(Main.py)에서 API 키가 로드되지 않았습니다.")
    # (선택) 만약 관리자 페이지에서도 바로 키를 끌어오고 싶다면 Secrets를 확인
    if "GOOGLE_API_KEY" in st.secrets:
        st.session_state["api_key"] = st.secrets["GOOGLE_API_KEY"]
    else:
        st.stop()

# --- [3. 진짜 관리자 기능 시작] ---
genai.configure(api_key=st.session_state["api_key"])

# 세션 초기화
if "uploaded_files_cache" not in st.session_state:
    st.session_state["uploaded_files_cache"] = []

st.success("✅ 관리자 인증 완료! 자료를 업로드하세요.")
st.write("### 📂 학습할 문서 업로드")
st.caption("안전 매뉴얼, 제품 가이드 등 여러 개의 PDF를 한 번에 올릴 수 있습니다.")

uploaded_files = st.file_uploader("PDF 파일 선택 (다중 선택 가능)", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 선택한 파일들 학습 시작"):
    if not uploaded_files:
        st.error("파일을 선택해주세요.")
    else:
        # 기존 학습 기록 초기화 (새로 학습)
        st.session_state["uploaded_files_cache"] = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"'{file.name}' 처리 중... (Gemini 눈으로 읽는 중)")
            
            # 임시 저장 -> 구글 업로드
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(file.getvalue())
                tmp_path = tmp.name
            
            try:
                g_file = genai.upload_file(path=tmp_path)
                
                # 처리 대기
                while g_file.state.name == "PROCESSING":
                    time.sleep(1)
                    g_file = genai.get_file(g_file.name)
                
                if g_file.state.name == "ACTIVE":
                    st.session_state["uploaded_files_cache"].append(g_file)
                    st.toast(f"✅ {file.name} 학습 완료!")
                else:
                    st.error(f"❌ {file.name} 처리 실패")
                    
                os.remove(tmp_path) # 임시 파일 삭제
                
            except Exception as e:
                st.error(f"오류: {e}")
            
            # 진행률 업데이트
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        status_text.success(f"총 {len(uploaded_files)}개 문서 학습 완료! 이제 '현장사원용' 페이지로 이동하세요.")
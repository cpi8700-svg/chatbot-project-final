import streamlit as st
import google.generativeai as genai
import os
import time

st.set_page_config(page_title="현장 업무 지원", page_icon="👷")
st.title("👷 현장 업무/제품 지원")

# --- [1. API 키 불러오기] ---
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    if "GOOGLE_API_KEY" in st.secrets:
        st.session_state["api_key"] = st.secrets["GOOGLE_API_KEY"]
    else:
        st.warning("⚠️ 메인 페이지에서 API 키가 설정되지 않았습니다.")
        st.stop()

# --- [2. AI 비서 설정] ---
try:
    genai.configure(api_key=st.session_state["api_key"])
except Exception as e:
    st.error(f"API 키 설정 중 오류가 발생했습니다: {e}")
    st.stop()

# 모델 설정 (2.0 시도 -> 1.5 자동 전환)
try:
    model = genai.GenerativeModel('gemini-3-flash-preview')
except:
    model = genai.GenerativeModel('gemini-3-flash-preview')

# -----------------------------------------------------------
# 🔥 [핵심 기능] VS Code에 있는 'manual.pdf' 자동 로딩
# -----------------------------------------------------------
@st.cache_resource  # (중요) 한 번 읽으면 계속 기억하게 만듦
def load_local_manual():
    # 1. 파일 이름이 정확한지 확인하세요! (manual.pdf)
    file_path = "manual.pdf" 
    
    if os.path.exists(file_path):
        try:
            # 구글 서버로 업로드
            uploaded_file = genai.upload_file(file_path)
            
            # 파일 처리될 때까지 대기
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)
                
            return uploaded_file
        except Exception as e:
            st.error(f"매뉴얼 로딩 실패: {e}")
            return None
    else:
        return None

# 함수 실행해서 파일 가져오기
default_manual = load_local_manual()

# -----------------------------------------------------------

# --- [3. 채팅 화면 만들기] ---
if default_manual:
    st.success("✅ 'manual.pdf' 매뉴얼이 정상적으로 탑재되었습니다.")
else:
    st.info("💡 등록된 기본 매뉴얼이 없습니다. (관리자 페이지에서 추가 가능)")


# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 보여주기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 질문 입력 받기
if prompt := st.chat_input("질문 입력 (예: 시급은?)"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 학습 자료 모으기 (기본 매뉴얼 + 관리자가 추가로 올린 거)
            content_to_send = [prompt]
            
            # 1. VS Code에 박아둔 기본 매뉴얼 추가
            if default_manual:
                content_to_send.append(default_manual)
            
            # 2. 관리자 페이지에서 임시로 올린 파일 추가
            if "uploaded_files_cache" in st.session_state and st.session_state["uploaded_files_cache"]:
                content_to_send.extend(st.session_state["uploaded_files_cache"])
            
            # 자료가 하나라도 있으면 "매뉴얼 보는 중" 표시
            if len(content_to_send) > 1:
                message_placeholder.markdown("📘 매뉴얼 내용을 확인하고 있습니다...")
            
            # AI에게 질문 던지기
            response = model.generate_content(content_to_send)
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("오류가 발생했습니다.")
            st.caption(f"에러 내용: {e}")
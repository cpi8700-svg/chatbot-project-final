import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="현장 업무 지원", page_icon="👷")
st.title("👷 래딕스 현장 사원용 챗봇")

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

# 모델 설정 (최신상 2.0 시도 -> 안되면 1.5 자동 전환)
try:
    model = genai.GenerativeModel('gemini-3-flash-preview')
except:
    model = genai.GenerativeModel('gemini-3-flash-preview')

# --- [3. 채팅 화면 만들기] ---
st.info("💡 래딕스에 대해 궁금한 것을 물어보세요!")

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 보여주기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 질문 입력 받기
if prompt := st.chat_input("질문 입력 (예: 시급은?)"):
    # 1. 사용자의 질문 표시
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. AI의 답변 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 🔥 [핵심 수정] 업로드된 파일이 있는지 확인
            if "uploaded_files_cache" in st.session_state and st.session_state["uploaded_files_cache"]:
                # 파일이 있으면: [질문 + 파일들]을 묶어서 보냄 (이게 바로 교과서 펴고 답하기!)
                content_to_send = [prompt] + st.session_state["uploaded_files_cache"]
                message_placeholder.markdown("📘 매뉴얼을 검토 중입니다...")
            else:
                # 파일이 없으면: 그냥 질문만 보냄 (경고 메시지 포함)
                content_to_send = prompt
                st.caption("⚠️ 현재 학습된 문서가 없습니다. 일반 지식으로 답변합니다.")

            # AI에게 질문 던지기
            response = model.generate_content(content_to_send)
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # 답변 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("답변을 생성하는 도중 오류가 발생했습니다.")
            st.caption(f"에러 내용: {e}")
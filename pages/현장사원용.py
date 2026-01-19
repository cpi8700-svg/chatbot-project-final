import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="현장 업무 지원", page_icon="👷")
st.title("👷 현장 업무/제품 지원")

# --- [1. API 키 불러오기 (여기가 핵심!)] ---
# main.py에서 가져온 키가 없으면, 금고(Secrets)를 직접 뒤져서라도 가져옵니다.
# 아까 에러가 났던 부분이 바로 여기입니다. 이제 "GOOGLE_API_KEY"라는 이름표를 정확히 찾습니다.
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

# 챗봇 설정 (모델을 'gemini-3-flash-preview'로 변경했습니다!)
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
            # AI에게 질문 던지기
            response = model.generate_content(prompt)
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # 답변 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.caption(f"상세 에러 내용: {e}")
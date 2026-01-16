import streamlit as st
import google.generativeai as genai
import os
import time

st.set_page_config(page_title="현장 지원 챗봇", page_icon="👷")
st.title("👷 현장 업무/제품 지원")

# API 키 확인
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.error("🚨 메인 화면(Main.py)에서 API 키를 먼저 입력해주세요!")
    st.stop()

genai.configure(api_key=st.session_state["api_key"])

# --- PDF 자동 로딩 (폴더에 있는 파일 읽기) ---
PDF_FILENAME = "manual.pdf"  # 배포할 때 이 파일이 꼭 같이 올라가야 합니다!

if not os.path.exists(PDF_FILENAME):
    st.error(f"⚠️ '{PDF_FILENAME}' 파일을 찾을 수 없습니다. 프로젝트 폴더에 넣어주세요.")
    st.stop()

# 파일 업로드 (캐싱하여 반복 업로드 방지)
if "worker_doc_cache" not in st.session_state:
    with st.spinner("매뉴얼을 불러오는 중입니다..."):
        try:
            uploaded_doc = genai.upload_file(path=PDF_FILENAME)
            
            # 처리 대기
            while uploaded_doc.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_doc = genai.get_file(uploaded_doc.name)
            
            st.session_state["worker_doc_cache"] = uploaded_doc
            st.toast("매뉴얼 로딩 완료!", icon="✅")
        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.stop()

# --- 채팅 인터페이스 ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안전 수칙이나 제품에 대해 물어보세요!"}]

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("질문 입력 (예: 비상시 대처 요령은?)"):
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("🔍 매뉴얼 검색 중...")
        
        try:
            full_prompt = [
                "당신은 현장 전문가입니다. 문서를 기반으로 답변하세요.",
                "질문:", prompt,
                "참고 문서:", st.session_state["worker_doc_cache"]
            ]
            
            model = genai.GenerativeModel('gemini-3-flash-preview')
            response = model.generate_content(full_prompt)
            
            msg_placeholder.markdown(response.text)
            st.session_state["messages"].append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            msg_placeholder.error("오류가 발생했습니다.")
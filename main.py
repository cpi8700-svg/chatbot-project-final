import streamlit as st

st.set_page_config(page_title="사내 교육 챗봇 포털", page_icon="🏢")

st.title("🏢 사내 교육/안전 가이드 챗봇 (ver 1.0)")
st.write("---")
st.subheader("👋 환영합니다.")
st.write("왼쪽 사이드바에서 원하는 메뉴를 선택하세요.")

st.info("""
- **👮 관리자용:** 안전 매뉴얼, 제품 교육 자료 등을 업로드하고 학습시킵니다.
- **👷 현장사원용:** 학습된 AI에게 업무 관련 질문을 합니다.
""")

# API 키 입력 (여기서 입력하면 전체 공유)
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

with st.sidebar:
    st.header("🔑 통합 설정")
    key_input = st.text_input("Google API Key 입력", type="password", value=st.session_state["api_key"])
    if key_input:
        st.session_state["api_key"] = key_input
        st.success("API 키가 설정되었습니다!")
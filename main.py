import streamlit as st

st.set_page_config(page_title="사내 교육 챗봇 포털", page_icon="🏢")

st.title("🏢 사내 교육/안전 가이드 챗봇")
st.write("---")
st.subheader("👋 환영합니다.")
st.write("왼쪽 사이드바에서 원하는 메뉴를 선택하세요.")

st.info("""
- **👮 관리자용:** 안전 매뉴얼, 제품 교육 자료 등을 업로드하고 학습시킵니다.
- **👷 현장사원용:** 학습된 AI에게 업무 관련 질문을 합니다.
""")

# --- [수정된 부분: API 키 자동 처리 로직] ---

# 1. 세션 상태 초기화
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# 2. 서버 금고(Secrets)에서 키 확인
if "GOOGLE_API_KEY" in st.secrets:
    # 금고에 키가 있으면 자동으로 가져와서 설정
    st.session_state["api_key"] = st.secrets["AIzaSyCtg3NEEG2b2DydYcidNinikq3SUDeK5nU"]

# 3. 사이드바 설정
with st.sidebar:
    st.header("🔑 통합 설정")
    
    # 금고에 키가 있는 경우: 입력창 숨김
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("✅ 인증키가 자동 적용되었습니다.")
        st.caption("관리자가 설정한 공용 키를 사용합니다.")
        
    # 금고에 키가 없는 경우: 수동 입력창 표시 (사장님 테스트용)
    else:
        key_input = st.text_input("Google API Key 입력", type="password", value=st.session_state["api_key"])
        if key_input:
            st.session_state["api_key"] = key_input
            st.success("API 키가 설정되었습니다!")

# ---------------------------------------
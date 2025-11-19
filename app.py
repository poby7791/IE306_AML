import streamlit as st
import requests

# 🟢 중요: 4단계에서 ngrok 실행 후 이 URL을 수정해야 합니다.
API_SERVER_URL = "https://uncomically-supervictorious-yan.ngrok-free.dev/recommend-persona/" 

# --- Streamlit UI 설정 ---
st.set_page_config(page_title="리뷰 기반 추천 시스템", layout="wide")
st.title("🤖 리뷰 기반 페르소나 추천 시스템")

st.sidebar.header("👤 페르소나 생성기")
persona_free_text = st.sidebar.text_area(
    "자신에 대해 자유롭게 설명해주세요 (예: 선호 음식, 선호 분위기 등)",
    height=150
)

# --- 추천 실행 버튼 로직 ---
if st.sidebar.button("추천 받기 (Recommend)", type="primary"):
    
    # 1. '내 컴퓨터(서버)'로 API 요청 전송
    with st.spinner("페르소나 분석 및 추천 진행 중... (서버 응답 대기)"):
        try:
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.post(API_SERVER_URL, json={"free_text": persona_free_text})
            
            if response.status_code != 200:
                # 서버에서 보낸 오류 메시지 표시
                st.error(f"서버 오류 발생: {response.json().get('detail')}")
                st.text("▼ 서버가 보낸 에러 메시지 ▼")
                st.code(response.text)
            else:
                # 2. '내 컴퓨터(서버)'에서 계산된 JSON 결과 수신
                result_data = response.json()
                recs = result_data.get("recs") 
                parsed_persona = result_data.get("persona")

                # 3. 결과 출력
                st.subheader("LLM이 분석한 페르소나 (서버 결과)")
                st.json(parsed_persona)
                
                st.subheader(f"페르소나 기반 Top {len(recs)} 추천")
                for i, info in enumerate(recs):
                    st.markdown(f"---")
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(f"#{i+1}: {info.get('name', 'Unknown')}")
                        st.caption(f"{info.get('city', 'Unknown')} | {info.get('categories', 'N/A')[:100]}")
                        st.markdown("**추천 사유:**")
                        for line in info.get('explanation', '').split('\n'):
                            if line.strip():
                                st.markdown(f"> {line.strip()}")
                    with col2:
                        st.metric(label="예측 평점 (Our Score)", value=f"{info.get('predicted_score', 0):.2f} / 5.0")
                        st.metric(label="실제 평점 (Actual Rating)", value=f"{info.get('stars', 0):.1f} / 5.0")
                        
        except requests.exceptions.ConnectionError as e:
            st.error(f"서버({API_SERVER_URL}) 연결에 실패했습니다.")
            st.error("발표자 컴퓨터의 API 서버와 ngrok이 실행 중인지 확인하세요.")
        except Exception as e:
            st.error(f"예상치 못한 오류 발생: {e}")
            
else:

    st.info("왼쪽 사이드바에서 페르소나를 설명하고 '추천 받기' 버튼을 눌러주세요.")






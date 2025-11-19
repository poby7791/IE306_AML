import streamlit as st
import requests
import json

API_SERVER_URL = "https://uncomically-supervictorious-yan.ngrok-free.dev/recommend-persona/" 

# --- Streamlit UI 설정 ---
st.set_page_config(page_title="리뷰 기반 추천 시스템", layout="wide")
st.title("🤖 리뷰 기반 페르소나 추천 시스템")

st.sidebar.header("👤 페르소나 생성기")
persona_free_text = st.sidebar.text_area(
    label="자신에 대해 자유롭게 설명해주세요 (예: 리뷰 경험, 선호도)", 
    value="",
    height=150
)

# --- 추천 실행 버튼 ---
if st.sidebar.button("추천 받기 (Recommend)", type="primary"):
    
    with st.spinner("페르소나 분석 및 추천 진행 중... (서버 응답 대기)"):
        try:
            # 🟢 1. ngrok 경고 우회 헤더 추가
            headers = {"ngrok-skip-browser-warning": "true"}
            
            # 🟢 2. API 요청 전송
            response = requests.post(API_SERVER_URL, json={"free_text": persona_free_text}, headers=headers)
            
            # 🟢 3. 응답 상태 확인
            if response.status_code == 200:
                try:
                    result_data = response.json()
                    
                    # 🟢 4. 데이터 키 이름 수정 (recs, persona)
                    recs = result_data.get("recs") 
                    parsed_persona = result_data.get("persona")

                    # --- 결과 출력 ---
                    
                    # (1) 페르소나 분석 결과
                    st.subheader("LLM 페르소나 분석 (서버 결과)")
                    st.json(parsed_persona)
                    
                    # (2) 추천 리스트 (Top 5)
                    if recs:
                        st.subheader(f"페르소나 기반 Top {len(recs)} 추천")
                        for i, info in enumerate(recs):
                            st.markdown(f"---")
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.subheader(f"#{i+1}: {info.get('name', 'Unknown')}")
                                st.caption(f"{info.get('city', 'Unknown')} | {info.get('categories', 'N/A')[:100]}")
                                
                                st.markdown("**추천 사유:**")
                                # 설명 텍스트 줄바꿈 처리
                                explanation = info.get('explanation', '')
                                for line in explanation.split('\n'):
                                    if line.strip():
                                        st.markdown(f"> {line.strip()}")
                            
                            with col2:
                                # 점수 표시
                                score = info.get('predicted_score', 0.0)
                                actual = info.get('stars', 0.0)
                                st.metric(label="예측 평점 (Our Score)", value=f"{score:.2f} / 5.0")
                                st.metric(label="실제 평점 (Actual Rating)", value=f"{actual:.1f} / 5.0")
                    else:
                        st.warning("추천 결과가 없습니다.")
                        
                except json.JSONDecodeError:
                    st.error("응답 데이터 형식 오류 (JSON이 아님)")
                    st.text("▼ 서버 응답 내용 ▼")
                    st.code(response.text) # 디버깅용
            
            else:
                # 200 OK가 아닐 경우 에러 메시지 출력
                st.error(f"서버 오류 발생 (Status Code: {response.status_code})")
                st.text("▼ 에러 상세 내용 ▼")
                st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error(f"서버({API_SERVER_URL})에 연결할 수 없습니다.")
            st.info("1. 내 컴퓨터(Server)에서 'api_server.py'가 실행 중인가요?")
            st.info("2. 내 컴퓨터(Server)에서 'ngrok'이 실행 중인가요?")
            st.info("3. 위 코드의 'API_SERVER_URL'이 ngrok 주소와 일치하나요?")
            
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            
else:
    st.info("왼쪽 사이드바에서 정보를 입력하고 '추천 받기' 버튼을 눌러주세요.")



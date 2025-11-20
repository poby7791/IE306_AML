import streamlit as st
import requests
import json

API_SERVER_URL = "https://uncomically-supervictorious-yan.ngrok-free.dev/recommend-persona/" 

st.set_page_config(page_title="RecSys AI Chat", layout="centered")

# 제목
st.title("AI 맛집 추천 챗봇")
st.caption("당신의 취향이나 상황(MBTI, 기분 등)을 자유롭게 말해주세요!")

# 🟢 1. 세션 상태 초기화 (대화 기록 저장용)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "자신에 대해 자유롭게 설명해주세요 (예: 리뷰 경험, 선호도)"}
    ]

# 2. 대화 내용 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], dict) and "recs" in msg["content"]:
            data = msg["content"]
            st.success(f"**💡 분석된 페르소나:** {data['persona']['preference_text']}")
            
            for i, item in enumerate(data["recs"]):
                st.markdown(f"### #{i+1} {item['name']}")
                st.markdown(f"**⭐ 예상 평점: {item['predicted_score']:.1f}** / 5.0")
                st.caption(f"📍 {item['city']} | {item['categories']}")
                
                # 설명 박스 (클릭 없이 바로 보임)
                st.info(item['explanation'], icon="💁‍♀️")
                
                # 구분선 (마지막 아이템 제외)
                if i < len(data["recs"]) - 1:
                    st.markdown("---")
        else:
            st.markdown(msg["content"])

# 3. 사용자 입력 처리
if prompt := st.chat_input("여기에 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("취향 분석 및 맛집 검색 중..."):
            try:
                headers = {"ngrok-skip-browser-warning": "true"}
                response = requests.post(API_SERVER_URL, json={"free_text": prompt}, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        recs = result.get("recs")
                        persona = result.get("persona")

                        # (1) 페르소나 출력
                        st.success(f"**💡 분석된 페르소나:** {persona['preference_text']}")
                        
                        # (2) 추천 리스트 출력 (펼침 없이 바로 표시)
                        if recs:
                            for i, item in enumerate(recs):
                                st.markdown(f"### #{i+1} {item['name']}")
                                st.markdown(f"**⭐ 예상 평점: {item['predicted_score']:.1f}** / 5.0")
                                st.caption(f"📍 {item['city']} | {item['categories']}")
                                
                                # 설명 박스
                                st.info(item['explanation'], icon="💁‍♀️")
                                
                                if i < len(recs) - 1:
                                    st.markdown("---")
                        else:
                            st.warning("추천 결과가 없습니다.")

                        # 대화 기록 저장
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": {"persona": persona, "recs": recs}
                        })
                        
                    except json.JSONDecodeError:
                        st.error("응답 데이터 오류")
                        st.code(response.text)
                else:
                    err_msg = f"서버 오류: {response.status_code}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
            
            except Exception as e:
                err_msg = f"연결 실패: {e}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

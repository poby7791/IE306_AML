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

# 🟢 2. 기존 대화 내용 출력 (Chat Bubbles)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # 추천 결과(JSON)인 경우 예쁘게 렌더링, 텍스트면 그냥 출력
        if isinstance(msg["content"], dict) and "recs" in msg["content"]:
            data = msg["content"]
            st.markdown(f"**페르소나:** `{data['persona']['preference_text']}`")
            
            for i, item in enumerate(data["recs"]):
                with st.expander(f"#{i+1} {item['name']} (⭐ {item['predicted_score']:.1f})"):
                    st.write(f"📍 {item['city']} | {item['categories']}")
                    st.info(item['explanation'])
        else:
            st.markdown(msg["content"])

# 🟢 3. 사용자 입력 처리 (하단 채팅창)
if prompt := st.chat_input("여기에 입력하세요..."):
    # 사용자 메시지 표시 & 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 서버 호출
    with st.chat_message("assistant"):
        with st.spinner("취향 분석 및 맛집 검색 중..."):
            try:
                headers = {"ngrok-skip-browser-warning": "true"}
                response = requests.post(API_SERVER_URL, json={"free_text": prompt}, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 저장용 데이터 구성
                    response_content = {
                        "persona": result.get("persona"),
                        "recs": result.get("recs")
                    }
                    
                    # 화면 출력 (즉시)
                    st.markdown(f"**🔍 분석된 페르소나:** `{result['persona']['preference_text']}`")
                    for i, item in enumerate(result['recs']):
                        with st.expander(f"#{i+1} {item['name']} (⭐ {item['predicted_score']:.1f})"):
                            st.write(f"📍 {item['city']} | {item['categories']}")
                            st.info(item['explanation'])
                    
                    # 대화 기록에 저장
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                
                else:
                    err_msg = f"서버 오류: {response.status_code}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
            
            except Exception as e:
                err_msg = f"연결 실패: {e}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})




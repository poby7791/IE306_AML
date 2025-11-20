import streamlit as st
import requests
import json

API_SERVER_URL = "https://uncomically-supervictorious-yan.ngrok-free.dev/recommend-persona/" 

st.set_page_config(page_title="RecSys AI", layout="centered")

# 🟢 다국어 텍스트 사전
UI_TEXT = {
    "kr": {
        "title": "🤖 AI 맛집 추천 챗봇",
        "caption": "당신의 취향이나 상황(MBTI, 기분 등)을 자유롭게 말해주세요!",
        "welcome": "안녕하세요! 어떤 식당을 찾으시나요? (예: '나 우울해', 'ENFP랑 갈 곳')",
        "input_placeholder": "여기에 입력하세요...",
        "analyzing": "취향 분석 및 맛집 검색 중...",
        "persona_label": "**💡 분석된 페르소나:**",
        "rec_label": "페르소나 기반 Top 5 추천",
        "score": "예상 평점",
        "actual": "실제 평점",
        "error_server": "서버 오류",
        "error_conn": "연결 실패",
        "no_result": "추천 결과가 없습니다."
    },
    "en": {
        "title": "🤖 AI Restaurant Recommender",
        "caption": "Tell me about your preference, mood, or MBTI!",
        "welcome": "Hello! What kind of restaurant are you looking for? (e.g., 'I'm sad', 'Date spot for ENFP')",
        "input_placeholder": "Type here...",
        "analyzing": "Analyzing persona & Searching restaurants...",
        "persona_label": "**💡 Analyzed Persona:**",
        "rec_label": "Top 5 Recommendations",
        "score": "Predicted",
        "actual": "Actual",
        "error_server": "Server Error",
        "error_conn": "Connection Failed",
        "no_result": "No recommendations found."
    }
}

# 🟢 언어 선택 토글 (기본: 한국어)
with st.sidebar:
    is_english = st.toggle("English Mode", value=False)
    lang_code = "en" if is_english else "kr"
    txt = UI_TEXT[lang_code] # 현재 언어 텍스트 가져오기

st.title(txt["title"])
st.caption(txt["caption"])

# 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": txt["welcome"]}
    ]

# 기존 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], dict) and "recs" in msg["content"]:
            data = msg["content"]
            # 저장된 언어 설정 확인 (없으면 현재 설정 따름)
            msg_lang = msg.get("lang", lang_code) 
            msg_txt = UI_TEXT[msg_lang]

            st.success(f"{msg_txt['persona_label']} {data['persona']['preference_text']}")
            
            for i, item in enumerate(data["recs"]):
                st.markdown(f"### #{i+1} {item['name']}")
                st.markdown(f"**⭐ {msg_txt['score']}: {item['predicted_score']:.1f}** / 5.0")
                st.caption(f"📍 {item['city']} | {item['categories']}")
                st.info(item['explanation'], icon="💁‍♀️")
                if i < len(data["recs"]) - 1:
                    st.markdown("---")
        else:
            st.markdown(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input(txt["input_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(txt["analyzing"]):
            try:
                headers = {"ngrok-skip-browser-warning": "true"}
                response = requests.post(API_SERVER_URL, json={"free_text": prompt}, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        recs = result.get("recs")
                        persona = result.get("persona")

                        st.success(f"{txt['persona_label']} {persona['preference_text']}")
                        
                        if recs:
                            st.subheader(txt["rec_label"])
                            for i, item in enumerate(recs):
                                st.markdown(f"### #{i+1} {item['name']}")
                                st.markdown(f"**⭐ {txt['score']}: {item['predicted_score']:.1f}** / 5.0")
                                st.caption(f"📍 {item['city']} | {item['categories']}")
                                st.info(item['explanation'], icon="💁‍♀️")
                                if i < len(recs) - 1:
                                    st.markdown("---")
                        else:
                            st.warning(txt["no_result"])

                        # 대화 기록 저장 (현재 언어 코드 포함)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": {"persona": persona, "recs": recs},
                            "lang": lang_code 
                        })
                        
                    except json.JSONDecodeError:
                        st.error("JSON Error")
                else:
                    st.error(f"{txt['error_server']}: {response.status_code}")
            
            except Exception as e:
                st.error(f"{txt['error_conn']}: {e}")


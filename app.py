import streamlit as st
import requests
import json

API_SERVER_URL = "https://uncomically-supervictorious-yan.ngrok-free.dev/recommend-persona/" 

st.set_page_config(page_title="RecSys AI", layout="centered")

# --- UI 텍스트 ---
UI_TEXT = {
    "kr": {
        "title": "🤖 AI 맛집 추천 챗봇",
        "caption": "당신의 취향이나 상황(MBTI, 기분 등)을 자유롭게 말해주세요!",
        "welcome": "안녕하세요! 어떤 식당을 찾으시나요?",
        "input_placeholder": "여기에 입력하세요...",
        "analyzing": "분석 및 검색 중...",
        "persona_label": "**💡 분석된 페르소나:**",
        "score": "예상 평점",
        "model_label": "사용 모델",
        "top_k_label": "추천 개수 (Top K)"
    },
    "en": {
        "title": "🤖 AI Restaurant Recommender",
        "caption": "Tell me about your preference, mood, or MBTI!",
        "welcome": "Hello! What kind of restaurant are you looking for?",
        "input_placeholder": "Type here...",
        "analyzing": "Analyzing & Searching...",
        "persona_label": "**💡 Analyzed Persona:**",
        "score": "Predicted",
        "model_label": "Model Used",
        "top_k_label": "Top K Items"
    }
}

def reset_conversation():
    st.session_state.messages = []

# --- 1. 상단 레이아웃 (언어 & Top-K) ---
col1, col2 = st.columns([0.7, 0.3])

with col2:
    is_english = st.toggle("English", value=False, on_change=reset_conversation)
    lang_code = "en" if is_english else "kr"
    txt = UI_TEXT[lang_code]
    
    # 🟢 Top-K 선택 (1~10)
    top_k = st.selectbox(txt["top_k_label"], options=list(range(1, 11)), index=4) # 기본값 5

with col1:
    st.title(txt["title"])
    st.caption(txt["caption"])

# --- 2. 관리자 모드 (사이드바) ---
selected_model = "review" # 기본값

with st.sidebar:
    st.header("⚙️ Settings")
    # 관리자 모드 활성화 체크박스
    if st.checkbox("Admin Access"):
        password = st.text_input("Password", type="password")
        if password == "1234": # 🟢 비밀번호 설정
            st.success("Unlocked!")
            st.markdown("### Model Switching")
            model_option = st.radio(
                "Choose Model for Generation:",
                ("Review (Text Only)", "Hybrid (Text + Meta)"),
                index=0
            )
            # API로 보낼 값 설정
            if model_option == "Hybrid (Text + Meta)":
                selected_model = "hybrid"
            else:
                selected_model = "review"
        elif password:
            st.error("Wrong Password")

st.markdown("---")

# --- 3. 채팅 로직 ---
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{"role": "assistant", "content": txt["welcome"]}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], dict) and "recs" in msg["content"]:
            data = msg["content"]
            msg_lang = msg.get("lang", lang_code)
            msg_txt = UI_TEXT[msg_lang]

            # 페르소나 및 모델 정보 표시
            st.success(f"{msg_txt['persona_label']} {data['persona']['preference_text']}")
            st.caption(f"🛠 {msg_txt['model_label']}: {data.get('model_used', 'Unknown')}")

            for i, item in enumerate(data["recs"]):
                st.markdown(f"### #{i+1} {item['name']}")
                st.markdown(f"**⭐ {msg_txt['score']}: {item['predicted_score']:.1f}** / 5.0")
                st.caption(f"📍 {item['city']} | {item['categories']}")
                st.info(item['explanation'], icon="💁‍♀️")
                if i < len(data["recs"]) - 1:
                    st.markdown("---")
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input(txt["input_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(txt["analyzing"]):
            try:
                headers = {"ngrok-skip-browser-warning": "true"}
                
                # 🟢 API 요청에 top_k와 model_type 추가
                payload = {
                    "free_text": prompt,
                    "top_k": top_k,
                    "model_type": selected_model
                }
                
                response = requests.post(API_SERVER_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        recs = result.get("recs")
                        persona = result.get("persona")
                        model_used = result.get("model_used") # 사용된 모델 정보

                        st.success(f"{txt['persona_label']} {persona['preference_text']}")
                        st.caption(f"🛠 {txt['model_label']}: {model_used}") # 어떤 모델 썼는지 표시
                        
                        if recs:
                            for i, item in enumerate(recs):
                                st.markdown(f"### #{i+1} {item['name']}")
                                st.markdown(f"**⭐ {txt['score']}: {item['predicted_score']:.1f}** / 5.0")
                                st.caption(f"📍 {item['city']} | {item['categories']}")
                                st.info(item['explanation'], icon="💁‍♀️")
                                if i < len(recs) - 1:
                                    st.markdown("---")
                        else:
                            st.warning(txt["no_result"])

                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": {"persona": persona, "recs": recs, "model_used": model_used},
                            "lang": lang_code 
                        })
                        
                    except json.JSONDecodeError:
                        st.error("JSON Error")
                else:
                    st.error(f"{txt['error_server']}: {response.status_code}")
            
            except Exception as e:
                st.error(f"{txt['error_conn']}: {e}")
            
            except Exception as e:
                st.error(f"{txt['error_conn']}: {e}")



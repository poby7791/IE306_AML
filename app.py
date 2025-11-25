import streamlit as st
import requests
import json

API_SERVER_URL = "https://uncomically-supervictorious-yan.ngrok-free.dev/recommend-persona/" 

st.set_page_config(page_title="RecSys AI", layout="centered")

UI_TEXT = {
    "kr": {
        "title": "🤖 AI 맛집 추천 챗봇",
        "caption": "당신의 취향이나 상황(MBTI, 기분 등)을 자유롭게 말해주세요!",
        "welcome": "안녕하세요! 어떤 식당을 찾으시나요?",
        "input_placeholder": "여기에 입력하세요...",
        "analyzing": "분석 및 검색 중...",
        "persona_label": "**💡 분석된 페르소나:**",
        "score": "예상 평점",
        "model_label": "모델",
        "prompt_label": "설명",
        "top_k_label": "추천 개수",
        "no_result": "추천 결과가 없습니다.",
        "error_server": "서버 오류",
        "error_conn": "연결 실패"
    },
    "en": {
        "title": "🤖 AI Restaurant Recommender",
        "caption": "Tell me about your preference, mood, or MBTI!",
        "welcome": "Hello! What kind of restaurant are you looking for?",
        "input_placeholder": "Type here...",
        "analyzing": "Analyzing & Searching...",
        "persona_label": "**💡 Analyzed Persona:**",
        "score": "Predicted",
        "model_label": "Model",
        "prompt_label": "Prompt",
        "top_k_label": "Top K",
        "no_result": "No recommendations found.",
        "error_server": "Server Error",
        "error_conn": "Connection Failed"
    }
}

# 대화 초기화 함수
def reset_conversation():
    st.session_state.messages = []

# --- 1. 상단 레이아웃 (언어 & Top-K) ---
col1, col2 = st.columns([0.7, 0.3])

with col2:
    # 언어 선택 (변경 시 대화 초기화)
    is_english = st.toggle("English", value=False, on_change=reset_conversation)
    lang_code = "en" if is_english else "kr"
    txt = UI_TEXT[lang_code]
    
    # Top-K 선택 (1~10)
    top_k = st.selectbox(txt["top_k_label"], options=list(range(1, 11)), index=4) # 기본값 5

with col1:
    st.title(txt["title"])
    st.caption(txt["caption"])

# --- 2. 관리자 모드 (사이드바 - 행렬식 선택) ---
selected_model = "review"   # 기본값
selected_prompt = "persona" # 기본값

with st.sidebar:
    st.header("⚙️ Admin Settings")
    # 관리자 접근 체크박스
    if st.checkbox("Admin Access"):
        password = st.text_input("Password", type="password")
        if password == "1234": # 🟢 비밀번호
            st.success("Unlocked!")
            st.markdown("### 🎛️ Experiment Matrix")
            
            # 2열 배치로 행렬 느낌 구현
            m_col, p_col = st.columns(2)
            
            with m_col:
                st.markdown("**Model (Row)**")
                model_option = st.radio(
                    "Select Model",
                    ("Baseline (Meta)", "Review (Text)", "Hybrid (All)"),
                    index=1, # Default: Review
                    label_visibility="collapsed"
                )
            
            with p_col:
                st.markdown("**Prompt (Col)**")
                prompt_option = st.radio(
                    "Select Prompt",
                    ("Simple (Fact)", "Persona (Feel)", "Analytical (Logic)"),
                    index=1, # Default: Persona
                    label_visibility="collapsed"
                )
            
            # 선택 값을 API 파라미터로 매핑
            if "Baseline" in model_option: selected_model = "baseline"
            elif "Hybrid" in model_option: selected_model = "hybrid"
            else: selected_model = "review"
            
            if "Simple" in prompt_option: selected_prompt = "simple"
            elif "Analytical" in prompt_option: selected_prompt = "analytical"
            else: selected_prompt = "persona"
            
            st.info(f"Config: `{selected_model}` × `{selected_prompt}`")

st.markdown("---")

# --- 3. 채팅 로직 ---

# 세션 초기화 (언어 변경 반영)
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{"role": "assistant", "content": txt["welcome"]}]

# 기존 대화 내용 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # 추천 결과(JSON)인 경우 렌더링
        if isinstance(msg["content"], dict) and "recs" in msg["content"]:
            data = msg["content"]
            
            # 저장된 메시지의 언어 설정 확인 (없으면 현재 설정 따름)
            msg_lang = msg.get("lang", lang_code)
            msg_txt = UI_TEXT[msg_lang]

            # 페르소나 표시
            st.success(f"{msg_txt['persona_label']} {data['persona']['preference_text']}")
            
            # (관리자용) 사용된 모델/프롬프트 정보 표시
            st.caption(f"🛠 {msg_txt['model_label']}: {data.get('model_used')} | {msg_txt['prompt_label']}: {data.get('prompt_used')}")

            # 추천 리스트 표시
            for i, item in enumerate(data["recs"]):
                st.markdown(f"### #{i+1} {item['name']}")
                st.markdown(f"**⭐ {msg_txt['score']}: {item['predicted_score']:.1f}** / 5.0")
                st.caption(f"📍 {item['city']} | {item['categories']}")
                
                # 설명 박스 (아이콘 포함)
                st.info(item['explanation'], icon="💁‍♀️")
                
                if i < len(data["recs"]) - 1:
                    st.markdown("---")
        else:
            # 일반 텍스트 메시지
            st.markdown(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input(txt["input_placeholder"]):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 서버 요청 및 응답 처리
    with st.chat_message("assistant"):
        with st.spinner(txt["analyzing"]):
            try:
                headers = {"ngrok-skip-browser-warning": "true"}
                
                # API 요청 데이터 구성
                payload = {
                    "free_text": prompt,
                    "top_k": top_k,
                    "model_type": selected_model,
                    "prompt_type": selected_prompt
                }
                
                response = requests.post(API_SERVER_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        recs = result.get("recs")
                        persona = result.get("persona")
                        model_used = result.get("model_used")
                        prompt_used = result.get("prompt_used")

                        # 1. 페르소나 출력
                        st.success(f"{txt['persona_label']} {persona['preference_text']}")
                        st.caption(f"🛠 {txt['model_label']}: {model_used} | {txt['prompt_label']}: {prompt_used}")
                        
                        # 2. 추천 리스트 출력
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

                        # 3. 대화 기록에 저장 (현재 언어 코드 포함)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": {
                                "persona": persona, 
                                "recs": recs, 
                                "model_used": model_used, 
                                "prompt_used": prompt_used
                            },
                            "lang": lang_code 
                        })
                        
                    except json.JSONDecodeError:
                        st.error("JSON Error")
                        st.code(response.text)
                else:
                    st.error(f"{txt['error_server']}: {response.status_code}")
            
            except Exception as e:
                st.error(f"{txt['error_conn']}: {e}")






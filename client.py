import streamlit as st
import requests

#세션 정보, 웹 페이지가 수정되어도 유지되는 데이터
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "context" not in st.session_state:
    st.session_state["context"] = ""
if "choose_index" not in st.session_state:
    st.session_state["choose_index"] = False
if "uploaded_state" not in st.session_state:
    st.session_state["uploaded_state"] = False

# 사용자의 텍스트 입력을 처리
if user_input := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user", avatar="🧑‍💻").write(user_input)

    max_messages = 5 #최대 매시지 개수, system 메시지 제외

    #이미지 처리코드, LLM 모델과 채팅하지 않음
    if st.session_state["choose_index"] == True:
        st.session_state["choose_index"] = False
        messages_to_send = st.session_state["messages"][-2:]
        response = requests.post("http://3.34.139.163/choose", json={"messages": messages_to_send})
    else: #일반적인 LLM 모델 채팅
        user_messages = st.session_state["messages"][-max_messages:]
        #약의 정보를 제공하여 LLM 모델에 답변하도록 요청
        if st.session_state["context"]:
            context_message = {"role": "system", "content": f"Please respond with the following context in mind:\n{st.session_state['context']}"}
            messages_to_send = [context_message] + user_messages
        else:
            messages_to_send = user_messages
        response = requests.post("http://3.39.225.172/chatbot", json={"messages": messages_to_send})

    if response.status_code == 200:
        #서버 응답 추출
        server_response = response.json()
        assistant_response = server_response.get("response")
        context_response = server_response.get("context")
        #세션 정보 업데이트, 약의 정보를 새로 제공할 경우에만 조건문 실행
        if context_response:
            st.session_state["context"] = context_response

        st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
        st.chat_message("assistant", avatar="🤖").write(assistant_response)
    else:
        st.error(f"서버 오류: {response.status_code}")

#이미지 업로드
uploaded_file = st.file_uploader("이미지 업로드", accept_multiple_files=False, type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None and st.session_state["uploaded_state"] == False:
    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post("http://3.34.139.163/upload", files=files)
    #서버로부터 테이블 정보를 받고, 이미지에 대한 처리코드 수행 준비
    if response.status_code == 200:
        st.success("업로드 완료")
        assistant_response = response.json().get("response", "")
        st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
        st.chat_message("assistant", avatar="🤖").write(assistant_response)
        st.session_state["choose_index"] = True
        st.session_state["uploaded_state"] = True
    else:
        st.error(f"서버 오류: {response.status_code}")

if st.button("uploaded_state 초기화"):
    st.session_state["uploaded_state"] = False


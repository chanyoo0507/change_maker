import streamlit as st
import pandas as pd
import random
import requests as rq
from streamlit_lottie import st_lottie

st.title("암기도우미 1.0")

def load_animation(url):
    r = rq.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def print_animation(animation):
    if animation is not None:
        st_lottie(animation, speed=2, loop=False, width=100, height=100)

def load_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

def make_question(df, question_id):
    q_index = question_id
    question = df["질문"][q_index]
    answer_list = df["답변"]
    answer = answer_list[q_index]
    wrong_answers = df["답변"].unique().tolist()
    wrong_answers.remove(answer)
    a_index = random.randint(0,min(len(wrong_answers),4))
    answers = []
    for i in range(0,min(len(wrong_answers)+1,5)):
        if i == a_index:
            answers.append(answer)
        else:
            wrong_answer = wrong_answers[random.randint(0,len(wrong_answers)-1)]
            answers.append(wrong_answer)
            wrong_answers.remove(wrong_answer)
    return {'question':question,'answers':answers,'answer':answers[a_index]}

def select_question(df, mode):
    if mode == "랜덤":
        question_id = random.randint(0,len(df["question_id"])-1)
    elif mode == "순서 섞기":
        if st.session_state["questions_left"] == []:
            st.session_state["questions_left"] = df["question_id"].tolist()
        question_id = st.session_state["questions_left"][random.randint(0,len(st.session_state["questions_left"])-1)]
        st.session_state["questions_left"].remove(question_id)
    elif mode == "순서대로":
        question_id = st.session_state["question_now"]
        st.session_state["question_now"] += 1
        if st.session_state["question_now"] >= len(df["question_id"]):
            st.session_state["question_now"] = 0
    else:
        st.warning("문제를 배정할 수 없습니다")
        question_id = 0
    return question_id

def partial_reset():
    st.session_state["next"] = 0
    st.session_state["questions_left"] = []
    st.session_state["question_now"] = 0

st.session_state.setdefault("questions_left",[])
st.session_state.setdefault("question_now",0)
st.session_state.setdefault("next", 0)
st.session_state.setdefault("animation1", None)
st.session_state.setdefault("animation2", None)
st.session_state.setdefault("answered", False)
if st.session_state["animation1"] is None:
    st.session_state["animation1"] = load_animation("https://lottie.host/0ab1b960-3f7a-4428-8134-b3a80dcb51ee/D7JGop9mCJ.json")
if st.session_state["animation2"] is None:
    st.session_state["animation2"] = load_animation("https://lottie.host/d2070fb5-8d52-41e0-a50b-748dbea63ecf/HNnk4aRdpN.json")

if st.session_state["next"] == 0:
    st.subheader("사용법")
    st.write("1. 학습을 원하는 내용의 학습자료(교과서, 프린트물 등)의 사진을 찍거나 PDF파일을 준비하세요")
    st.write("2. 다음 프롬프트를 복사해 AI(gemini, chatGPT 등)에게 1의 자료와 함께 입력하세요")
    st.code("""다음 조건에 따라 .xlsx파일을 작성해줘
    
    --고정된 셀(각 셀 별로 변형없이 ':'이후부터 그대로 입력할 것)--
    셀A1:question_id
    셀B1:질문
    셀C1:답변
    
    --나머지 셀--
    첨부된 사진 또는 PDF 자료를 바탕으로 학습을 점검하기 위한 최대한 많은 단답형 질문을 만들어줘
    A열에는 A2:0부터 시작하여 1씩 증가하는 질문 번호를 매겨줘
    B열에는 B2부터 시작하여 만들어진 질문을 작성해줘
    C열에는 C2부터 시작하여 만들어진 질문의 답변을 작성해줘
    A,B,C열 이외에는 건드리지 말고, 빈 값이 없도록 하며, 질문 번호 작성은 마지막 질문까지 해줘
    """)

uploaded_file = st.file_uploader("3. AI가 만들어준 엑셀 파일을 업로드하세요",type=["xlsx"])
if uploaded_file is not None:
    df = load_file(uploaded_file)
    mode = st.selectbox("문제 순서를 선택해주세요",["랜덤", "순서 섞기", "순서대로"])
    next = st.button("다음으로")
    if next:
        question_id = select_question(df, mode)
        st.session_state["question"] = make_question(df, question_id)
        st.session_state["next"] = 1
        st.session_state["answered"] = False
    if st.session_state["next"] == 1:
        st.subheader("문제")
        question = st.session_state["question"]
        answer = st.radio(question['question'],question['answers'],index=None,disabled=st.session_state["answered"])
        if answer is not None:
            if not st.session_state["answered"]:
                st.session_state["answered"] = True
                st.rerun()
            if answer == question['answer']:
                print_animation(st.session_state["animation1"])
                st.markdown(":green[정답]")
                st.markdown(":green[입력한 답 : %s, 정답 : %s]"%(answer, question['answer']))
            else:
                print_animation(st.session_state["animation2"])
                st.markdown(":red[오답]")
                st.markdown(":red[입력한 답 : %s, 정답 : %s]"%(answer, question['answer']))
else:
    partial_reset()

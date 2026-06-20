import streamlit as st
import pandas as pd
import random
import requests as rq
from streamlit_lottie import st_lottie

st.title("암기도우미 1.0")

@st.cache_data
def load_animation():
    r1 = rq.get("https://lottie.host/07c18784-e513-474f-b579-2dfb46350ee8/mJoPjJKc5I.lottie")
    r2 = rq.get("https://lottie.host/b45c4f65-636e-449a-807f-d7d2ccd117ed/DfQgP8x4Wg.lottie")
    if r1.status_code != 200:
        return None
    if r2.status_code != 200:
        return None
    return r1.json()

def print_animation(animations, index):
    st_lottie(animations[index], speed=2, loop=False, width=400, height=400)

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


st.session_state.setdefault("questions_left",[])
st.session_state.setdefault("question_now",0)
st.session_state.setdefault("next", 0)
st.session_state.setdefault("animations", None)
if st.session_state["animations"] is None:
    st.session_state["animations"] = load_animation()
    rerun()

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요",type=["xlsx"])
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
        question = st.session_state["question"]
        answer = st.radio(question['question'],question['answers'],index=None,disabled=st.session_state["answered"])
        if answer is not None:
            if not st.session_state["answered"]:
                st.session_state["answered"] = True
                st.rerun()
            if answer == question['answer']:
                st.markdown(":green[정답]")
                st.markdown(":green[입력한 답 : %s, 정답 : %s]"%(answer, question['answer']))
                print_animation(st.session_state["animations"], 0)
            else:
                st.markdown(":red[오답]")
                st.markdown(":red[입력한 답 : %s, 정답 : %s]"%(answer, question['answer']))
                print_animation(st.session_state["animations"], 0)

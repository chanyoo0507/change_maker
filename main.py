import streamlit as st
import pandas as pd
import random
import requests as rq
from streamlit_lottie import st_lottie

st.title("암기도우미 1.0")

def load_animation():
    r1 = rq.get("https://lottiefiles.com/free-animation/correct-JwZs0nPkwu")
    r2 = rq.get("https://lottiefiles.com/free-animation/incorrect-NZdw5E0PZC")
    return (r1.json(),r2.json()) if r1.ok and r2.ok else None

def print_animation(animations, index):
    st_lottie(animations[index], speed=2, loop=False, width=400, height=400)

def load_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

def make_question(df):
    q_index = random.randint(0,len(df["question_id"])-1)
    question = df["질문"][q_index]
    answer_list = df["답변"]
    answer = answer_list[q_index]
    wrong_answers = df["답변"].unique().remove(answer)
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

animations = load_animation()
mode = 0
if mode == 0:
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요",type=["xlsx"])
    if uploaded_file is not None:
        df = load_file(uploaded_file)
        next = st.button("다음으로")
        if st.button:
            mode = 1
if mode == 1:
    question = make_question(df)
    answer = st.radio(question['question'],question['answers'])
    if answer == question[answer]:
        st.markdown(":green[정답]")
    else:
        st.markdown(":red[오답]")

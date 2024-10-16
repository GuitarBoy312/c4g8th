import streamlit as st
from openai import OpenAI
import random
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 세션 상태에 현재 문제 유형을 저장하기 위한 키 추가
if 'reading_quiz_current_question_type' not in st.session_state:
    st.session_state.reading_quiz_current_question_type = None

# 앱에 새로 들어갈 때마다 초기화할 변수들
if 'reading_quiz_session_init' not in st.session_state:
    st.session_state.reading_quiz_session_init = False

if not st.session_state.reading_quiz_session_init:
    st.session_state.reading_quiz_total_questions = 0
    st.session_state.reading_quiz_correct_answers = 0
    st.session_state.reading_quiz_current_question = None
    st.session_state.reading_quiz_session_init = True

# 사이드바 컨테이너 생성
if 'reading_quiz_sidebar_placeholder' not in st.session_state:
    st.session_state.reading_quiz_sidebar_placeholder = st.sidebar.empty()

# 사이드바 업데이트 함수
def update_sidebar():
    st.session_state.reading_quiz_sidebar_placeholder.empty()
    with st.session_state.reading_quiz_sidebar_placeholder.container():
        st.write("## 읽기퀴즈 점수")
        st.write(f"총 문제 수: {st.session_state.reading_quiz_total_questions}")
        st.write(f"맞춘 문제 수: {st.session_state.reading_quiz_correct_answers}")
        if st.session_state.reading_quiz_total_questions > 0:
            accuracy = int((st.session_state.reading_quiz_correct_answers / st.session_state.reading_quiz_total_questions) * 100)
            st.write(f"정확도: {accuracy}%")

# 초기 사이드바 설정
update_sidebar()

# 세션 상태에 문제 답변 여부를 추적하는 변수 추가
if 'question_answered' not in st.session_state:
    st.session_state.question_answered = False

# 세션 상태에 이전 선택을 저장하는 변수 추가
if 'previous_selection' not in st.session_state:
    st.session_state.previous_selection = None

def generate_conversation_question():
    names = ["Paul", "Jello", "Uju", "Khan", "Eric", "Bora", "Tina", "Amy"]
    occupations = [
        "I'm a police officer",
        "I'm a firefighter",
        "I'm a doctor",
        "I'm a pilot",
        "I'm a scientist",
        "I'm a farmer",
        "I'm a singer",
        "I'm a cook"
    ]

    name = random.choice(names)
    occupation = random.choice(occupations)

    dialogue = f"""
A: {name}, what do you do?
B: {occupation}.
"""

    question = f"{name}의 직업은 무엇인가요?"
    correct_answer = occupation

    # 오답 생성
    wrong_answers = random.sample([o for o in occupations if o != occupation], 3)
    options = [occupation] + wrong_answers
    random.shuffle(options)

    # 선택지를 한국어로 변환
    korean_occupations = {
        "I'm a police officer": "경찰관",
        "I'm a firefighter": "소방관",
        "I'm a doctor": "의사",
        "I'm a pilot": "비행기 조종사",
        "I'm a scientist": "과학자",
        "I'm a farmer": "농부",
        "I'm a singer": "가수",
        "I'm a cook": "요리사"
    }

    korean_options = [korean_occupations[opt] for opt in options]
    correct_answer = korean_occupations[correct_answer]

    return f"""
[영어 대화]
{dialogue}

[한국어 질문]
질문: {question}
A. {korean_options[0]}
B. {korean_options[1]}
C. {korean_options[2]}
D. {korean_options[3]}
정답: {chr(65 + korean_options.index(correct_answer))}
"""

def generate_question():
    return generate_conversation_question(), "conversation"

def parse_question_data(data):
    lines = data.split('\n')
    dialogue = ""
    question = ""
    options = []
    correct_answer = None

    dialogue_section = True
    for line in lines:
        if line.strip() == "[한국어 질문]":
            dialogue_section = False
            continue
        if dialogue_section:
            dialogue += line + "\n"
        else:
            if line.startswith("질문:"):
                question = line.replace("질문:", "").strip()
            elif line.startswith(("A.", "B.", "C.", "D.")):
                options.append(line.strip())
            elif line.startswith("정답:"):
                correct_answer = line.replace("정답:", "").strip()

    # 정답에서 알파벳만 추출
    if correct_answer:
        correct_answer = correct_answer.split('.')[0].strip()

    return dialogue.strip(), question, options, correct_answer

def get_explanation(question, dialogue, correct_answer, selected_option):
    prompt = f"""
    이 학생에게  정답이 무엇인지, 그들의 답변이 왜 틀렸는지, 학생이 방금 선택한 답변을 영어로 표현하면 무엇인지 설명해주세요.  
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.

    대화:
    {dialogue}

    문제: {question}
    정답: {correct_answer}
    학생의 선택: {selected_option}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 친절한 초등학교 영어 선생님입니다. 주어진 대화 내용만을 바탕으로 설명해야 합니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def display_question():
    dialogue, question, options, correct_answer = parse_question_data(st.session_state.reading_quiz_current_question)
    
    st.subheader("질문")
    st.write(question)

    st.divider()
    st.text(dialogue)
    st.divider()

    st.subheader("다음 중 알맞은 답을 골라보세요.")
    
    with st.form(key='answer_form'):
        selected_option = st.radio("", options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')

        if submit_button and not st.session_state.question_answered:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                st.session_state.question_answered = True
                is_correct = selected_option.split('.')[0].strip() == correct_answer
                
                if is_correct:
                    st.success("정답입니다!")
                    st.session_state.reading_quiz_correct_answers += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}입니다.")
                    explanation = get_explanation(question, dialogue, correct_answer, selected_option)
                    st.write(explanation)
                
                update_sidebar()
            else:
                st.warning("답을 선택해주세요.")
        elif st.session_state.question_answered:
            st.warning("이미 답변을 제출했습니다. 새 문제를 만들어주세요.")

def main():
    st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♀️")
    st.subheader("직업을 묻고 답하기 영어읽기 퀴즈👨‍🚀👩‍🚒")
    st.divider()

    # 확장 설명
    with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
        st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제를 만드세요.<br>
    2️⃣ 질문과 대화를 읽어보세요.<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼을 누르세요.<br>
    4️⃣ 틀렸으면 오답풀이를 확인하세요.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

    if st.session_state.reading_quiz_current_question:
        display_question()

    if st.button("새 문제 만들기"):
        with st.spinner("새로운 문제를 생성 중입니다..."):
            st.session_state.reading_quiz_current_question, st.session_state.reading_quiz_current_question_type = generate_question()
            st.session_state.question_answered = False
            st.session_state.reading_quiz_total_questions += 1  # 총 문제 수 증가
            update_sidebar()  # 사이드바 업데이트
        st.rerun()

if __name__ == "__main__":
    main()

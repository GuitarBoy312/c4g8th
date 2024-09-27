import streamlit as st
from openai import OpenAI
import random
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_essay_question():
    name = random.choice(["Paul", "Jello", "Uju", "Khan", "Eric", "Bora", "Tina", "Amy"])
    question = "What do you do?"
    answer = random.choice([
        "I'm a police officer.",
        "I'm a firefighter.",
        "I'm a doctor.",
        "I'm a pilot.",
        "I'm a scientist.",
        "I'm a farmer.",
        "I'm a singer.",
        "I'm a cook."
    ])
    question_format = "대화를 읽고 직업에 관해 묻는 질문"

    key_expression = f'''
    A: What do you do?
    B: {answer}
    '''
    prompt = f"""
    {key_expression}을 이용하여CEFR A1 수준의 영어 지문을 1문장으로 작성해주세요. 
    그 다음, 지문에 관한 간단한 질문을 한국어로 만들어주세요. 
    질문을 만들 때, 지문에 맞는 화자를 포함해서 질문해 주세요. 예를 들어, 화자가 {name}이면 "{name}이..." 로"로 시작하는 질문을 생성해 주세요.
    마지막으로, 질문에 대한 4개의 선택지를 한국어로 제공해주세요. 
    정답은 선택지 중 하나여야 합니다.
    출력 형식:
    질문: (한국어 질문)
    지문: (영어 지문)
    선택지:
    1. (선택지 1)
    2. (선택지 2)
    3. (선택지 3)
    4. (선택지 4)
    정답: (정답 번호)
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content" : "너는 EFL 환경의 초등학교 영어교사야. 초등학생에 맞는 쉬운 한국어와 영어를 사용해."},
            {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def generate_conversation_question():
     name = random.choice(["Paul", "Jello", "Uju", "Khan", "Eric", "Bora", "Tina", "Amy"])
     answer = random.choice([
        "I'm a police officer.",
        "I'm a firefighter.",
        "I'm a doctor.",
        "I'm a pilot.",
        "I'm a scientist.",
        "I'm a farmer.",
        "I'm a singer.",
        "I'm a cook."])
    question_format = "대화를 읽고 직업이 관해 묻는 질문"

    key_expression = f'''
    {name}: What do you do?
    {name}: {answer}
    '''
    prompt = f"""{key_expression}과 같은 구문을 사용 하는 CEFR A1 수준의 간단한 영어 대화를 생성해주세요. 
    영어 대화를 생성할 때, 마지막 대화 내용은 알려주지 말고대화 내용에 관한 객관식 질문으로 만들어야 합니다. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.  
    조건: 문제의 정답은 1개 입니다. 
    {name}와 {name}가 대화할 때 상대방의 이름을 부르면서 대화를 합니다. 
    영어 대화는 {name}와 {name}가 각각 1번 말하고 끝납니다.
    형식:
    [영어 대화]
    {name}: ...
    {name}: ...

    [한국어 질문]
    조건: {question_format}을 만들어야 합니다. 영어 대화에서 생성된 A와 B의 이름 중 필요한 것을 골라서 질문에 사용해야 합니다.
    질문: (한국어로 된 질문) 이 때, 선택지는 한국어로 제공됩니다.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def generate_question():
    # 랜덤으로 에세이 또는 대화 문제 생성 함수 선택
    question_type = random.choice(["essay", "conversation"])
    if question_type == "essay":
        return generate_essay_question(), "essay"
    else:
        return generate_conversation_question(), "conversation"

def parse_question_data(data):
    lines = data.split('\n')
    passage = ""
    question = ""
    options = []
    correct_answer = None

    for line in lines:
        if line.startswith("지문:"):
            passage = line.replace("지문:", "").strip()
        elif line.startswith("질문:"):
            question = line.replace("질문:", "").strip()
        elif re.match(r'^\d+\.', line):
            options.append(line.strip())
        elif line.startswith("정답:"):
            correct_answer = line.replace("정답:", "").strip()

    # 정답을 숫자로 변환
    if correct_answer:
        correct_answer = int(re.search(r'\d+', correct_answer).group())

    return passage, question, options, correct_answer

def explain_wrong_answer(passage, question, user_answer, correct_answer):
    prompt = f"""
    지문: {passage}
    질문: {question}
    사용자의 답변: {user_answer}
    정답: {correct_answer}

    위 정보를 바탕으로, 사용자가 왜 틀렸는지 간단히 설명해주세요. 그리고 정답이 왜 맞는지도 설명해주세요.
    답변은 한국어로 작성해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def main():
    # Streamlit UI

    # 메인 화면 구성
    st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♀️")
    st.subheader("직업을 묻고 답하는말에 대한 영어읽기 퀴즈👨‍🚀👩‍🚒")
    st.divider()

    #확장 설명
    with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
        st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 질문과 대화를 읽어보기<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'question_data' not in st.session_state:
        st.session_state.question_data = None
        st.session_state.question_type = None
        st.session_state.selected_option = None
        st.session_state.show_answer = False

    if st.button("새로운 문제 생성"):
        st.session_state.question_data, st.session_state.question_type = generate_question()
        st.session_state.selected_option = None
        st.session_state.show_answer = False

    if st.session_state.question_data:
        if st.session_state.question_type == "essay":
            # 에세이 문제 처리
            passage, question, options, correct_answer = parse_question_data(st.session_state.question_data)
            
            st.subheader("질문")
            st.write(question)

            st.divider()
            st.write(passage)
            st.divider()

            st.subheader("다음 중 알맞은 답을 골라보세요.")
            for i, option in enumerate(options, 1):
                if st.checkbox(option, key=f"option_{i}", value=st.session_state.selected_option == i):
                    st.session_state.selected_option = i

            if st.button("정답 확인"):
                st.session_state.show_answer = True

            if st.session_state.show_answer:
                if st.session_state.selected_option is not None:
                    if st.session_state.selected_option == correct_answer:
                        st.success("정답입니다!")
                    else:
                        st.error(f"틀렸습니다. 정답은 {correct_answer}번입니다.")
                        explanation = explain_wrong_answer(
                            passage, 
                            question, 
                            options[st.session_state.selected_option - 1], 
                            options[correct_answer - 1]
                        )
                        st.write("오답 설명:", explanation)
                else:
                    st.warning("선택지를 선택해주세요.")

        else:
            # 대화 문제 처리
            dialogue, question_part = st.session_state.question_data.split("[한국어 질문]")
            
            question_lines = question_part.strip().split("\n")
            question = question_lines[0].replace("질문:", "").strip() if question_lines else ""
            options = question_lines[1:5] if len(question_lines) > 1 else []
            correct_answer = ""
            
            for line in question_lines:
                if line.startswith("정답:"):
                    correct_answer = line.replace("정답:", "").strip()
                    break

            st.markdown("### 질문")
            st.write(question)
            
            st.markdown("### 대화")
            st.text(dialogue.strip())
              
            with st.form(key='answer_form'):
                selected_option = st.radio("정답을 선택하세요:", options, index=None)
                submit_button = st.form_submit_button(label='정답 확인')

                if submit_button:
                    if selected_option == correct_answer:
                        st.success("정답입니다!")
                    else:
                        st.error(f"틀렸습니다. 정답은 {correct_answer}입니다.")

if __name__ == "__main__":
    main()

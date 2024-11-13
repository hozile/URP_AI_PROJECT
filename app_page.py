import streamlit as st
from study_content_ai_analyzer import db

def display_app_page():
    # Function to display the quiz and handle form submission
    def display_quiz():
        # Retrieve the difficulty from session state
        difficulty = st.session_state.get("difficulty", default="Easy")  # Default to 'Easy' if not set
        st.subheader(f"Difficulty Selected: {difficulty}")
        print(f"difficulty selected:{difficulty}")
        selected_file_name = st.session_state.get("filename_selected")

        questions_data = db.get_question(difficulty,selected_file_name)
        answers = {}

        # Apply custom CSS for colors and font size
        st.markdown("""
        <style>
            .question { font-size: 20px; color: #1a73e8; font-weight: bold; margin-bottom: 10px; }
            .option { font-size: 16px; color: #e8eaed; background-color: #303134; padding: 8px; border-radius: 6px; margin-left: 20px; margin-bottom: 10px; }
            .option:hover { background-color: #5f6368; color: #ffffff; }
            .result { font-size: 18px; font-weight: bold; color: #0066cc; }
        </style>
        """, unsafe_allow_html=True)

        st.title("Answer the AI-Generated Questions Below 📝")
        for idx, item in enumerate(questions_data, start=1):  # start=1 will make the question numbers start from 1
                question_text = item['Question']
                options = item['Option']

                # Display the question number and text using idx as the question number
                st.markdown(f"**Q{idx}: {question_text}**")

                # Display the options as radio buttons
                user_answer = st.radio(
                    f"Choose your answer for Question {idx}",
                    options,
                    key=f"q{idx}",
                    index=None
                )

                # Store the user's answer for later evaluation if needed
                answers[f"q{idx}"] = user_answer

        # Button to submit the quiz
        if st.button("Submit Quiz"):
            score = calculate_score(answers, questions_data)
            # Store score and answers in session state and mark as submitted
            st.session_state["submitted"] = True
            st.session_state["score"] = score
            st.session_state["answers"] = answers
            st.session_state["questions"] = questions_data

    # Function to display the results page with optimized appearance
    def display_results():
        score = st.session_state["score"]
        user_answers = st.session_state["answers"]
        questions = st.session_state["questions"]

        # Determine pass or fail
        if score >= len(questions) // 2:
            # Pass - display score in green
            st.markdown(
                f"<h3 style='color:green;'>Final Result: {score}/{len(questions)}</h3>",
                unsafe_allow_html=True
            )
        else:
            # Fail - display score in red
            st.markdown(
                f"<h3 style='color:red;'>Final Result: {score}/{len(questions)}</h3>",
                unsafe_allow_html=True
            )
        
        # Loop through each question to display answers and indicate correct/incorrect responses
        for idx, question in enumerate(questions, start=1):  # Use enumerate to start question numbers from 1
            question_text = question["Question"]
            correct_answer = question["Answer"]
            user_answer = user_answers.get(f"q{idx}")  # Use idx for correct referencing

            # Display the question number and text using idx as the question number
            st.markdown(f"<p class='question'><strong>Q{idx}: {question_text}</strong></p>", unsafe_allow_html=True)

            # Display each option, highlighting the user's answer and indicating correctness
            for option in question["Option"]:
                if option == user_answer:
                    if option == correct_answer:
                        color_class = "correct"
                        db.disable_question(question["No_Question "])  # Disable question if answered correctly
                    else:
                        color_class = "incorrect"
                    st.markdown(f"<p class='option {color_class}'>{option} (Your Answer)</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p class='option'>{option}</p>", unsafe_allow_html=True)

            # Show the correct answer explicitly if the user was incorrect
            if user_answer != correct_answer:
                st.markdown(f"<p class='correct-answer'>Correct Answer: {correct_answer}</p>", unsafe_allow_html=True)

        if st.button("Restart"):
            st.session_state.question_generated = "Second Generated"
            st.session_state.page = 'difficulty'

            
    # CSS styling for improved UI with green/red color coding
    st.markdown("""
    <style>
        .question { font-size: 20px; color: #1a73e8; font-weight: bold; margin-bottom: 10px; }
        .option { font-size: 16px; color: #e8eaed; background-color: #303134; padding: 8px; border-radius: 6px; margin-left: 20px; margin-bottom: 10px; }
        .correct { background-color: #d4edda; color: #155724; font-weight: bold; }  /* Green for correct answers */
        .incorrect { background-color: #f8d7da; color: #721c24; font-weight: bold; }  /* Red for incorrect answers */
        .correct-answer { color: #28a745; font-weight: bold; margin-top: 5px; }
        .result { font-size: 18px; font-weight: bold; color: #0066cc; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # Function to calculate the score
    def calculate_score(user_answers, questions):
        score = 0
        for index in range(len(questions)):
            correct_answer = questions[index]['Answer']
            print(f"user_answers:{user_answers}")
            print(f"questions:{questions}")

            # Loop through each question-answer pair and print them
            for question, user_answer in user_answers.items():
                print(f"{question}: {user_answer}")
                # Check if the user's answer matches the correct answer
                if user_answer == correct_answer:
                    score += 1
                else:
                    print("Not correct")
                print(f"result_score:{score}")

        return score

    # Initialize session state for tracking submission
    if "submitted" not in st.session_state:
        st.session_state["submitted"] = False

    # Main app logic: show quiz or results page based on submission status
    if st.session_state["submitted"]:
        display_results()  # Show results page after submission
    else:
        display_quiz()  # Show quiz initially

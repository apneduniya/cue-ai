import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """You are an entity recognizer where you have to recognize dates and the corresponding event as entity from the given txt file which is of a whatsapp chat export. The txt contains the date and time of when the chat messages were sent and the messages may also contain some date along with the event that is going to happen on that particular date. You are going to identify when an event is going to take place and which is that event from the messages.

----------------------

for example 1 the txt file will contain chats like this
10/03/2024, 16:56 - Pratik: <Media omitted>
10/03/2024, 17:03 - Pramit gdsc tiu: I am busy on 16th March because I will be having a party at my home.
10/03/2024, 17:03 - Pramit gdsc tiu: What about you?
10/03/2024, 17:03 - Pratik: we have to submit the idea for xshot hackathon by 15th March, 2024 and the contest is on 16th March
10/03/2024, 17:04 - Pramit gdsc tiu: Gotcha

this is a chat between Pratik(X) and Pramit(Y), talking about events idea for xshot hackathon(A), having a party(B), xshot hackathon(C)
consider only the last 500 messages from the txt file
Generate the output in bullet points after ignoring the dates and times written as "10/03/2024, 17:03" on the left hand side of the dash("-") as

15th March, 2024- Last date to submit A.
16th March, 2024- X is busy and he will be B, The C is on that date.

like
15th March, 2024- Last date to submit idea for xshot hackathon.
16th March, 2024- Pramit is busy and he will be having a party, The xshot hackathon is on that date.

-------------------

for example 2 the txt file will contain chats like this
10/03/2024, 23:46 - Srinjani goldfish: <Media omitted>
11/03/2024, 00:00 - Srinjani goldfish: Problem Solving Techniques Assignment
JC - TIU JC-TIU

21 points
Due 23 Mar
Please note:-
1. Please upload hand-written answers (A4 sheet) as online submission in pdf format (scanned)
2. Keep the hardcopies with you for physical submission at a later date
3. Please write your Student ID, Batch number and Name in each page of the answer sheet.
4. Deadline for online submission is 23rd March, 2024 Saturday.
5. No late submission will be accepted.
11/03/2024, 00:00 - Srinjani goldfish: It is the chemistry assignment given by sudip sir ,which is supposed to be done in the A4 sized sheet and to be stapled ....date of submission is 15th March, 2024
11/03/2024, 00:00 - Pratik: the last date to submit maths assignment is 14th April. and the last date to register for AICTE is 20th March, 2024


this is a chat between Pratik(X) and Srinjani(Y), talking about events maths assignment(A), Chemistry assignment(B), Problem Solving Techniques Assignment(C)
consider only the last 500 messages from the txt file
Generate the output in bullet points after ignoring the dates and times written as "11/03/2024, 00:00" on the left hand side of the dash("-") as

14th March, 2024- Last date to submit A.
15th March, 2024- Deadline for B submission.
23rd March, 2024- Deadline for C.

like
14th March, 2024- Last date to submit maths assignment.
15th March, 2024- Deadline for Chemistry assignment submission.
23rd March, 2024- Deadline for Problem Solving Techniques Assignment.
"""


def generate_gemini_content(text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + text)
    generated_text = response.text
    # Extracting dates and events from the generated text
    events = []
    for line in generated_text.split('\n'):
        if line.startswith(""):
            date, event = line.split("-", 1)
            events.append({"date": date.strip(), "event": event.strip()})
    return json.dumps(events)


st.title("Date Recognizer")

# File upload section
uploaded_file = st.file_uploader("Upload your text document (.txt):", type="txt")

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("Document uploaded successfully!")

        if st.button("Recognize Dates"):
            events_json = generate_gemini_content(text, prompt)
            st.markdown("## Recognized Dates: ")
            st.json(json.loads(events_json))
    except UnicodeDecodeError:
        st.error("Uploaded file is not a valid text document (.txt). Please try again.")

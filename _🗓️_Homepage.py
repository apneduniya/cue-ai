import streamlit as st
import os, sys, json
import google.generativeai as genai
from dotenv import load_dotenv
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from datetime import datetime

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 


prompt = """You are an entity recognizer where you have to recognize dates and the corresponding event as entity from the given txt file which is of a whatsapp chat export. The txt contains the date and time of when the chat messages were sent and the messages may also contain some date along with the event that is going to happen on that particular date. You are going to identify when an event is going to take place and which is that event from the messages.

----------------------

RULES TO BE FOLLOWED:
1. Output should also write the year along with the date
2. Write the event briefly
3. Your response should be in a VALID JSON in the said format.
4. Don't hallucinate.

----------------------

For example 1 (the txt file will contain chats like this):

PROMPT: 10/03/2024, 16:56 - Pratik: <Media omitted>
10/03/2024, 17:03 - Pramit gdsc tiu: I am busy on 16th March because I will be having a party at my home.
10/03/2024, 17:03 - Pramit gdsc tiu: What about you?
10/03/2024, 17:03 - Pratik: we have to submit the idea for xshot hackathon by 15th March, 2024 and the contest is on 16th March
10/03/2024, 17:04 - Pramit gdsc tiu: Gotcha


RESPONSE: 

[
{{
"event_title": "Last date to submit idea for Xshot hackathon",
"event_date": "15",
"event_month": "3",
"event_year": "2024",
}},
{{
"event_title": "Xshot hackathon",
"event_date": "16",
"event_month": "3",
"event_year": "2024",
}}
]
-------------------

For example 2 (the txt file will contain chats like this):
PROMPT: 10/03/2024, 23:46 - Srinjani goldfish: <Media omitted>
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

RESPONSE:

[
{{
"event_title": "Last date to submit maths assignment",
"event_date": "14",
"event_month": "3",
"event_year": "2024",
}},
{{
"event_title": "Deadline for chemistry assignment submission",
"event_date": "15",
"event_month": "3",
"event_year": "2024",
}},
{{
"event_title": "Deadline for Problem Solving Techniques Assignment",
"event_date": "24",
"event_month": "3",
"event_year": "2024",
}}
]

--------------------------

Give me response in JSON format like:
[
{{
"event_title": "",
"event_date": "",
"event_month": "",
"event_year": "",
}}
]

"""


def generate_gemini_content(text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + text)
    generated_text = response.text

    return generated_text

def save_event_in_google_calendar(event_name: str, event_date: int, event_month: int, event_year: int):
    calendar = GoogleCalendar(credentials_path=f"{script_directory}/.credentials/credentials.json")

    event = Event(
        event_name,
        start=datetime(event_year, event_month, event_date, 0, 0),
        minutes_before_popup_reminder=15
    )

    calendar.add_event(event)

st.set_page_config(
    page_title="ICue App",
    page_icon="🗓️",
)
st.title("ICue Date and Events Recognizer")

# File upload section
uploaded_file = st.file_uploader("Upload your text document (.txt):", type="txt")

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("Chats uploaded successfully!")

        if st.button("Recognize Events"):
            with st.spinner("Recognizing the events...."):
                events_json = generate_gemini_content(text, prompt)
            st.markdown("## Recognized Dates: ")
            for event in json.loads(events_json):
                st.write(event["event_title"],"-",event["event_date"],"/",event["event_month"],"/",event["event_year"])
                # Saving events in google calender
            with st.spinner("Saving events in Google calendar...."):
                for event in json.loads(events_json):
                    save_event_in_google_calendar(event_name=event["event_title"], event_date=int(event["event_date"]), event_month=int(event["event_month"]), event_year=int(event["event_year"]))
            st.markdown("Events have been saved to your [Google Calendar](https://calendar.google.com)")
            
            #st.markdown("## Recognized Dates: ")
            #st.json(json.loads(events_json))


    except UnicodeDecodeError:
        st.error("Uploaded file is not a valid text document (.txt). Please try again.")

footer="""<style>

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #451571;
color: #FFFFFF;
text-align: center;
}
</style>
<div class="footer">
<p>© 2024 ICue-AI. All Rights Reserved</p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

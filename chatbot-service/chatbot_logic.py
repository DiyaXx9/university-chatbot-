def get_response(message: str) -> str:
    """
    Simple rule-based NLP logic for the university chatbot.
    Later, you can replace this with machine learning or LLM-based responses.
    """
    msg = message.lower().strip()

    if "course" in msg:
        return "You can find all course details here: https://university.edu/courses"

    elif "exam" in msg:
        return "You can view the exam schedule here: https://university.edu/exams"

    elif "timetable" in msg:
        return "Your class timetable is available at: https://university.edu/timetable"

    elif "fee" in msg or "fees" in msg:
        return "Fee details are available here: https://university.edu/fees"

    elif "library" in msg:
        return "Library information: https://university.edu/library"

    elif "hostel" in msg:
        return "Hostel details can be found at: https://university.edu/hostel"

    elif "admission" in msg:
        return "Admission guidelines are available here: https://university.edu/admissions"

    else:
        return (
            "Sorry, I didn't understand your query. "
            "You can ask about courses, exams, timetable, hostel, fees, or library."
        )

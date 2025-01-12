import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Define categories and words
WORD_CATEGORIES = {
    "Emotions": ["Happy", "Sad", "Angry", "Peaceful", "Excited"],
    "Nature": ["Ocean", "Forest", "Mountain", "Desert", "Sky"],
    "Temperature": ["Hot", "Cold", "Warm", "Freezing", "Mild"],
    "Abstract": ["Freedom", "Love", "Success", "Power", "Wisdom"],
}


def initialize_session_state():
    if "current_category" not in st.session_state:
        st.session_state.current_category = list(WORD_CATEGORIES.keys())[0]
    if "current_word_index" not in st.session_state:
        st.session_state.current_word_index = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "test_complete" not in st.session_state:
        st.session_state.test_complete = False


def save_responses(responses):
    # Create a directory if it doesn't exist
    if not os.path.exists("responses"):
        os.makedirs("responses")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"responses/color_test_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(responses, f)

    return filename


def load_previous_responses():
    if not os.path.exists("responses"):
        return None

    files = os.listdir("responses")
    if not files:
        return None

    latest_file = max(
        files, key=lambda x: os.path.getctime(os.path.join("responses", x))
    )
    with open(os.path.join("responses", latest_file), "r") as f:
        return json.load(f)


def main():
    st.title("Color Perception Test")
    initialize_session_state()

    if not st.session_state.test_complete:
        current_category = st.session_state.current_category
        current_words = WORD_CATEGORIES[current_category]

        if st.session_state.current_word_index < len(current_words):
            current_word = current_words[st.session_state.current_word_index]

            st.subheader(f"Category: {current_category}")
            st.header(current_word)
            st.write("Select the color you associate with this word:")

            color = st.color_picker("Pick a color", "#000000")

            if st.button("Next"):
                # Save response
                if current_category not in st.session_state.responses:
                    st.session_state.responses[current_category] = {}
                st.session_state.responses[current_category][current_word] = color

                # Move to next word
                st.session_state.current_word_index += 1
                if st.session_state.current_word_index >= len(current_words):
                    # Move to next category
                    categories = list(WORD_CATEGORIES.keys())
                    current_category_index = categories.index(current_category)

                    if current_category_index < len(categories) - 1:
                        st.session_state.current_category = categories[
                            current_category_index + 1
                        ]
                        st.session_state.current_word_index = 0
                    else:
                        st.session_state.test_complete = True

                st.rerun()

    else:
        st.success("Test completed!")
        filename = save_responses(st.session_state.responses)
        st.write(f"Your responses have been saved to: {filename}")

        # Compare with previous responses if available
        previous_responses = load_previous_responses()
        if previous_responses and previous_responses != st.session_state.responses:
            st.subheader("Comparison with Previous Test")

            for category in WORD_CATEGORIES:
                st.write(f"\n**{category}**")
                for word in WORD_CATEGORIES[category]:
                    current_color = st.session_state.responses.get(category, {}).get(
                        word
                    )
                    previous_color = previous_responses.get(category, {}).get(word)

                    if current_color and previous_color:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"{word} (Current):")
                            st.color_picker(
                                "",
                                current_color,
                                disabled=True,
                                key=f"current_{category}_{word}",
                            )
                        with col2:
                            st.write(f"{word} (Previous):")
                            st.color_picker(
                                "",
                                previous_color,
                                disabled=True,
                                key=f"previous_{category}_{word}",
                            )

        if st.button("Start New Test"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()

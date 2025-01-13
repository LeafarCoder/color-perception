import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io

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
    if "previous_responses" not in st.session_state:
        st.session_state.previous_responses = None


def get_download_link(responses):
    """Generate a download link for the responses"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"color_test_{timestamp}.json"

    json_str = json.dumps(responses, indent=2)
    bytes_data = json_str.encode()

    return filename, bytes_data


def load_previous_responses(uploaded_file):
    """Load responses from an uploaded file"""
    if uploaded_file is not None:
        try:
            return json.loads(uploaded_file.getvalue().decode())
        except:
            st.error("Error loading the file. Please make sure it's a valid JSON file.")
    return None


def display_color_box(color):
    """Display a large color box with the selected color"""
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            width: 200px;
            height: 200px;
            border-radius: 10px;
            border: 2px solid #ccc;
            margin: 10px 0;
        "></div>
        """,
        unsafe_allow_html=True,
    )


def get_previous_word_and_category():
    """Get the previous word and category based on current position"""
    current_category = st.session_state.current_category
    current_word_index = st.session_state.current_word_index
    categories = list(WORD_CATEGORIES.keys())
    current_category_index = categories.index(current_category)

    if current_word_index > 0:
        return current_category, current_word_index - 1
    elif current_category_index > 0:
        prev_category = categories[current_category_index - 1]
        return prev_category, len(WORD_CATEGORIES[prev_category]) - 1
    else:
        return None, None


def main():
    st.title("Color Perception Test")
    initialize_session_state()

    # Add file uploader for previous results
    with st.sidebar:
        st.header("Previous Results")
        uploaded_file = st.file_uploader("Upload previous test results", type=["json"])
        if uploaded_file:
            st.session_state.previous_responses = load_previous_responses(uploaded_file)

    if not st.session_state.test_complete:
        current_category = st.session_state.current_category
        current_words = WORD_CATEGORIES[current_category]

        if st.session_state.current_word_index < len(current_words):
            current_word = current_words[st.session_state.current_word_index]

            # Progress indicator
            total_words = sum(len(words) for words in WORD_CATEGORIES.values())
            current_total_index = (
                sum(
                    len(WORD_CATEGORIES[cat])
                    for cat in WORD_CATEGORIES.keys()
                    if cat < current_category
                )
                + st.session_state.current_word_index
            )
            st.progress(current_total_index / total_words)

            st.subheader(f"Category: {current_category}")
            st.header(current_word)
            st.write("Select the color you associate with this word:")

            # Get previously selected color for this word if it exists
            previous_color = st.session_state.responses.get(current_category, {}).get(
                current_word, "#000000"
            )
            color = st.color_picker("Pick a color", previous_color)

            # Display large color box
            display_color_box(color)

            # Navigation buttons in columns
            col1, col2 = st.columns(2)
            with col1:
                # Only show "Previous" button if we're not at the first word
                prev_category, prev_word_index = get_previous_word_and_category()
                if prev_category is not None:
                    if st.button("← Previous"):
                        st.session_state.current_category = prev_category
                        st.session_state.current_word_index = prev_word_index
                        st.rerun()

            with col2:
                if st.button("Next →"):
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

        # Create download button for current results
        filename, bytes_data = get_download_link(st.session_state.responses)
        st.download_button(
            label="Download Your Results",
            data=bytes_data,
            file_name=filename,
            mime="application/json",
        )

        # Compare with previous responses if available
        if st.session_state.previous_responses:
            st.subheader("Comparison with Previous Test")

            for category in WORD_CATEGORIES:
                st.write(f"\n**{category}**")
                for word in WORD_CATEGORIES[category]:
                    current_color = st.session_state.responses.get(category, {}).get(
                        word
                    )
                    previous_color = st.session_state.previous_responses.get(
                        category, {}
                    ).get(word)

                    if current_color and previous_color:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"{word} (Current):")
                            display_color_box(current_color)
                        with col2:
                            st.write(f"{word} (Previous):")
                            display_color_box(previous_color)

        if st.button("Start New Test"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()

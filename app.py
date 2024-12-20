import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import os
from google import genai

# Load environment variables from .env file
load_dotenv()

# Streamlit app title
st.title("AI-Homework-Helper")

# Input for the Gemini API key
google_api_key = st.text_input("Enter your Gemini API Key", type="password")
if not google_api_key:
    st.warning("Please enter your Gemini API key to proceed.")
    st.stop()

# Initialize the genai client
try:
    client = genai.Client(api_key=google_api_key)
except Exception as e:
    st.error(f"Error initializing the GenAI client: {e}")
    st.stop()

# Checkbox to enable camera input
enable_camera = st.checkbox("Enable camera")
img_file_buffer_camera = st.camera_input("Take a picture", disabled=not enable_camera)

# Drag-and-drop image uploader
st.markdown("### Or upload an image using drag-and-drop:")
img_file_buffer_upload = st.file_uploader("Drag and drop an image here", type=["png", "jpg", "jpeg"])

# Text input for the query
query = st.text_input("Ask a Question")

# Handle the image input
img = None
if img_file_buffer_camera:
    try:
        img = Image.open(img_file_buffer_camera).resize((256, 256))
    except Exception as e:
        st.error(f"Error loading image from camera: {e}")
elif img_file_buffer_upload:
    try:
        img = Image.open(img_file_buffer_upload).resize((256, 256))
    except Exception as e:
        st.error(f"Error loading uploaded image: {e}")

# Load the selected model
model_name = "gemini-2.0-flash-thinking-exp"  # Example model name

# Initialize session state for response if not already set
if "response" not in st.session_state:
    st.session_state.response = None
    st.session_state.approach = None
    st.session_state.answer = None

# Button to generate the response
generate_response = st.button("Generate Response")

# Generate response using the genai client when the button is clicked
if generate_response:
    if not query and img is None:
        st.warning("Please provide a query or an image before generating a response.")
    else:
        contents = []
        if query:
            contents.append(query)
        if img:
            # Convert image to bytes for API compatibility if needed
            contents.append(img)

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )

            # Extract response parts
            st.session_state.approach = response.candidates[0].content.parts[0].text
            st.session_state.answer = response.candidates[0].content.parts[1].text
        except Exception as e:
            st.error(f"Error generating response: {e}")

# Display the response if available
if st.session_state.approach:
    st.subheader("Approach")
    st.write(st.session_state.approach)

    show_answer = st.checkbox("Show Answer")
    if show_answer and st.session_state.answer:
        st.subheader("Answer")
        st.write(st.session_state.answer)

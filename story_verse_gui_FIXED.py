import streamlit as st

# 🔧 1. Custom Styling – Apply before all logic
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stTextArea, .stTextInput {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🎬 2. Hero Banner
st.markdown(
    """
    <div style="background-color:#0E1117;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">🎬 STORY-VERSE: Co-Write Your Next Hit</h1>
        <p style="color:#CCCCCC;text-align:center;">Powered by Google Gemini + Imagen APIs</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 📂 3. Sidebar Image & Settings
st.sidebar.title("🎛️ Settings")
st.sidebar.image("https://placehold.co/250x150?text=StoryVerse", use_column_width=True)
genre = st.sidebar.selectbox("Genre", ["Sci-Fi", "Fantasy", "Drama", "Thriller"])

# ✍️ 4. Input Area
st.subheader("✍️ Your Prompt or Story Segment")
user_input = st.text_area("Write the beginning of your story or a prompt for the AI to continue:")

# 🧠 5. Generate AI Output (Mocked for Presentation)
if st.button("✨ Generate AI Suggestions"):
    if user_input.strip():
        st.markdown("### 💡 AI Suggestions (Sample)")
        st.markdown("- **Bonus:** In a world where dreams are regulated, one man discovers he’s been living a lie.")
        st.markdown("- **Bonus:** After a global blackout, humanity learns it was never alone.")
        st.markdown("- **Bonus:** The moon is no longer Earth's satellite — it's watching.")
    else:
        st.warning("Please enter some story input to begin.")

# 📜 6. Display Story Area
st.markdown("---")
st.subheader("📖 Story Progress")
st.text_area("Here's your story so far:", value=user_input, height=200)

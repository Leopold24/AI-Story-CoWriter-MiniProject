### STORY-VERSE GUI V13 - 2025-06-27 - Replayable Endings & API Integration ###

# --- Version Indicator (for debugging) ---
print("Running Streamlit GUI Version: 2025-06-27-V13 - CONFIRMED LOADED")
import time
time.sleep(1) # Small delay to ensure the print statement appears before other Streamlit output


import streamlit as st
import re
import asyncio
import random
import json
import httpx # For making asynchronous HTTP requests from Python

# --- API Configuration ---
# IMPORTANT: The API key should NOT be hardcoded in production.
# For local testing, you can uncomment and set your API_KEY here.
# For better security, consider using environment variables (e.g., os.getenv("GEMINI_API_KEY")).
# If running this code inside the Google AI Studio Canvas environment,
# the '__api_key' global variable will be automatically provided, and this 'API_KEY'
# variable will be ignored.
API_KEY = "" # Leave empty if you rely on Canvas's __api_key or environment variables

# --- Global Data Definitions (from ai-story-co-writer-python-local-exec) ---
MOOD_SCENES = {
    "Fantasy": [
        "🌌✨🌲🌲🏰🌲🌲✨🌌",
        "🐉⚔️🛡️🔮📖✨",
        "🧚‍♀️🌿🍄🦌 enchanted forest🦉🏞️"
    ],
    "Sci-Fi": [
        "👽 SCI-FI MODE 👽",
        "🌌🚀🪐🛰️⚡🌠🧬",
        "🤖 Cyberpunk City 🏙️🌃🔌"
    ],
    "Mystery": [
        "🕵️‍♂️ WHO DUN IT? 🔎",
        " dimly lit alleyway 🌃🌧️🚶‍♀️",
        "❓❓👁️‍🗨️💡🕵️‍♀️"
    ],
    "Horror": [
        "💀 GHOULISH GRIN 👹",
        "🏚️🕸️🕯️🔪🩸",
        "🎃👻💀🏚️ Beware the night 🦇"
    ],
    "Romance": [
        "💖 LOVESTRUCK ❤️‍🔥",
        "💞💌🌹🥂✨",
        "🌅👩‍❤️‍👨🌆✨ Sweet whispers 💖"
    ],
    "Adventure": [
        "🗺️ EXPLORE! 🧭",
        "🏞️⛰️🛶🧭丛林深处🏕️"
    ]
}

FORMAT_POSTER_MOODS = {
    "Novel": "📘🖋️ *Classic 20th-century novel cover*: muted tones, silhouette of main character, dramatic font.",
    "Short Story": "📚📰 *Vintage magazine vibe*: Pulp fiction colors, 2D cover blurbs, exaggerated drama.",
    "Television Script": "📺📝 *1980s Title Card*: Big bold serif font, freeze-frame energy, theme song feel.",
    "Screenplay": "🎬📃 *Black Courier on White*: Scene header, centered title, “FADE IN:” on first line.",
    "Play": "🎭🕯️ *Broadway Poster*: Spotlight, single figure on stage, marquee font, deep reds and golds."
}

STORY_FORMATS = [
    "Novel", "Short Story", "Screenplay", "Television Script", "Play"
]

STORY_ERAS = [
    "1920s Modernist",
    "1940s Noir",
    "1950s Stage Drama",
    "1960s Beatnik",
    "1980s Television",
    "1990s Speculative Fiction"
]

QUIZ_QUESTIONS = [ # From ai-story-co-writer-python-local-exec
    {
        "question": "Which Python keyword is used to define a function?",
        "options": ["class", "func", "def", "method"],
        "correct_answer_index": 2
    },
    {
        "question": "What data type is [1, 2, 3] in Python?",
        "options": ["tuple", "list", "dictionary", "set"],
        "correct_answer_index": 1
    },
    {
        "question": "How do you start a 'for' loop that iterates 5 times?",
        "options": ["for i in range(5):", "loop (5):", "for i from 1 to 5:", "repeat 5 times:"],
        "correct_answer_index": 0
    },
    {
        "question": "Which of these is used to store key-value pairs in Python?",
        "options": ["list", "tuple", "set", "dictionary"],
        "correct_answer_index": 3
    },
    {
        "question": "What does 'API' stand for?",
        "options": ["Application Program Interface", "Advanced Personal Interface", "Automated Process Integration", "Application Programming Interface"],
        "correct_answer_index": 3
    }
]


# --- API Call Functions (from ai-story-co-writer-python-local-exec) ---

async def call_gemini_api(prompt_text: str) -> str:
    """
    Makes an asynchronous call to the Gemini API (text generation model) to generate content.
    Uses httpx for HTTP requests.

    Args:
        prompt_text (str): The prompt string to send to the AI.

    Returns:
        str: The AI's generated response text.
    """
    api_key_to_use = API_KEY
    if '__api_key' in globals(): # Check if running in Canvas environment
        api_key_to_use = globals()['__api_key']

    if not api_key_to_use:
        st.error("Error: API key is not configured. Please set the API_KEY variable or ensure Canvas provides it.")
        return "API Key Error"

    chat_history = [{'role': 'user', 'parts': [{'text': prompt_text}]}]
    payload = {'contents': chat_history}
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key_to_use}";

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                api_url,
                headers={'Content-Type': 'application/json'},
                json=payload # httpx handles JSON payload directly
            )
            response.raise_for_status()

            result = response.json()
            candidates = result.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text']
            
            st.error(f'Unexpected API response structure: {result}')
            return "Sorry, I couldn't get a clear response from the AI. Please try again!"

    except httpx.RequestError as error:
        st.error(f'Error calling Gemini API: {error}')
        return f"ERROR: Failed to connect to AI. Details: {error}. Make sure your API key is correctly entered and you have an internet connection."
    except Exception as error:
        st.error(f'An unexpected error occurred: {error}')
        return f"An unexpected error occurred: {error}"

async def call_imagen_api(prompt_text: str) -> str:
    """
    Calls the Imagen API (image generation model) to generate an image.
    Uses httpx for HTTP requests.

    Args:
        prompt_text (str): The prompt string for the image generation.

    Returns:
        str: A base64 image URL or a placeholder URL if generation fails.
    """
    api_key_to_use = API_KEY
    if '__api_key' in globals(): # Check if running in Canvas environment
        api_key_to_use = globals()['__api_key']

    if not api_key_to_use:
        st.error("Error: API key is not configured for Imagen. Please set the API_KEY variable.")
        return f"https://placehold.co/400x200/505050/FFFFFF?text=API+Key+Missing" # Fallback for display


    payload = {"instances": {"prompt": prompt_text}, "parameters": {"sampleCount": 1}}
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key_to_use}";

    st.info(f"Generating visual concept for: '{prompt_text}'...") # Informative message for user
    await asyncio.sleep(4) # Simulate longer network delay for image generation

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                apiUrl,
                headers={'Content-Type': 'application/json'},
                json=payload # httpx handles JSON payload directly
            )
            response.raise_for_status()

            result = response.json()
            if result.get('predictions') and len(result['predictions']) > 0 and result['predictions'][0].get('bytesBase64Encoded'):
                return f"data:image/png;base64,{result['predictions'][0]['bytesBase64Encoded']}"
            else:
                st.error(f'Unexpected Imagen API response structure: {result}');
                return f"https://placehold.co/400x200/FF0000/FFFFFF?text=Image+Gen+Failed"; # Generic failure placeholder
    except httpx.RequestError as error:
        st.error(f'Error calling Imagen API: {error}');
        return f"https://placehold.co/400x200/FF0000/FFFFFF?text=API+Error"; # Connection error placeholder
    except Exception as error:
        st.error(f'An unexpected error occurred: {error}');
        return f"An unexpected error occurred: {error}"


# --- Core Project Functions (Adapted from ai-story-co-writer-python-local-exec) ---

async def generate_gemini_suggestions(story_context: str, language: str, genre: str, story_format: str, tone_command: str = "", aesthetic_style: str = "", era_style: str = "") -> list[tuple[str, str]]:
    """
    Generates dynamic story suggestions (continuations, character ideas, plot twists)
    by prompting the Gemini API, respecting the chosen language, genre, character details,
    story format, optional tone command, aesthetic style, and era/style.
    Each suggestion includes a commentary, and a visual concept is also generated.

    Args:
        story_context (str): The current story content to base suggestions on.
        language (str): The language the AI should generate the response in.
        genre (str): The chosen genre of the story.
        story_format (str): The chosen format of the story (Novel, Screenplay, etc.).
        tone_command (str): An optional command to influence the tone of the next generation.
        aesthetic_style (str): Optional aesthetic style (e.g., "20th-century aesthetic").
        era_style (str): Optional era/style reference (e.g., "1940s Noir").

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple contains (suggestion_text, commentary).
                                Expected to return 5 tuples (3 continuations + 1 bonus idea + 1 visual concept).
    """
    # --- AI Prompt Engineering for Suggestions ---
    tone_instruction = f"Also, {tone_command} the next part of the story." if tone_command else "";

    writer_persona = f"award-winning {story_format.lower()} writer";
    aesthetic_instruction = "";
    if aesthetic_style == "20th-century aesthetic":
        aesthetic_instruction = f"Write in the style of a classic 20th-century {story_format.lower()} from the 1930s-1980s, emulating the language, structure, and tone of that era.";
    
    era_style_instruction = "";
    if era_style:
        era_style_instruction = f"Emulate the stylistic elements of a {era_style}.";

    # Determine the type of visual concept to ask for
    visual_concept_type_prompt = "";
    if story_format == "Novel":
        visual_concept_type_prompt = "book cover concept";
    elif story_format == "Short Story":
        visual_concept_type_prompt = "magazine cover concept";
    elif story_format == "Screenplay":
        visual_concept_type_prompt = "movie poster concept";
    elif story_format == "Television Script":
        visual_concept_type_prompt = "TV show title card concept";
    elif story_format == "Play":
        visual_concept_type_prompt = "playbill poster concept";
    
    visual_concept_instruction = "";
    if visual_concept_type_prompt:
        visual_concept_instruction = f"Also describe what a 20th-century-style {visual_concept_type_prompt} would look like for this story. Use vivid visual language.";


    prompt = f"""
You are an {writer_persona} helping a user co-write a suspenseful, engaging, and fun story. The user will pick from your suggestions.

The story genre is {genre}. Write in {language}.
Provide 3 vivid {story_format.lower()} continuation options (1-2 sentences max), each followed by a 'Commentary:' line explaining the creative choice.
Also suggest 1 'Bonus Idea' that introduces a surprise twist or new character, followed by its own 'Commentary:' line.
{tone_instruction}
{aesthetic_instruction}
{era_style_instruction}

Use a tone appropriate to the current mood and {genre} conventions. Be playful, mysterious, or dramatic when fitting.

Format exactly like this:
1. [Continuation 1]
Commentary: [Explanation]
2. [Continuation 2]
Commentary: [Explanation]
3. [Continuation 3]
Commentary: [Explanation]
Bonus Idea: [Plot twist or new character]
Commentary: [Explanation]
{visual_concept_instruction}

Story so far:
---
{story_context}
---
""";
    ai_raw_response = await call_gemini_api(prompt);

    # --- Parsing AI Response for Suggestions and Commentary ---
    parsed_suggestions = [];
    lines = [line.strip() for line in ai_raw_response.strip().split('\n') if line.strip()]; # Clean and split

    i = 0;
    while i < len(lines):
        # Match numbered suggestions
        match_suggestion = re.match(r'^\d+\.\s*(.*)$', lines[i]);
        # Match Bonus Idea
        match_bonus = re.match(r'^Bonus Idea:\s*(.*)$', lines[i], re.IGNORECASE);
        # Match Visual Concept - now explicitly looking for the new prompt wording
        match_visual_concept_output = re.match(r'^(Visual Concept:.*?)$', lines[i], re.IGNORECASE);


        current_line_is_suggestion_or_bonus = False;
        suggestion_text = "";

        if match_suggestion:
            suggestion_text = match_suggestion.group(1).strip();
            current_line_is_suggestion_or_bonus = True;
        elif match_bonus:
            suggestion_text = "Bonus Idea: " + match_bonus.group(1).strip();
            current_line_is_suggestion_or_bonus = True;
        elif match_visual_concept_output: # This means it's the actual output of the visual concept
            suggestion_text = match_visual_concept_output.group(1).strip();
        else:
            i += 1;
            continue; # Skip line if it's not a recognizable suggestion or visual concept

        # Move to the next line to check for commentary
        i += 1; 
        commentary_text = "No commentary provided."; # Default if not found

        if i < len(lines) and lines[i].lower().startswith("commentary:"):
            commentary_text = re.sub(r'^commentary:\s*', '', lines[i], flags=re.IGNORECASE).strip();
            i += 1; # Move to the next line after commentary
        else:
            # If no commentary found, stay on the current line or move past the suggestion
            pass; 
        
        parsed_suggestions.append((suggestion_text, commentary_text));


    # Ensure we return exactly 5 tuples (3 main + 1 bonus + 1 visual concept), even if parsing fails partially.
    # This robust padding ensures display functions don't error out.
    if len(parsed_suggestions) < 5:
        print(f"Warning: Expected 5 suggestions with commentary (3 main, 1 bonus, 1 visual), got {len(parsed_suggestions)}. Raw response:\n{ai_raw_response}");
        while len(parsed_suggestions) < 3: # Pad main suggestions
            parsed_suggestions.append((f"AI continuation {len(parsed_suggestions)+1} (fallback)", "No commentary."));
        if len(parsed_suggestions) < 4: # Pad bonus idea
            parsed_suggestions.append(("Bonus Idea (fallback)", "No commentary."));
        if len(parsed_suggestions) < 5: # Pad visual concept
            parsed_suggestions.append(("Visual Concept: Placeholder image idea.", "No commentary."));


    return parsed_suggestions[:5]; # Return exactly the first 5 if more were somehow parsed


async def generate_gemini_endings(story_context: str, language: str, genre: str, story_format: str, aesthetic_style: str = "", era_style: str = "") -> list[str]:
    """
    Generates distinct story endings by prompting the Gemini API, respecting
    the chosen language, genre, story format, aesthetic style, and era/style.

    Args:
        story_context (str): The current story content to base endings on.
        language (str): The language the AI should generate the response in.
        genre (str): The chosen genre of the story.
        story_format (str): The chosen format of the story (Novel, Screenplay, etc.).
        aesthetic_style (str): Optional aesthetic style (e.g., "20th-century aesthetic").
        era_style (str): Optional era/style reference (e.g., "1940s Noir").

    Returns:
        list[str]: A list of 2-3 distinct AI-generated ending texts.
    """
    writer_persona = f"award-winning {story_format.lower()} writer";
    aesthetic_instruction = "";
    if aesthetic_style == "20th-century aesthetic":
        aesthetic_instruction = f"Write in the style of a classic 20th-century {story_format.lower()} from the 1930s-1980s, emulating the language, structure, and tone of that era.";
    
    era_style_instruction = "";
    if era_style:
        era_style_instruction = f"Emulate the stylistic elements of a {era_style}.";

    prompt = f"""
You are an {writer_persona} helping a user conclude their suspenseful, engaging, and fun story. The user will pick from your suggested endings.

The story genre is {genre}. Write in {language}.
Provide 2-3 distinct and concise {story_format.lower()} ending options (1-3 sentences max each). Each ending should offer a different resolution or emotional tone (e.g., triumphant, bittersweet, mysterious, conclusive).
{aesthetic_instruction}
{era_style_instruction}

Format exactly as a numbered list:
1. [Ending 1]
2. [Ending 2]
3. [Ending 3] (Optional, if you have a third distinct idea)

Story so far:
---
{story_context}
---
""";
    ai_raw_response = await call_gemini_api(prompt);

    # Parsing AI Response for Endings
    endings = re.findall(r'^\d+\.\s*(.*)$', ai_raw_response, re.MULTILINE);

    if not endings:
        print(f"Warning: No endings parsed from AI response. Raw response:\n{ai_raw_response}");
        return ["A mysterious silence fell, leaving the story unfinished.", "The end, for now."]; # Fallback endings
    
    return endings;


# --- Helper Functions for Streamlit State Management (from ai-story-co-writer-python-local-exec) ---

def initialize_session_state():
    """Initializes Streamlit session state variables for a new story."""
    if 'current_story' not in st.session_state:
        st.session_state.current_story = ""
    if 'story_log' not in st.session_state:
        st.session_state.story_log = [] # List of dicts for full story history
    if 'suggestions_with_commentary' not in st.session_state:
        st.session_state.suggestions_with_commentary = []
    if 'generated_image_url' not in st.session_state:
        st.session_state.generated_image_url = ""
    if 'main_character_name' not in st.session_state:
        st.session_state.main_character_name = ""
    if 'main_character_role' not in st.session_state:
        st.session_state.main_character_role = "" # Start empty for explicit choice
    if 'story_language' not in st.session_state:
        st.session_state.story_language = "" # Start empty for explicit choice
    if 'story_genre' not in st.session_state:
        st.session_state.story_genre = "" # Start empty for explicit choice
    if 'story_format' not in st.session_state:
        st.session_state.story_format = "" # Start empty for explicit choice
    if 'aesthetic_style' not in st.session_state:
        st.session_state.aesthetic_style = ""
    if 'era_style' not in st.session_state:
        st.session_state.era_style = ""
    if 'round_number' not in st.session_state:
        st.session_state.round_number = 0
    if 'story_creation_complete' not in st.session_state:
        st.session_state.story_creation_complete = False # Flag to control UI stages
    if 'alternate_endings' not in st.session_state: # NEW: for storing alternate endings
        st.session_state.alternate_endings = []
    if 'story_concluded' not in st.session_state: # NEW: flag to indicate story is finished
        st.session_state.story_concluded = False


def update_story_log(chosen_text: str, contributor: str = "User", suggestion_type: str = ""):
    """Appends a new segment to the story log."""
    st.session_state.round_number += 1
    st.session_state.story_log.append({
        "round": st.session_state.round_number,
        "text": chosen_text,
        "contributor": contributor,
        "type": suggestion_type if contributor == "AI" else "User Input"
    })
    # Update current_story string for display
    if st.session_state.current_story and not st.session_state.current_story.strip().endswith(('.', '!', '?', '\n', ' ')):
        separator = ". "
    else:
        separator = ""
    st.session_state.current_story += separator + chosen_text.strip()


# --- Story Generation Logic (Adapted for Streamlit) ---

def get_story_context_streamlit(main_character_name: str, main_character_role: str, story_genre: str, story_format: str, aesthetic_style: str = "", era_style: str = "") -> str:
    """
    Prepares and returns the current story content as context for the AI,
    including character details, genre, format, aesthetic style, and era/style.
    Uses st.session_state.current_story.
    """
    aesthetic_line = f"Aesthetic Style: {aesthetic_style}.\n" if aesthetic_style else ""
    era_style_line = f"Era/Stylistic Reference: {era_style}.\n" if era_style else ""

    return (f"Main character: {main_character_name} the {main_character_role}.\n"
            f"Story Genre: {story_genre}.\n"
            f"Story Format: {story_format}.\n"
            f"{aesthetic_line}"
            f"{era_style_line}"
            f"Current story progress:\n{st.session_state.current_story}")

# This function will be triggered by Streamlit's event loop
async def _generate_and_update_suggestions_gui():
    """
    Orchestrates AI suggestion generation and updates Streamlit UI state.
    This is an internal helper function.
    """
    # Check if all required initial parameters are set before generating
    if not all([st.session_state.main_character_name,
                st.session_state.main_character_role,
                st.session_state.story_language,
                st.session_state.story_genre,
                st.session_state.story_format]):
        st.warning("Please fill in all required fields (Character Name, Role, Language, Genre, Format) to create your story.")
        st.session_state._generating_suggestions = False # Reset generating state
        st.rerun() # Rerun to clear spinner/show warning
        return

    with st.spinner("Calling the AI Muse..."): # Show spinner while AI is thinking
        # Gather all necessary context from session state
        story_context = get_story_context_streamlit(
            st.session_state.main_character_name,
            st.session_state.main_character_role,
            st.session_state.story_genre,
            st.session_state.story_format,
            st.session_state.aesthetic_style,
            st.session_state.era_style
        )
        
        # Tone command can be made dynamic via a st.text_input in UI later (not implemented in this GUI version yet)
        tone_command = "" 

        suggestions_with_commentary = await generate_gemini_suggestions(
            story_context,
            st.session_state.story_language,
            st.session_state.story_genre,
            st.session_state.story_format,
            tone_command,
            st.session_state.aesthetic_style,
            st.session_state.era_style
        )
        
        st.session_state.suggestions_with_commentary = suggestions_with_commentary
        st.session_state.alternate_endings = [] # Clear endings if new suggestions are generated

        generated_image_url = ""
        visual_concept_tuple = next((s for s in suggestions_with_commentary if s[0].startswith("Visual Concept:")), None)
        if visual_concept_tuple:
            visual_concept_description = visual_concept_tuple[0].replace("Visual Concept: ", "").strip()
            # Call the image generation API with the description
            generated_image_url = await call_imagen_api(visual_concept_description)
        
        st.session_state.generated_image_url = generated_image_url
        st.session_state._generating_suggestions = False # Reset generating state after completion
        st.session_state.story_creation_complete = True # Move to the next UI stage
        st.rerun() # Rerun to update UI with new suggestions and image


async def _generate_and_update_endings_gui():
    """
    Orchestrates AI ending generation and updates Streamlit UI state.
    """
    with st.spinner("Crafting alternate realities..."):
        story_context = get_story_context_streamlit(
            st.session_state.main_character_name,
            st.session_state.main_character_role,
            st.session_state.story_genre,
            st.session_state.story_format,
            st.session_state.aesthetic_style,
            st.session_state.era_style
        )
        
        alternate_endings = await generate_gemini_endings(
            story_context,
            st.session_state.story_language,
            st.session_state.story_genre,
            st.session_state.story_format,
            st.session_state.aesthetic_style,
            st.session_state.era_style
        )
        
        st.session_state.alternate_endings = alternate_endings # Store new endings
        st.session_state.suggestions_with_commentary = [] # Clear regular suggestions
        st.session_state.generated_image_url = "" # Clear image
        st.session_state._generating_endings = False # Reset generating state
        st.rerun()


# --- Custom CSS for Styling (Matching download.jpg) ---
st.markdown("""
<style>
    /* General body and container styling for dark theme and rounded corners */
    body {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0; /* Light gray text */
        background-color: #0A0A10; /* Very dark background */
    }
    .stApp {
        background-color: #0A0A10;
        color: #E0E0E0;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        background-color: #1A1A2A; /* Slightly lighter dark blue for content area */
        border-radius: 12px; /* Rounded corners for main container */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .stSidebar {
        background-color: #1A1A2A; /* Same as main for a cohesive look */
        border-right: 1px solid #303040;
    }
    .st-dg, .st-ck, .st-dd { /* Target text input, checkbox, radio button labels */
        color: #E0E0E0 !important;
    }

    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: #F0F0F0; /* White/light gray for headers */
    }

    /* Text input styling to match image (darker, rounded) */
    div[data-baseweb="input"] > div {
        background-color: #2A2A3A; /* Darker input background */
        border-radius: 8px; /* Rounded corners */
        border: 1px solid #4A4A5A; /* Subtle border */
        color: #F0F0F0; /* Light text in input */
    }
    textarea[data-baseweb="textarea"] {
        background-color: #2A2A3A !important;
        border-radius: 8px !important;
        border: 1px solid #4A4A5A !important;
        color: #F0F0F0 !important;
    }

    /* Button styling to match image (rounded, dark, then blue active) */
    .stButton > button {
        width: 100%; /* Make buttons fill width like image */
        border-radius: 8px; /* Rounded corners */
        background-color: #3A3A4A; /* Dark button background */
        color: #E0E0E0; /* Light text */
        border: 1px solid #4A4A5A; /* Subtle border */
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #4A4A5A; /* Lighter on hover */
        border-color: #6A6A7A;
    }

    /* Specific styling for selected/active buttons (simulating the blue in the image) */
    .stButton > button.selected-choice {
        background-color: #007BFF; /* Primary blue for selected */
        color: white;
        border-color: #0056b3;
        box-shadow: 0 2px 8px rgba(0, 123, 255, 0.4);
    }

    /* Main "Create Story" button style */
    .create-story-btn > button {
        background-color: #007BFF; /* Blue background */
        color: white;
        border-color: #0056b3;
        font-size: 1.25rem;
        padding: 1rem 1.5rem;
        font-weight: 700;
        margin-top: 2rem;
        box-shadow: 0 4px 10px rgba(0, 123, 255, 0.4);
    }
    .create-story-btn > button:hover {
        background-color: #0056b3;
        border-color: #004085;
    }

    /* Section Headers */
    .stContainer > h2 {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F0F0F0;
        margin-bottom: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #303040; /* Separator lines */
    }
    .stContainer > h2:first-of-type {
        border-top: none; /* No top border for the very first header */
    }

    /* General text styling */
    p {
        color: #D0D0D0;
    }
    
    /* Hide Streamlit default header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} /* Hides the upper Streamlit header too */

    /* Custom Header at the top */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 1.5rem;
        color: #F0F0F0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .close-icon {
        cursor: pointer;
        font-size: 1.8rem;
    }
    .film-reel-image {
        width: 100%; /* Make image responsive */
        max-width: 300px; /* Max size for the film reel */
        display: block;
        margin: 0 auto 1.5rem auto; /* Center image with spacing */
        border-radius: 8px; /* Slightly rounded for the image */
    }
</style>
""", unsafe_allow_html=True)


# --- UI Choice Helper Function (from ai-story-co-writer-python-local-exec) ---
# This function creates a set of buttons that behave like a radio group.
# It updates st.session_state when a choice is made.
def create_choice_buttons(label, options, session_state_key):
    st.markdown(f"**{label}**") # Title for the group
    cols = st.columns(len(options)) # Create columns for buttons
    
    current_selection = st.session_state.get(session_state_key, "")

    for i, option in enumerate(options):
        with cols[i]:
            if st.button(option, key=f"{session_state_key}_{option}"):
                st.session_state[session_state_key] = option
                st.rerun() # Rerun to update button styling

    # Apply 'selected-choice' class via markdown if the option is active
    # This must be done AFTER the buttons are created
    st.markdown(
        f"""
        <script>
            var buttons = parent.document.querySelectorAll('div[data-testid="stButton"] button');
            buttons.forEach(button => {{
                if (button.textContent === "{current_selection}") {{
                    button.classList.add('selected-choice');
                }} else {{
                    button.classList.remove('selected-choice');
                }}
            }});
        </script>
        """,
        unsafe_allow_html=True
    )


# --- Streamlit UI Layout ---

st.set_page_config(layout="centered", page_title="Story-Verse Alpha") # Centered layout for mobile-like feel

# NEW: Display app version in the sidebar for immediate visual confirmation
st.sidebar.markdown("---")
st.sidebar.info("App Version: 2025-06-27-V13") # This line will confirm the correct file is running!


initialize_session_state()

# Custom Header (Mimicking the image's top bar)
st.markdown("""
<div class="custom-header">
    <span class="close-icon" onclick="window.parent.postMessage('close_app', '*')">✖</span>
    <span>New Story</span>
    <span></span> <!-- Placeholder for symmetry -->
</div>
""", unsafe_allow_html=True)

# Film Reel Image (using a placeholder for now, replace with actual if available)
st.image("https://placehold.co/400x250/1A1A2A/FFFFFF?text=Film+Reel+Placeholder", use_column_width=True, caption="") # Or use download.jpg locally if accessible

# Use a main container to group all input sections for consistent styling
with st.container():
    st.markdown("## Character")
    st.session_state.main_character_name = st.text_input(
        "Character Name",
        value=st.session_state.main_character_name,
        placeholder="Character Name",
        label_visibility="collapsed",
        key="mc_name_input",
        disabled=st.session_state.story_concluded # Disable input if story concluded
    )

    # Character Role buttons
    character_roles = ["Hero", "Villain", "Wanderer"]
    create_choice_buttons("Character Role", character_roles, "main_character_role")

    st.markdown("## Genre")
    genres = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Thriller", "Historical"]
    create_choice_buttons("Genre", genres, "story_genre")

    st.markdown("## Language")
    languages = ["English", "Spanish", "French", "German", "Hindi", "Chinese"] # Expanded languages
    create_choice_buttons("Language", languages, "story_language")

    st.markdown("## Format")
    formats = STORY_FORMATS # Use the global list
    create_choice_buttons("Format", formats, "story_format")

    st.markdown("## Aesthetic Style")
    aesthetic_styles = ["No Aesthetic", "20th-century aesthetic"] # Simplified choices for now
    create_choice_buttons("Aesthetic Style", aesthetic_styles, "aesthetic_style")
    if st.session_state.aesthetic_style == "No Aesthetic":
        st.session_state.aesthetic_style = "" # Clear if "No Aesthetic" chosen

    st.markdown("## Era/Style")
    era_styles_display = STORY_ERAS + ["None / Skip"] # Use the global list + skip option
    create_choice_buttons("Era/Style", era_styles_display, "era_style")
    if st.session_state.era_style == "None / Skip":
        st.session_state.era_style = "" # Clear if "None / Skip" chosen

    # The "Create Story" button from the image
    if not st.session_state.story_creation_complete and not st.session_state.story_concluded:
        if st.button("Create Story", key="create_story_btn", type="primary", help="Generate the initial story segment"):
            # Check if all required fields are filled for initial story creation
            if not st.session_state.main_character_name:
                st.error("Please enter a Character Name.")
            elif not st.session_state.main_character_role:
                st.error("Please select a Character Role.")
            elif not st.session_state.story_genre:
                st.error("Please select a Genre.")
            elif not st.session_state.story_language:
                st.error("Please select a Language.")
            elif not st.session_state.story_format:
                st.error("Please select a Format.")
            else:
                # All initial setup is complete, proceed to story generation
                st.session_state.story_creation_complete = True
                st.session_state._generating_suggestions = True # Set flag to show spinner
                # Use asyncio.create_task for async generation in Streamlit callback
                asyncio.create_task(_generate_and_update_suggestions_gui())
                st.rerun() # Rerun to show loading spinner and hide setup form

# --- Story Progression / AI Suggestions (Hidden until initial setup is done) ---
if st.session_state.story_creation_complete:
    st.markdown("---") # Separator from setup
    st.header("📜 Your Co-Authored Narrative")
    
    # Display the full story
    st.text_area(
        "Full Story Progression:",
        value=st.session_state.current_story,
        height=300,
        key="full_story_display",
        disabled=True # User cannot edit directly here
    )

    # Conditionally show buttons for suggestions or endings based on story state
    if not st.session_state.story_concluded: # Only show these if story is not concluded
        if st.session_state.get('_generating_suggestions', False):
            st.info("Generating suggestions, please wait...")
        elif st.session_state.get('_generating_endings', False):
            st.info("Crafting alternate realities, please wait...")
        else:
            st.header("💡 AI's Creative Input")

            if st.session_state.suggestions_with_commentary:
                st.markdown("---")
                st.subheader("Choose Your Next Path:")

                options_to_display = []
                for i, (sugg_text, commentary) in enumerate(st.session_state.suggestions_with_commentary):
                    if sugg_text.startswith("Bonus Idea:"):
                        options_to_display.append(f"Bonus: {sugg_text.replace('Bonus Idea: ', '')} (Notes: {commentary})")
                    elif sugg_text.startswith("Visual Concept:"):
                        pass # Not a story continuation choice, it's for the image display
                    else:
                        options_to_display.append(f"{sugg_text} (Notes: {commentary})")
                
                selected_option_label = st.radio(
                    "Select an option to continue the story:",
                    options_to_display[:4], # Show first 4 options (3 main + 1 bonus)
                    key="suggestion_radio_buttons"
                )

                user_typed_continuation = st.text_input("Or type your own continuation:", key="user_typed_continuation")

                if st.button("Add to Story", key="add_to_story_btn"):
                    chosen_text = ""
                    # Determine chosen_text based on radio selection or user input
                    if user_typed_continuation:
                        chosen_text = user_typed_continuation
                        update_story_log(chosen_text, "User")
                    elif selected_option_label:
                        # Find the original text from suggestions_with_commentary based on the label
                        for sugg_text, commentary in st.session_state.suggestions_with_commentary:
                            formatted_sugg_check = ""
                            if sugg_text.startswith("Bonus Idea:"):
                                formatted_sugg_check = f"Bonus: {sugg_text.replace('Bonus Idea: ', '')} (Notes: {commentary})"
                            else:
                                formatted_sugg_check = f"{sugg_text} (Notes: {commentary})"
                            
                            if formatted_sugg_check == selected_option_label:
                                chosen_text = sugg_text.replace("Bonus Idea: ", "").strip() # Clean prefix for story
                                update_story_log(chosen_text, "AI", "Bonus Idea" if "Bonus" in formatted_sugg_check else "Continuation")
                                break
                    else:
                        st.warning("Please select an AI suggestion or type your own continuation.")
                        st.stop() # Stop execution to prevent further processing if no choice

                    # Clear previous suggestions and trigger new generation
                    st.session_state.suggestions_with_commentary = [] 
                    st.session_state.alternate_endings = [] # Clear any previous endings
                    st.session_state.generated_image_url = "" 
                    st.session_state.user_typed_continuation = "" # Clear user input field
                    st.session_state._generating_suggestions = True # Show spinner for next round
                    asyncio.create_task(_generate_and_update_suggestions_gui()) # Generate next suggestions
                    st.rerun() # Rerun to update UI
                        
                st.markdown("---")
                st.subheader("🎨 Visual Concept for Your Story")
                visual_concept_found = next((s for s in st.session_state.suggestions_with_commentary if s[0].startswith("Visual Concept:")), None)
                if visual_concept_found:
                    st.markdown(f"**Concept:** {visual_concept_found[0].replace('Visual Concept: ', '').strip()}")
                    st.markdown(f"*(Director's Notes: {visual_concept_found[1]})*")
                    if st.session_state.generated_image_url:
                        st.image(st.session_state.generated_image_url, caption="AI-Generated Visual Concept", use_column_width=True)
                    else:
                        st.info("No image URL generated or available for this concept.")
                else:
                    st.info("AI has not yet generated a visual concept for this story segment.")
                
                # --- NEW: Roll Another Ending Button ---
                if st.session_state.round_number > 0: # Only show after at least one round
                    st.markdown("---")
                    if st.button("🎭 Roll Alternate Endings", key="roll_endings_btn"):
                        st.session_state._generating_endings = True
                        asyncio.create_task(_generate_and_update_endings_gui())
                        st.rerun()

            elif st.session_state.alternate_endings: # Display alternate endings if available
                st.markdown("---")
                st.subheader("Choose Your Ending:")
                for i, ending_text in enumerate(st.session_state.alternate_endings):
                    st.markdown(f"**Ending {i+1}:**")
                    st.write(ending_text)
                    if st.button(f"✅ Make Ending {i+1} Canon", key=f"select_ending_{i}"):
                        update_story_log(ending_text, "AI", "Story Ending")
                        st.session_state.story_concluded = True
                        st.session_state.alternate_endings = [] # Clear endings after one is chosen
                        st.rerun()
                
                if st.button("Roll More Endings", key="roll_more_endings_btn"):
                    st.session_state._generating_endings = True
                    asyncio.create_task(_generate_and_update_endings_gui())
                    st.rerun()

            else: # Initial state after "Create Story" or if no suggestions/endings yet
                if st.session_state.current_story: # Only show this if a story has been started
                    if st.button("Get Next Suggestions", key="get_next_suggestions_btn"):
                        st.session_state._generating_suggestions = True
                 
                else:
                    st.info("Start by filling out the form and clicking 'Create Story'!")
    else: # Story is concluded
        st.success("🎉 Your story has reached its grand finale! 🎉")
        st.markdown("---")
        # Add export options here (e.g., download button for full story)
        st.download_button(
            label="⬇️ Download Full Story",
            data=st.session_state.current_story.encode('utf-8'),
            file_name="my_co_authored_story.txt",
            mime="text/plain"
        )
        st.markdown("---")
        if st.button("Start a New Story", key="new_story_after_end_btn"):
            st.session_state.clear()
            initialize_session_state()
            st.experimental_rerun()


# Display the full story log for debugging/review (optional, can be removed in final app)
with st.expander("Show Full Story Log (for Debugging)"):
    st.json(st.session_state.story_log)

st.markdown("---")
st.markdown("Created by Director Dunstan with AI assistance.")

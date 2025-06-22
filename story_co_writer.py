import re # Used for parsing numbered lists from AI responses

# --- Hypothetical Gemini API Call Function (for demonstration) ---
# In a real application, this would interact with the actual Gemini API
# This function is a placeholder to show how prompts are used.
async def call_gemini_api(prompt_text: str) -> str:
    """
    Simulates an asynchronous call to the Gemini API.
    In a real application, this would involve actual API requests.
    For this conceptual example, it will return a mock response.

    Args:
        prompt_text (str): The prompt string to send to the AI.

    Returns:
        str: A simulated AI response.
    """
    print(f"\n--- Sending to AI ---\nPrompt:\n{prompt_text}\n---------------------\n")
    # This is where you'd integrate your actual API call logic.
    # For now, return a fixed, parseable mock response for testing.
    # In a real scenario, the AI will generate these dynamically.
    if "story continuation" in prompt_text.lower() and "character idea" in prompt_text.lower():
        return """
1. The old lighthouse keeper, wary of strangers, watched them from his window as they approached, his hand resting on a rusty lever.
2. A new character appears: Elara, a nimble shadow thief with an uncanny knack for finding lost things.
3. Plot twist: The 'ancient artifact' they seek is not a physical object, but a forgotten melody that unlocks a hidden dimension.
"""
    elif "What is a 'variable'?" in prompt_text:
        return "A 'variable' in programming is like a named box where you can store different kinds of toys (data). You can put a car in it, then later put a teddy bear in it, and the box keeps track of what's inside!"
    elif "a loop that counts to 5" in prompt_text:
        return """```python
for i in range(1, 6):
    print(i)
```"""
    elif "quick, surprising tip about Python" in prompt_text:
        return "Python has a 'zen' embedded in it! Type `import this` in your Python interpreter for a surprise poetic philosophy lesson."
    elif "greeting for a user named" in prompt_text:
        # Example for greeting prompt, would be more dynamic with actual AI
        return f"Greetings, fellow adventurer! Your chosen path indicates a valiant spirit. Let us embark on this narrative quest!"
    else:
        return "Simulated AI: I'm ready for a new challenge. What's next?"


# --- Core Project Functions ---

def get_story_context(current_story: str) -> str:
    """
    Prepares and returns the current story content as context for the AI.
    This function can be enhanced to manage token limits by truncating
    or summarizing 'current_story' if it gets too long for the AI model.

    Args:
        current_story (str): The complete story string built so far.

    Returns:
        str: A formatted string representing the story context for the AI.
    """
    # For simplicity, we'll use the entire story for context.
    # For very long stories, consider sending only the last N sentences/paragraphs
    # or using a summarization AI call first.
    return f"Current story progress:\n{current_story}"

async def generate_ai_suggestions(story_context: str) -> list[str]:
    """
    Generates adaptive AI-driven suggestions for story continuation,
    new characters, or plot twists by prompting the Gemini API.

    Args:
        story_context (str): The current story content to base suggestions on.

    Returns:
        list[str]: A list of 3 extracted AI-generated suggestions.
    """
    # --- AI Prompt Engineering for Suggestions ---
    # This prompt is carefully crafted to get 3 specific types of suggestions
    # in a parseable numbered list format.
    prompt = f"""
Given the following story context, generate exactly 3 distinct, concise (1-2 sentences each) options for how the story could proceed. Each option should be a:
1.  **Direct Story Continuation:** What happens next directly building on the last events.
2.  **New Character Idea:** Introduce a new character relevant to the current plot or setting.
3.  **Potential Plot Twist:** A sudden, unexpected turn in the narrative.

Present these as a numbered list (1., 2., 3.).

Story context:
---
{story_context}
---
"""
    ai_raw_response = await call_gemini_api(prompt)

    # --- Parsing AI Response ---
    # This regex looks for lines starting with a number followed by a period and space,
    # capturing the rest of the line.
    suggestions = re.findall(r'^\d+\.\s*(.*)$', ai_raw_response, re.MULTILINE)

    # Ensure we return exactly 3 suggestions, even if parsing fails partially.
    # In a robust app, you'd add more error checking/re-prompting logic.
    if len(suggestions) != 3:
        print(f"Warning: Expected 3 suggestions, got {len(suggestions)}. Raw response:\n{ai_raw_response}")
        # Fallback in case parsing doesn't yield 3 options
        return suggestions[:3] if suggestions else ["AI suggestion 1 (fallback)", "AI suggestion 2 (fallback)", "AI suggestion 3 (fallback)"]
    return suggestions

def update_story(current_story: str, chosen_text: str) -> str:
    """
    Appends the user's chosen suggestion or free-form text to the current story.

    Args:
        current_story (str): The story string before the update.
        chosen_text (str): The text chosen by the user to append.

    Returns:
        str: The updated story string.
    """
    # Add a newline or space for readability between segments
    if current_story and not current_story.endswith(('.', '!', '?', '\n', ' ')):
        separator = ". " # Add a period if the last sentence didn't end with one
    else:
        separator = ""
    
    return current_story + separator + chosen_text.strip()

# --- Placeholder for UI-related functions (frontend responsibility) ---

def display_suggestions(suggestions: list[str]):
    """
    (Conceptual function)
    Renders the AI-generated suggestions as interactive elements on the UI
    (e.g., buttons), allowing the user to select one.
    Also provides a free-form input for the user's own text.
    This function would be implemented in JavaScript/HTML.

    Args:
        suggestions (list[str]): The list of AI-generated suggestions.
    """
    print("\n--- AI Suggestions ---")
    for i, suggestion in enumerate(suggestions):
        print(f"{i+1}. {suggestion}")
    print("----------------------")
    print("Or type your own continuation.")

def get_user_choice() -> str:
    """
    (Conceptual function)
    Waits for and captures the user's selection (either clicking an AI suggestion
    or submitting their own free-form text).
    This function would primarily be event-driven in JavaScript/HTML.

    Returns:
        str: The text chosen or entered by the user.
    """
    # This would involve JavaScript event listeners and UI state management.
    # For Python simulation, we would use input().
    return input("\nYour choice (type 1, 2, 3 or your own text): ")

# --- New function as requested: get_user_words ---
def get_user_words() -> tuple[str, str, str]:
    """
    Prompts the user to enter a noun, a verb, and an adjective,
    and returns these three words.

    Returns:
        tuple[str, str, str]: A tuple containing the noun, verb, and adjective
                              entered by the user, in that order.
    """
    noun = input("Please enter a noun: ").strip()
    verb = input("Please enter a verb: ").strip()
    adjective = input("Please enter an adjective: ").strip()
    return noun, verb, adjective

# --- Example Usage (Conceptual Python Backend Flow) ---
async def main_story_loop():
    """
    Illustrates the main collaborative story loop.
    In a full web app, this would be orchestrated by JavaScript,
    with Python functions handling specific backend AI calls.
    """
    initial_prompt = input("Start your story with an opening sentence: ")
    current_story = initial_prompt

    print(f"\nYour Story So Far:\n{current_story}")

    for _ in range(3): # Let's do 3 rounds for demonstration
        story_context = get_story_context(current_story)
        suggestions = await generate_ai_suggestions(story_context)
        display_suggestions(suggestions) # Placeholder for UI display

        user_input = get_user_choice() # Placeholder for UI input capture

        # Decide if user chose an AI suggestion or typed their own
        try:
            choice_index = int(user_input) - 1
            if 0 <= choice_index < len(suggestions):
                chosen_text = suggestions[choice_index]
            else:
                chosen_text = user_input # Fallback to user's raw input if number is out of range
        except ValueError:
            chosen_text = user_input # User typed free-form text

        current_story = update_story(current_story, chosen_text)
        print(f"\n--- Current Story ---\n{current_story}\n---------------------\n")

    print("\n--- End of Story (Demonstration) ---")
    print("Your final story:\n", current_story)

    # Example usage of the new get_user_words function
    print("\n--- Let's get some words for fun! ---")
    my_noun, my_verb, my_adjective = get_user_words()
    print(f"You provided: Noun='{my_noun}', Verb='{my_verb}', Adjective='{my_adjective}'")

# To run this conceptual Python backend part (e.g., in a Python environment):
# import asyncio
# asyncio.run(main_story_loop())

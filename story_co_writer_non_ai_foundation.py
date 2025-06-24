import re
import json # Import json for saving/loading structured data

# --- Core Project Functions (Non-AI Version) ---

def start_new_story():
    """
    Initiates a new story session.
    """
    print("\n--- Welcome to the Story Co-Writer (Non-AI Mode)! ---")
    print("Let's craft a tale together. You'll start, and I'll give you options.\n")

def get_initial_prompt(story_log: list[dict]) -> None:
    """
    Asks the user for the initial sentence or prompt for their story
    and appends it as the first segment to the story_log.

    Args:
        story_log (list[dict]): The list of story segments (each a dictionary).
    """
    while True:
        prompt_text = input("Start your story with an opening sentence: ").strip()
        if prompt_text:
            # Store the initial prompt as a dictionary with 'text' and 'contributor'
            story_log.append({
                "text": prompt_text,
                "contributor": "User",
                "round": 0 # Initial segment is round 0
            })
            print(f"\n--- Your Story So Far ---\n{get_full_story_text(story_log)}\n-------------------------\n")
            break
        else:
            print("The story needs a beginning! Please enter something.")

def get_full_story_text(story_log: list[dict]) -> str:
    """
    Compiles the full story text from the list of story segments.

    Args:
        story_log (list[dict]): The list of story segments.

    Returns:
        str: The concatenated text of the entire story.
    """
    full_text = []
    for segment in story_log:
        segment_text = segment.get("text", "")
        # Add a separator if the previous segment didn't end with punctuation
        if full_text and not full_text[-1].strip().endswith(('.', '!', '?', '\n', ' ')):
            full_text.append(". ")
        full_text.append(segment_text)
    return "".join(full_text).strip()


def generate_static_suggestions(round_num: int) -> list[dict]:
    """
    Generates static, hardcoded suggestions as dictionaries to simulate AI behavior.
    Each suggestion now includes a 'type' and 'description' (the text).

    Args:
        round_num (int): The current round number, used conceptually to vary suggestions.

    Returns:
        list[dict]: A list of static story suggestion dictionaries.
    """
    # These are placeholder suggestions. In the AI version, Gemini would generate these.
    # We now structure each suggestion as a dictionary for more attributes.
    if round_num % 2 == 0:
        return [
            {"type": "continuation", "text": "A mysterious shadow darted across the moonlit alley, and then vanished."},
            {"type": "continuation", "text": "Suddenly, a tiny, glowing creature emerged from the old oak tree."},
            {"type": "plot_twist", "text": "The ancient map, long thought lost, finally revealed its secret: it was a receipt."},
            {"type": "character_idea", "text": "Introduce a grizzled, cynical detective who hates mysteries."}
        ]
    else:
        return [
            {"type": "continuation", "text": "The air grew cold, and a strange melody began to play from nowhere."},
            {"type": "continuation", "text": "They found a hidden message carved into the underside of the table."},
            {"type": "plot_twist", "text": "The main character woke up, realizing it was all a dream... or was it?"},
            {"type": "character_idea", "text": "Introduce a quirky librarian who knows too much about rare books."}
        ]


def display_suggestions(suggestions: list[dict]):
    """
    Displays the given suggestions as numbered options to the user.
    Now handles a list of dictionaries.

    Args:
        suggestions (list[dict]): The list of story suggestion dictionaries.
    """
    print("\n--- Choose your next path or type your own ---")
    for i, suggestion_dict in enumerate(suggestions):
        print(f"{i+1}. [{suggestion_dict['type'].replace('_', ' ').title()}]: {suggestion_dict['text']}")
    print("---------------------------------------------")

def get_user_choice(num_suggestions: int, suggestions_list: list[dict]) -> dict:
    """
    Prompts the user to make a choice: select a numbered suggestion
    or type their own continuation. Returns the chosen segment as a dictionary.

    Args:
        num_suggestions (int): The number of static suggestions provided.
        suggestions_list (list[dict]): The actual list of suggestion dictionaries.

    Returns:
        dict: A dictionary representing the chosen segment (either from suggestions or user input).
    """
    while True:
        user_input = input(f"Enter a number (1-{num_suggestions}) or type your own continuation: ").strip()
        if not user_input:
            print("Please make a choice or type your continuation.")
            continue

        try:
            choice_index = int(user_input) - 1 # Convert to 0-based index
            if 0 <= choice_index < num_suggestions:
                # User chose a valid numbered suggestion, return its dictionary
                return {
                    "text": suggestions_list[choice_index]["text"],
                    "contributor": "AI", # This segment came from an AI suggestion
                    "type": suggestions_list[choice_index]["type"] # Include the type of suggestion
                }
            else:
                # Number is out of valid range, treat as free-form text
                return {
                    "text": user_input,
                    "contributor": "User", # This segment was user-typed
                    "type": "free_form"
                }
        except ValueError:
            # Not a number, treat as free-form text
            return {
                "text": user_input,
                "contributor": "User",
                "type": "free_form"
            }

def update_story(story_log: list[dict], chosen_segment_dict: dict, round_num: int) -> None:
    """
    Appends the user's chosen segment (as a dictionary) to the story_log.

    Args:
        story_log (list[dict]): The list representing the complete story.
        chosen_segment_dict (dict): The dictionary for the chosen segment.
        round_num (int): The current round number.
    """
    chosen_segment_dict["round"] = round_num # Add round info to the segment
    story_log.append(chosen_segment_dict)


def save_story_to_file(story_log: list[dict], filename: str = "my_story_log.json"):
    """
    Saves the complete story log (list of dictionaries) to a JSON file.

    Args:
        story_log (list[dict]): The complete story content as a list of dictionaries.
        filename (str): The name of the file to save the story to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(story_log, f, indent=4) # Use json.dump for structured data
        print(f"\n✅ Your story log has been saved as '{filename}'!")
    except IOError as e:
        print(f"\n❌ Error saving story to file: {e}")

def load_story_from_file(filename: str = "my_story_log.json") -> list[dict]:
    """
    Loads a story log from a JSON file.

    Args:
        filename (str): The name of the file to load the story from.

    Returns:
        list[dict]: The loaded story log, or an empty list if loading fails.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            story_log = json.load(f)
        print(f"\n✅ Story log loaded from '{filename}'!")
        return story_log
    except FileNotFoundError:
        print(f"\n❌ No story file found at '{filename}'. Starting a new story.")
        return []
    except json.JSONDecodeError as e:
        print(f"\n❌ Error decoding JSON from '{filename}': {e}. Starting a new story.")
        return []
    except IOError as e:
        print(f"\n❌ Error loading story from file: {e}. Starting a new story.")
        return []

# --- Main Logic for Non-AI Version ---

async def run_non_ai_story_co_writer(): # Made async to match potential AI version
    """
    Orchestrates the flow of the non-AI story co-writer, simulating the
    collaborative loop with static suggestions using list of dictionaries.
    """
    start_new_story()

    # Initialize story_log as a list of dictionaries
    story_log: list[dict] = []

    # Option to load a previous story
    if input("Load a previous story? (y/n): ").lower().strip() == 'y':
        story_log = load_story_from_file()

    if not story_log: # If no story loaded or user chose not to load
        get_initial_prompt(story_log)


    num_rounds = 3 # Run for a few rounds to demonstrate the interaction
    for i in range(1, num_rounds + 1): # Start rounds from 1
        print(f"\n--- Round {i} ---")
        
        # We don't need story_context in the non-AI version as suggestions are static
        suggestions = generate_static_suggestions(i) # Pass round number to vary suggestions
        display_suggestions(suggestions)

        user_choice_segment_dict = get_user_choice(len(suggestions), suggestions)
        update_story(story_log, user_choice_segment_dict, i) # Pass round_num here

        print(f"\n--- Current Story After Round {i} ---\n{get_full_story_text(story_log)}\n----------------------------------\n")

    print("\n--- Story Session Concluded (Non-AI Demo) ---")
    print("Here's your complete story:\n")
    print(get_full_story_text(story_log)) # Display the full compiled story

    save_story_to_file(story_log) # Save the full structured log
    
    print("\nThanks for co-writing!")

    # Add Replay or Restart Option
    while True:
        restart = input("\nWould you like to start a new story? (y/n): ").lower().strip()
        if restart == "y":
            print("\n")
            await run_non_ai_story_co_writer() # Restart the entire process
            break # Exit the loop after restarting
        elif restart == "n":
            print("Goodbye, storyteller!")
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# To run this non-AI version, use asyncio.run():
if __name__ == "__main__":
    asyncio.run(run_non_ai_story_co_writer())

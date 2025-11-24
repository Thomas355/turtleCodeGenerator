import os
import random
import time
import json
import traceback
from kaggle_secrets import UserSecretsClient

#to call the array with the prompts
from promptsData import prompts

try:
    GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print("✅ Loaded GOOGLE_API_KEY from Kaggle secrets.")
except Exception as e:
    print("⚠️ Could not load Kaggle secret. Falling back to env variable.", e)

if "GOOGLE_API_KEY" not in os.environ:
    raise RuntimeError("❌ ERROR: No GOOGLE_API_KEY found.")

# Import SDK
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "Please install google-generativeai:\n"
        "!pip install --upgrade google-generativeai\n"
        f"Original error: {e}"
    )

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

MODEL_NAME = "models/gemini-2.5-flash"

def is_executable_python(code_string: str) -> bool:
    """Return True if code_string compiles as Python code."""
    if not isinstance(code_string, str) or not code_string.strip():
        return False
    try:
        compile(code_string, "<string>", "exec")
        return True
    except Exception:
        return False
    
def extract_text(resp):
    """
    Safely extract text from Gemini generate_content() response.
    Gemini 2.x always returns:
    resp.candidates[0].content[0].text
    """
    try:
        return resp.candidates[0].content[0].text
    except:
        return ""

def call_model(prompt: str, temperature=0.7, max_output_tokens=700):
    """
    function that calls the models
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(
            prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        return extract_text(resp)
    except Exception as e:
        print("❌ Model call error:", e)
        traceback.print_exc()
        return ""
    
# Stage 1: Base turtle code generation

def generate_turtle_code(seed_prompt: str, tries: int = 3) -> str:

    base_instruction = f"""
You are a Python programmer who writes turtle graphics code.
Follow these exact constraints:

1) Output MUST be ONLY a single Python code block (NO markdown).
2) Code must start with:

import turtle as t
import random
t.colormode(255)
r = random.randint(0, 255)
g = random.randint(0, 255)
b = random.randint(0, 255)
t.speed(0)
t.bgcolor(r, g, b)
t.tracer(0, 0)

3) Code must end with:

t.hideturtle()
t.update()
t.done()

Write runnable Python turtle code for the user's prompt:
{seed_prompt}
"""

    for attempt in range(1, tries + 1):
        out = call_model(base_instruction, temperature=0.6)
        if is_executable_python(out):
            return out
        print(f"Stage 1 attempt {attempt}: non-executable, retrying...")

    return out

#add variablility to the generated code 
def add_variance_to_code(code: str, tries: int = 2) -> str:

    variance_instruction = f"""
You are a variance generator for Python turtle code.

RULES:
1) Add at least ONE new geometric shape or pattern.
2) Add at least ONE function (def ...).
3) Add a new loop or conditional.
4) Use random colors / pen sizes.
5) Must remain runnable Python turtle code.
6) Must begin with the same required header and end with t.hideturtle(), t.update(), t.done().

Input code:
{code}
"""

    for attempt in range(1, tries + 1):
        out = call_model(variance_instruction, temperature=0.9)
        if is_executable_python(out):
            return out
        print(f"Stage 2 attempt {attempt}: non-executable, retrying...")

    return out

#final layer to make sure that it runs efficently 

def edit_and_polish_code(code: str, tries: int = 2) -> str:

    edit_instruction = f"""
Edit and polish the following Python turtle code.

Requirements:
- Keep required header (imports, colormode, tracer).
- Keep required footer (t.hideturtle(), t.update(), t.done()).
- Improve structure, remove inefficiencies.
- Output ONLY runnable Python code.

Input draft:
{code}
"""

    for attempt in range(1, tries + 1):
        out = call_model(edit_instruction, temperature=0.4)
        if is_executable_python(out):
            return out
        print(f"Stage 3 attempt {attempt}: non-executable, retrying...")

    return out

NUM_SAMPLES = 200 #this can be changed according to specs as the code is flexible 
OUTPUT_DIRECTORY = "turtle_training_data"
#makes directory or puts there
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
#shuffles the prompts to increace variability further 
random.shuffle(prompts)

print(f"Starting to generate {NUM_SAMPLES} samples using {MODEL_NAME}...\n")

#for loop to ask each prompt
for i in range(1, NUM_SAMPLES + 1):
    ptext = prompts[i % len(prompts)]
    print(f"\n--- Sample {i}/{NUM_SAMPLES}: {ptext!r} ---")

    try:
        # Stage 1
        base = generate_turtle_code(ptext, tries=4)
        if not is_executable_python(base):
            print("❌ Base stage failed. Skipping.")
            continue

        # Stage 2
        var = add_variance_to_code(base, tries=3)
        if not is_executable_python(var):
            print("❌ Variance stage failed. Skipping.")
            continue

        # Stage 3
        final = edit_and_polish_code(var, tries=2)
        if not is_executable_python(final):
            print("❌ Final polishing failed. Skipping.")
            continue

        # Validate header/footer
        if not final.strip().startswith("import turtle"):
            print("❌ Missing required header. Skipping.")
            continue
        if not final.strip().endswith("t.done()"):
            print("❌ Missing required footer. Skipping.")
            continue

        # Save files
        with open(f"{OUTPUT_DIRECTORY}/code_{i}.py", "w") as f:
            f.write(final)
        with open(f"{OUTPUT_DIRECTORY}/prompt_{i}.txt", "w") as f:
            f.write(ptext)

        print(f"✅ Saved sample {i}")

    except Exception as e:
        print(f"🔥 Critical error at sample {i}: {e}")
        traceback.print_exc()

print("\n--- DONE: Data Generation Complete ---")
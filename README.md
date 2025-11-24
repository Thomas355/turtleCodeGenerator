
## turtleCodeGenerator

an agentic way to generate python code to be used as training data

This repository provides a fully automated synthetic-data generator that uses Google’s Gemini 2.x models to produce hundreds of high-quality Python turtle graphics scripts.
The pipeline performs three generation stages (base → variance → polishing) and saves both the code samples and the prompts used to create them.

It is designed for:

Training code-generation models

Research on structured code transformations

Artistic procedural generation

Dataset production for ML experiments

📦Installation

install this:
pip install --upgrade google-generativeai
and also this if you are not running this inside Kaggle:
pip install kaggle_secrets

Add your Gemini API key

in kaggle add it under:
Add-ons → Secrets → GOOGLE_API_KEY
on your local machine: 
export GOOGLE_API_KEY="your-key-here"

🛠 Configuration
Open the script and edit:

NUM_SAMPLES = 200
MODEL_NAME = "models/gemini-2.5-flash"
OUTPUT_DIRECTORY = "turtle_training_data"

You can also change the width and height in generate_turtle_code, it is standardized to make the ouptut all the same size 
screen.setup(width=384, height=384)

You can also update the prompts array in promptsData.py.

▶️Running the Script

python generate.py


(Or whatever the script filename is in your repo.)

The script will:

Shuffle prompts

Generate samples

Save them

Print progress and errors

When finished, you’ll see:

--- DONE: Data Generation Complete ---

🧪Validity Checks


Every generated script must:

Be syntactically valid Python (compile(...))

Start with the required turtle header

End with t.hideturtle(); t.update(); t.done()

Execute without errors

Contain added variance (Stage 2)

Pass optimization (Stage 3)

If any step fails, it retries or skips gracefully.


🧷 ##Error Handling & Debugging

The script provides:

Tracebacks for model errors

Retry counters per stage

Warnings for invalid code output

Skips sample creation cleanly when needed

| Issue                                | Solution                                        |
| ------------------------------------ | ----------------------------------------------- |
| `ERROR: No GOOGLE_API_KEY found.`    | Add env variable or Kaggle secret               |
| `Please install google-generativeai` | Run `pip install --upgrade google-generativeai` |
| Non-executable model output          | Script automatically retries                    |




🤝Contributing

Pull requests and issues are welcome!
Please ensure changes preserve:

Header/Footer constraints

Retry logic

Syntactic validation

Reproducible outputs




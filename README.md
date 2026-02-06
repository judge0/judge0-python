# Judge0 Python SDK

[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/Judge0HQ)](https://x.com/Judge0HQ)
[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/hermanzvonimir)](https://x.com/hermanzvonimir)

[![License](https://img.shields.io/github/license/judge0/judge0-python)](LICENSE)
[![Release](https://img.shields.io/github/v/release/judge0/judge0-python)](https://github.com/judge0/judge0/releases)
[![Stars](https://img.shields.io/github/stars/judge0/judge0-python)](https://github.com/judge0/judge0-python/stargazers)
![PyPI - Downloads](https://img.shields.io/pypi/dw/judge0)

The official Python SDK for Judge0.
```python
>>> import judge0
>>> result = judge0.run(source_code="print('hello, world')")
>>> result.stdout
'hello, world\n'
>>> result.time
0.987
>>> result.memory
52440
>>> for f in result:
...     f.name
...     f.content
...
'script.py'
b"print('hello, world')"
```

## Installation

```bash
pip install judge0
```

### Requirements

- Python 3.10+

## Quick Start

### Getting The API Key

Get your API key from [Rapid](https://rapidapi.com/organization/judge0), or [ATD](https://www.allthingsdev.co/publisher/profile/Herman%20Zvonimir%20Do%C5%A1ilovi%C4%87).

#### Notes

* Judge0 has two flavors: Judge0 CE and Judge0 Extra CE, and their difference is just in the languages they support. When choosing Rapid and ATD you will need to explicitly subscribe to both flavors if you want to use both.

### Using Your API Key

#### Option 1: Explicit Client Object

Explicitly create a client object with your API key and pass it to Judge0 Python SDK functions.

```python
import judge0
client = judge0.RapidJudge0CE(api_key="xxx")
result = judge0.run(client=client, source_code="print('hello, world')")
print(result.stdout)
```

Other options include:
- `judge0.RapidJudge0CE`
- `judge0.ATDJudge0CE`
- `judge0.RapidJudge0ExtraCE`
- `judge0.ATDJudge0ExtraCE`

#### Option 2: Implicit Client Object

Put your API key in one of the following environment variables, respectable to the provider that issued you the API key: `JUDGE0_RAPID_API_KEY`, or `JUDGE0_ATD_API_KEY`.

Judge0 Python SDK will automatically detect the environment variable and use it to create a client object that will be used for all API calls if you do not explicitly pass a client object.

```python
import judge0
result = judge0.run(source_code="print('hello, world')")
print(result.stdout)
```

## Examples
### hello, world

```python
import judge0
result = judge0.run(source_code="print('hello, world')", language=judge0.PYTHON)
print(result.stdout)
```

### Running C Programming Language

```python
import judge0

source_code = """
#include <stdio.h>

int main() {
    printf("hello, world\\n");
    return 0;
}
"""

result = judge0.run(source_code=source_code, language=judge0.C)
print(result.stdout)
```

### Running Java Programming Language

```python
import judge0

source_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("hello, world");
    }
}
"""

result = judge0.run(source_code=source_code, language=judge0.JAVA)
print(result.stdout)
```

### Reading From Standard Input

```python
import judge0

source_code = """
#include <stdio.h>

int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d\\n", a + b);

    char name[10];
    scanf("%s", name);
    printf("Hello, %s!\\n", name);

    return 0;
}
"""

stdin = """
3 5
Bob
"""

result = judge0.run(source_code=source_code, stdin=stdin, language=judge0.C)
print(result.stdout)
```

### Test Cases

```python
import judge0

results = judge0.run(
    source_code="print(f'Hello, {input()}!')",
    test_cases=[
        ("Bob", "Hello, Bob!"), # Test Case #1. Tuple with first value as standard input, second value as expected output.
        { # Test Case #2. Dictionary with "input" and "expected_output" keys.
            "input": "Alice",
            "expected_output": "Hello, Alice!"
        },
        ["Charlie", "Hello, Charlie!"], # Test Case #3. List with first value as standard input and second value as expected output.
    ],
)

for i, result in enumerate(results):
    print(f"--- Test Case #{i + 1} ---")
    print(result.stdout)
    print(result.status)
```

### Test Cases And Multiple Languages

```python
import judge0

submissions = [
    judge0.Submission(
        source_code="print(f'Hello, {input()}!')",
        language=judge0.PYTHON,
    ),
    judge0.Submission(
        source_code="""
#include <stdio.h>

int main() {
    char name[10];
    scanf("%s", name);
    printf("Hello, %s!\\n", name);
    return 0;
}
""",
        language=judge0.C,
    ),
]

test_cases=[
    ("Bob", "Hello, Bob!"),
    ("Alice", "Hello, Alice!"),
    ("Charlie", "Hello, Charlie!"),
]

results = judge0.run(submissions=submissions, test_cases=test_cases)

for i in range(len(submissions)):
    print(f"--- Submission #{i + 1} ---")

    for j in range(len(test_cases)):
        result = results[i * len(test_cases) + j]

        print(f"--- Test Case #{j + 1} ---")
        print(result.stdout)
        print(result.status)
```

### Asynchronous Execution

```python
import judge0

submission = judge0.async_run(source_code="print('hello, world')")
print(submission.stdout) # Prints 'None'

judge0.wait(submissions=submission) # Wait for the submission to finish.

print(submission.stdout) # Prints 'hello, world'
```

### Get Languages

```python
import judge0
client = judge0.get_client()
print(client.get_languages())
```

### Running LLM-Generated Code

#### Simple Example With Ollama

```python
# pip install judge0 ollama
import os

from ollama import Client
import judge0

# Get your free tier Ollama Cloud API key at https://ollama.com.
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + os.environ.get("OLLAMA_API_KEY")},
)

system = """
You are a helpful assistant that can execute code written in the C programming language.
Only respond with the code written in the C programming language that needs to be executed and nothing else.
Strip the backticks in code blocks.
"""
prompt = "How many r's are in the word 'strawberry'?"

response = client.chat(
    model="gpt-oss:120b-cloud",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ],
)

code = response["message"]["content"]
print(f"CODE GENERATED BY THE MODEL:\n{code}\n")

result = judge0.run(source_code=code, language=judge0.C)
print(f"CODE EXECUTION RESULT:\n{result.stdout}")
```

#### Tool Calling (a.k.a. Function Calling) With Ollama

```python
# pip install judge0 ollama
import os

from ollama import Client
import judge0

# Get your free tier Ollama Cloud API key at https://ollama.com.
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + os.environ.get("OLLAMA_API_KEY")},
)

model="qwen3-coder:480b-cloud"

messages=[
    {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
]

tools = [{
    "type": "function",
    "function": {
        "name": "execute_c",
        "description": "Execute the C programming language code.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code written in the C programming language."
                }
            },
            "required": ["code"]
        }
    }
}]

response = client.chat(model=model, messages=messages, tools=tools)

response_message = response["message"]
messages.append(response_message)

if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
        if tool_call.function.name == "execute_c":
            code = tool_call.function.arguments["code"]
            print(f"CODE GENERATED BY THE MODEL:\n{code}\n")

            result = judge0.run(source_code=code, language=judge0.C)
            print(f"CODE EXECUTION RESULT:\n{result.stdout}\n")

            messages.append({
                "role": "tool",
                "tool_name": "execute_c",
                "content": result.stdout,
            })

final_response = client.chat(model=model, messages=messages)
print(f'FINAL RESPONSE BY THE MODEL:\n{final_response["message"]["content"]}')
```

#### Multi-Agent System For Iterative Code Generation, Execution, And Debugging

```python
# pip install judge0 ag2[openai]
import os
from typing import Annotated, Optional

from autogen import ConversableAgent, LLMConfig, register_function
from autogen.tools import Tool
from pydantic import BaseModel, Field
import judge0


class PythonCodeExecutionTool(Tool):
    def __init__(self) -> None:
        class CodeExecutionRequest(BaseModel):
            code: Annotated[str, Field(description="Python code to execute")]

        async def execute_python_code(
            code_execution_request: CodeExecutionRequest,
        ) -> Optional[str]:
            result = judge0.run(
                source_code=code_execution_request.code,
                language=judge0.PYTHON,
                redirect_stderr_to_stdout=True,
            )
            return result.stdout

        super().__init__(
            name="python_execute_code",
            description="Executes Python code and returns the result.",
            func_or_tool=execute_python_code,
        )


python_executor = PythonCodeExecutionTool()

# Get your free tier Ollama Cloud API key at https://ollama.com.
llm_config = LLMConfig(
    {
        "api_type": "openai",
        "base_url": "https://ollama.com/v1",
        "api_key": os.environ.get("OLLAMA_API_KEY"),
        "model": "qwen3-coder:480b-cloud",
    }
)

code_runner = ConversableAgent(
    name="code_runner",
    system_message="You are a code executor agent, when you don't execute code write the message 'TERMINATE' by itself.",
    human_input_mode="NEVER",
    llm_config=llm_config,
)

question_agent = ConversableAgent(
    name="question_agent",
    system_message=(
        "You are a developer AI agent. "
        "Send all your code suggestions to the python_executor tool where it will be executed and result returned to you. "
        "Keep refining the code until it works."
    ),
    llm_config=llm_config,
)

register_function(
    python_executor,
    caller=question_agent,
    executor=code_runner,
    description="Run Python code",
)

result = code_runner.initiate_chat(
    recipient=question_agent,
    message=(
        "Write Python code to print the current Python version followed by the numbers 1 to 11. "
        "Make a syntax error in the first version and fix it in the second version."
    ),
    max_turns=5,
)

print(f"Result: {result.summary}")
```

#### Kaggle Dataset Visualization With LLM-Generated Code Using Ollama And Judge0

```python
# pip install judge0 ollama requests
import os
import zipfile

import judge0
import requests
from judge0 import File, Filesystem
from ollama import Client

# Step 1: Download the dataset from Kaggle.
dataset_url = "https://www.kaggle.com/api/v1/datasets/download/gregorut/videogamesales"
dataset_zip_path = "vgsales.zip"
dataset_csv_path = "vgsales.csv"  # P.S.: We know the CSV file name inside the zip.

if not os.path.exists(dataset_csv_path):  # Download only if not already downloaded.
    with requests.get(dataset_url) as response:
        with open(dataset_zip_path, "wb") as f:
            f.write(response.content)
            with zipfile.ZipFile(dataset_zip_path, "r") as f:
                f.extractall(".")

# Step 2: Prepare the submission for Judge0.
with open(dataset_csv_path, "r") as f:
    submission = judge0.Submission(
        language=judge0.PYTHON_FOR_ML,
        additional_files=Filesystem(
            content=[
                File(name=dataset_csv_path, content=f.read()),
            ]
        ),
    )

# Step 3: Initialize Ollama Client. Get your free tier Ollama Cloud API key at https://ollama.com.
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + os.environ.get("OLLAMA_API_KEY")},
)

# Step 4: Prepare the prompt, messages, tools, and choose the model.
prompt = f"""
I have a CSV that contains a list of video games with sales greater than 100,000 copies. It's saved in the file {dataset_csv_path}.
These are the columns:
- 'Rank': Ranking of overall sales
- 'Name': The games name
- 'Platform': Platform of the games release (i.e. PC,PS4, etc.)
- 'Year': Year of the game's release
- 'Genre': Genre of the game
- 'Publisher': Publisher of the game
- 'NA_Sales': Sales in North America (in millions)
- 'EU_Sales': Sales in Europe (in millions)
- 'JP_Sales': Sales in Japan (in millions)
- 'Other_Sales': Sales in the rest of the world (in millions)
- 'Global_Sales': Total worldwide sales.

I want to better understand how the sales are distributed across different genres over the years.
Write Python code that analyzes the dataset based on my request, produces right chart and saves it as an image file.
"""
messages = [{"role": "user", "content": prompt}]
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Execute the Python programming language code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code written in the Python programming language.",
                    }
                },
                "required": ["code"],
            },
        },
    }
]
model = "qwen3-coder:480b-cloud"

# Step 5: Start the interaction with the model.
response = client.chat(model=model, messages=messages, tools=tools)
response_message = response["message"]

if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
        if tool_call.function.name == "execute_python":
            code = tool_call.function.arguments["code"]
            print(f"CODE GENERATED BY THE MODEL:\n{code}\n")

            submission.source_code = code
            result = judge0.run(submissions=submission)

            for f in result.post_execution_filesystem:
                if f.name.endswith((".png", ".jpg", ".jpeg")):
                    with open(f.name, "wb") as img_file:
                        img_file.write(f.content)
                    print(f"Generated image saved as: {f.name}\n")
```

#### Minimal Example Using `smolagents` With Ollama And Judge0

```python
# pip install judge0 smolagents[openai]
import os
from typing import Any

import judge0
from smolagents import CodeAgent, OpenAIServerModel, Tool
from smolagents.local_python_executor import CodeOutput, PythonExecutor


class Judge0PythonExecutor(PythonExecutor):
    def send_tools(self, tools: dict[str, Tool]) -> None:
        pass

    def send_variables(self, variables: dict[str, Any]) -> None:
        pass

    def __call__(self, code_action: str) -> CodeOutput:
        source_code = f"final_answer = lambda x : print(x)\n{code_action}"
        result = judge0.run(source_code=source_code, language=judge0.PYTHON_FOR_ML)
        return CodeOutput(
            output=result.stdout,
            logs=result.stderr or "",
            is_final_answer=result.exit_code == 0,
        )


# Get your free tier Ollama Cloud API key at https://ollama.com.
model = OpenAIServerModel(
    model_id="gpt-oss:120b-cloud",
    api_base="https://ollama.com/v1",
    api_key=os.environ["OLLAMA_API_KEY"],
)

agent = CodeAgent(tools=[], model=model)
agent.python_executor = Judge0PythonExecutor()

result = agent.run("How many r's are in the word 'strawberry'?")
print(result)
```

### Filesystem

This example shows how to use Judge0 Python SDK to:
1. Create a submission with additional files in the filesystem which will be available during the execution.
2. Read the files after the execution which were created during the execution.

```python
# pip install judge0
import judge0
from judge0 import Filesystem, File, Submission

fs = Filesystem(
    content=[
        File(name="./my_dir1/my_file1.txt", content="hello from my_file.txt"),
    ]
)

source_code = """
cat ./my_dir1/my_file1.txt

mkdir my_dir2
echo "hello, world" > ./my_dir2/my_file2.txt
"""

submission = Submission(
    source_code=source_code,
    language=judge0.BASH,
    additional_files=fs,
)

result = judge0.run(submissions=submission)

print(result.stdout)
print(result.post_execution_filesystem.find("./my_dir2/my_file2.txt"))
```

### Custom Judge0 Client

This example shows how to use Judge0 Python SDK with your own Judge0 instance.

```python
# pip install judge0
import judge0

client = judge0.Client("http://127.0.0.1:2358")

source_code = """
#include <stdio.h>

int main() {
    printf("hello, world\\n");
    return 0;
}
"""

result = judge0.run(client=client, source_code=source_code, language=judge0.C)
print(result.stdout)
```

### Generating And Saving An Image File

```python
# pip install judge0
import judge0

source_code = """
import matplotlib.pyplot as plt

plt.plot([x for x in range(10)], [x**2 for x in range(10)])
plt.savefig("chart.png")
"""

result = judge0.run(source_code=source_code, language=judge0.PYTHON_FOR_ML)

image = result.post_execution_filesystem.find("chart.png")
with open(image.name, "wb") as f:
    f.write(image.content)
print(f"Generated image saved as: {image.name}\n")
```

## Contributors

Thanks to all [contributors](https://github.com/judge0/judge0-python/graphs/contributors) for contributing to this project.

[![](https://contributors-img.web.app/image?repo=judge0/judge0-python)](https://github.com/judge0/judge0-python/graphs/contributors)

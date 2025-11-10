# Judge0 Python SDK

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

#### Simple Example with Ollama

```python
import os
from ollama import Client
import judge0

# Get your Ollama Cloud API key from https://ollama.com.
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + os.environ.get("OLLAMA_API_KEY")},
)

system = "You are a helpful assistant that can execute Python code. Only respond with the code to be executed and nothing else. Strip backticks in code blocks."
prompt = "Calculate how many r's are in the word 'strawberry'."

response = client.chat(
    model="gpt-oss:120b-cloud",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ],
)

code = response["message"]["content"]
print(f"Generated code:\n{code}")

result = judge0.run(source_code=code, language=judge0.PYTHON)
print(f"Execution result:\n{result.stdout}")
```

#### Tool Calling (a.k.a. Function Calling) with Ollama

```python
import os
from ollama import Client
import judge0

# Get your Ollama Cloud API key from https://ollama.com.
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + os.environ.get("OLLAMA_API_KEY")},
)

model="qwen3-coder:480b-cloud"

messages=[
    {"role": "user", "content": "Calculate how many r's are in the word 'strawberry'."},
]

tools = [{
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": "Execute Python code and return result",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute"
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
        if tool_call.function.name == "execute_python":
            result = judge0.run(source_code=tool_call.function.arguments["code"], language=judge0.PYTHON)
            messages.append({
                "role": "tool",
                "tool_name": "execute_python",
                "content": result.stdout,
            })

final_response = client.chat(model=model, messages=messages)
print(final_response["message"]["content"])
```

### Filesystem

```python
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

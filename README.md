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

- Python 3.9+

## Quick Start

### Getting The API Key

Get your API key from [Sulu](https://platform.sulu.sh/apis/judge0), [Rapid](https://rapidapi.com/organization/judge0), or [ATD](https://www.allthingsdev.co/publisher/profile/Herman%20Zvonimir%20Do%C5%A1ilovi%C4%87).

#### Notes

* [**Recommended**] Choose Sulu if you need pay-as-you-go (pey-per-use) pricing.
* Choose Rapid or ATD if you need a quota-based (volume-based) plan.
* Judge0 has two flavors: Judge0 CE and Judge0 Extra CE, and their difference is just in the languages they support. When choosing Sulu, your API key will work for both flavors, but for Rapid and ATD you will need to explicitly subscribe to both flavors if you want to use both.

### Using Your API Key

#### Option 1: Explicit Client Object

Explicitly create a client object with your API key and pass it to Judge0 Python SDK functions.

```python
import judge0
client = judge0.SuluJudge0CE(api_key="xxx")
result = judge0.run(client=client, source_code="print('hello, world')")
print(result.stdout)
```

Other options include:
- `judge0.RapidJudge0CE`
- `judge0.ATDJudge0CE`
- `judge0.SuluJudge0ExtraCE`
- `judge0.RapidJudge0ExtraCE`
- `judge0.ATDJudge0ExtraCE`

#### Option 2: Implicit Client Object

Put your API key in one of the following environment variables, respectable to the provider that issued you the API key: `JUDGE0_SULU_API_KEY`, `JUDGE0_RAPID_API_KEY`, or `JUDGE0_ATD_API_KEY`.

Judge0 Python SDK will automatically detect the environment variable and use it to create a client object that will be used for all API calls if you do not explicitly pass a client object.

```python
import judge0
result = judge0.run(source_code="print('hello, world')")
print(result.stdout)
```

## Examples

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

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

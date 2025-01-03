import os

import judge0

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("JUDGE0_RAPID_API_KEY")


def run_example(client_class, language_id):
    client = client_class(api_key=api_key)
    submission = judge0.Submission(
        source_code="print('Hello Judge0')",
        language=language_id,
        expected_output="Hello Judge0",
    )

    judge0.execute(client=client, submissions=submission)

    print(f"{submission.status=}")
    print(f"{submission.stdout=}")


def main():
    run_example(judge0.RapidJudge0CE, 100)
    run_example(judge0.RapidJudge0ExtraCE, 25)


if __name__ == "__main__":
    main()

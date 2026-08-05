import judge0

submissions = judge0.run(
    source_code="print(f'hello {input()}')",
    test_cases=[
        ("tuple", "hello tuple"),
        {"input": "dict", "expected_output": "hello dict"},
        ["list", "hello list"],
    ],
)

submissions = judge0.run(submissions=submissions)

for submission in submissions:
    print(submission.status)

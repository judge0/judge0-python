import judge0

print("Subexample 1")
result = judge0.run(
    source_code="print(f'Hello, {input()}')",
    test_cases=("Herman", "Hello, Herman"),
)

print(result.status)





print("Subexample 2")
results = judge0.run(
    source_code="print(f'Hello, {input()}')",
    test_cases=[
        ("Herman", "Hello, Herman"),
        ("Filip", "Hello, Filip"),
    ],
)

for result in results:
    print(result.status)





print("Subexample 3")
submission = judge0.Submission(source_code="print(f'Hello, {input()}')")
result = judge0.run(
    submissions=submission,
    test_cases=("Herman", "Hello, Herman"),
)

print(result.status)





print("Subexample 4")
submissions = [
    judge0.Submission(source_code="print(f'Hello, {input()}')"),
    judge0.Submission(source_code="print(f'Bok, {input()}')")
]
results = judge0.run(
    submissions=submissions,
    test_cases=("Herman", "Hello, Herman"),
)

for result in results:
    print(result.status)





print("Subexample 5")
submissions = [
    judge0.Submission(source_code="print(f'Hello, {input()}')"),
    judge0.Submission(source_code="print(f'Bok, {input()}')")
]
results = judge0.run(
    submissions=submissions,
    test_cases=[
        ("Herman", "Hello, Herman"),
        ("Filip", "Hello, Filip"),
    ],
)

for result in results:
    print(result.status)

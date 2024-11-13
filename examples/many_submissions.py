import judge0

submissions = []
for i in range(42):
    submissions.append(judge0.Submission(
        source_code=f"print({i})",
    ))

results = judge0.run(submissions=submissions)
for result in results:
    print(result.stdout.strip(), " ", end="")
print()

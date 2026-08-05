#!/usr/bin/env python3
import asyncio
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI

import judge0


class AppContext:
    def __init__(self):
        self.public_url = ""


LOCAL_SERVER_PORT = 8000

app = FastAPI()
app_context = AppContext()


def get_app_context():
    return app_context


@app.get("/")
async def root(app_context: Annotated[AppContext, Depends(get_app_context)]):
    if not app_context.public_url:
        return {
            "message": "Public URL is not available yet. Try again after a few seconds."
        }

    submission = judge0.Submission(
        source_code="print('Hello, World!')",
        language_id=judge0.PYTHON,
        callback_url=f"{app_context.public_url}/callback",
    )

    return judge0.async_execute(submissions=submission)


@app.put("/callback")
async def callback(response: judge0.Submission):
    print(f"Received: {response}")


# We are using free service from https://localhost.run to get a public URL for
# our local server. This approach is not recommended for production use. It is
# only for demonstration purposes since domain names change regularly and there
# is a speed limit for the free service.
async def run_ssh_tunnel():
    app_context = get_app_context()

    command = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ServerAliveInterval=30",
        "-R",
        f"80:localhost:{LOCAL_SERVER_PORT}",
        "localhost.run",
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    while True:
        line = await process.stdout.readline()
        if not line:
            break

        decoded_line = line.decode().strip()
        if decoded_line.endswith(".lhr.life"):
            app_context.public_url = decoded_line.split()[-1].strip()

    await process.wait()


async def run_server():
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=LOCAL_SERVER_PORT,
        workers=5,
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(run_ssh_tunnel(), run_server())


if __name__ == "__main__":
    asyncio.run(main())

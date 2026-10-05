import json
from base64 import b64encode

import httpx2
import pytest

from judge0 import Submission, clients
from judge0.version import __version__


def test_httpx2_client_initialization_and_submission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert getattr(clients, "httpx2", None) is httpx2

    config = {
        "allow_enable_network": True,
        "allow_enable_per_process_and_thread_memory_limit": True,
        "allow_enable_per_process_and_thread_time_limit": True,
        "allowed_languages_for_compile_options": [],
        "callbacks_max_tries": 3,
        "callbacks_timeout": 5.0,
        "cpu_extra_time": 1.0,
        "cpu_time_limit": 2.0,
        "enable_additional_files": True,
        "enable_batched_submissions": True,
        "enable_callbacks": True,
        "enable_command_line_arguments": True,
        "enable_compiler_options": True,
        "enable_network": False,
        "enable_per_process_and_thread_memory_limit": False,
        "enable_per_process_and_thread_time_limit": False,
        "enable_submission_delete": False,
        "enable_wait_result": False,
        "maintenance_mode": False,
        "max_cpu_extra_time": 5.0,
        "max_cpu_time_limit": 15.0,
        "max_extract_size": 10240,
        "max_file_size": 1024,
        "max_max_file_size": 4096,
        "max_max_processes_and_or_threads": 120,
        "max_memory_limit": 512000,
        "max_number_of_runs": 20,
        "max_processes_and_or_threads": 60,
        "max_queue_size": 100,
        "max_stack_limit": 128000,
        "max_submission_batch_size": 20,
        "max_wall_time_limit": 20.0,
        "memory_limit": 128000,
        "number_of_runs": 1,
        "redirect_stderr_to_stdout": False,
        "stack_limit": 64000,
        "submission_cache_duration": 1.0,
        "use_docs_as_homepage": True,
        "wall_time_limit": 5.0,
    }
    requests: list[httpx2.Request] = []
    token = "5513d8ca-975b-4499-b54b-342f1952d00e"

    def handle_request(request: httpx2.Request) -> httpx2.Response:
        """Return mock Judge0 responses.

        Raises
        ------
        AssertionError
            If the SDK requests an unexpected endpoint.
        """
        requests.append(request)
        if request.url.path == "/api/languages":
            return httpx2.Response(200, json=[{"id": 100, "name": "Python (3.12.5)"}])
        if request.url.path == "/api/config_info":
            return httpx2.Response(200, json=config)
        assert request.url.path == "/api/submissions"
        return httpx2.Response(201, json={"token": token})

    http_client_type = httpx2.Client

    def make_http_client(base_url: str) -> httpx2.Client:
        return http_client_type(
            base_url=base_url, transport=httpx2.MockTransport(handle_request)
        )

    monkeypatch.setattr(httpx2, "Client", make_http_client)
    client = clients.Client(
        endpoint="https://judge0.example/api", headers={"X-Auth-Token": "test-token"}
    )
    try:
        assert isinstance(client.client, http_client_type)
        assert client.languages[0].id == 100
        assert client.languages[0].name == "Python (3.12.5)"
        assert client.config.cpu_time_limit == 2.0
        assert client.config.enable_batched_submissions is True

        submission = Submission(source_code="print('hello')", language=100)
        assert client.create_submission(submission) is submission
        assert str(submission.token) == token

        assert [(request.method, request.url.path) for request in requests] == [
            ("GET", "/api/languages"),
            ("GET", "/api/config_info"),
            ("POST", "/api/submissions"),
        ]
        for request in requests:
            assert request.url.host == "judge0.example"
            assert request.headers["X-Auth-Token"] == "test-token"
            assert request.headers["X-Judge0-App"] == "Judge0 Python SDK"
            assert request.headers["X-Judge0-App-Version"] == __version__

        request = requests[-1]
        assert dict(request.url.params) == {"base64_encoded": "true", "wait": "false"}
        assert request.headers["Content-Type"] == "application/json"
        body = json.loads(request.content)
        assert body["language_id"] == 100
        assert body["source_code"] == b64encode(b"print('hello')").decode()
    finally:
        client.client.close()

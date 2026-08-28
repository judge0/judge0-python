import asyncio
from typing import Any

import httpx

from judge0 import Client
from judge0.clients import AsyncClient
from judge0.submission import Submission

CONFIG_PAYLOAD: dict[str, Any] = {
    "allow_enable_network": False,
    "allow_enable_per_process_and_thread_memory_limit": False,
    "allow_enable_per_process_and_thread_time_limit": False,
    "allowed_languages_for_compile_options": [],
    "callbacks_max_tries": 1,
    "callbacks_timeout": 1.0,
    "cpu_extra_time": 0.0,
    "cpu_time_limit": 1.0,
    "enable_additional_files": False,
    "enable_batched_submissions": True,
    "enable_callbacks": False,
    "enable_command_line_arguments": False,
    "enable_compiler_options": False,
    "enable_network": False,
    "enable_per_process_and_thread_memory_limit": False,
    "enable_per_process_and_thread_time_limit": False,
    "enable_submission_delete": False,
    "enable_wait_result": False,
    "maintenance_mode": False,
    "max_cpu_extra_time": 1.0,
    "max_cpu_time_limit": 1.0,
    "max_extract_size": 1,
    "max_file_size": 1,
    "max_max_file_size": 1,
    "max_max_processes_and_or_threads": 1,
    "max_memory_limit": 1,
    "max_number_of_runs": 1,
    "max_processes_and_or_threads": 1,
    "max_queue_size": 1,
    "max_stack_limit": 1,
    "max_submission_batch_size": 2,
    "max_wall_time_limit": 1.0,
    "memory_limit": 1,
    "wall_time_limit": 1.0,
    "number_of_runs": 1,
    "redirect_stderr_to_stdout": False,
    "stack_limit": 1,
    "submission_cache_duration": 0.0,
    "use_docs_as_homepage": False,
}

LANGUAGES_PAYLOAD = [
    {"id": 89, "name": "Multi File Program"},
    {"id": 92, "name": "Python (3.11.2)"},
]


def _mock_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path.endswith("/about"):
            return httpx.Response(200, json={"version": "1.13.1"})
        if request.method == "GET" and path.endswith("/config_info"):
            return httpx.Response(200, json=CONFIG_PAYLOAD)
        if request.method == "GET" and path.endswith("/languages"):
            return httpx.Response(200, json=LANGUAGES_PAYLOAD)
        if request.method == "GET" and path.endswith("/statuses"):
            return httpx.Response(200, json=[{"id": 3, "description": "Accepted"}])
        if request.method == "GET" and "/languages/" in path:
            return httpx.Response(200, json={"id": 92, "name": "Python (3.11.2)"})
        if request.method == "POST" and path.endswith("/submissions/batch"):
            return httpx.Response(201, json=[{"token": "t1"}, {"token": "t2"}])
        if request.method == "POST" and path.endswith("/submissions"):
            return httpx.Response(201, json={"token": "tok-1"})
        if request.method == "GET" and path.endswith("/submissions/batch"):
            return httpx.Response(
                200,
                json={
                    "submissions": [
                        {"token": "t1", "status": {"id": 3, "description": "Accepted"}},
                        {"token": "t2", "status": {"id": 3, "description": "Accepted"}},
                    ]
                },
            )
        if request.method == "GET" and "/submissions/" in path:
            return httpx.Response(
                200,
                json={
                    "token": "tok-1",
                    "status": {"id": 3, "description": "Accepted"},
                    "stdout": "aGVsbG8K",
                },
            )
        return httpx.Response(404, json={"error": path})

    return httpx.MockTransport(handler)


def _sync_http_client() -> httpx.Client:
    return httpx.Client(
        base_url="https://example.invalid",
        transport=_mock_transport(),
    )


def _async_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url="https://example.invalid",
        transport=_mock_transport(),
    )


def test_client_uses_injected_http_client_for_get_about() -> None:
    http_client = _sync_http_client()
    client = Client(
        endpoint="https://example.invalid",
        http_client=http_client,
    )
    about = client.get_about()
    assert about["version"] == "1.13.1"
    client.close()


def test_async_client_get_about() -> None:
    async def _run() -> None:
        http_client = _async_http_client()
        client = AsyncClient(
            endpoint="https://example.invalid",
            http_client=http_client,
        )
        about = await client.get_about()
        assert about["version"] == "1.13.1"
        await client.aclose()

    asyncio.run(_run())


def test_async_client_reads_languages_statuses_and_config() -> None:
    async def _run() -> None:
        client = AsyncClient(
            endpoint="https://example.invalid",
            http_client=_async_http_client(),
        )
        languages = await client.get_languages()
        statuses = await client.get_statuses()
        config = await client.get_config_info()
        language = await client.get_language(92)
        assert languages[0].id == 89
        assert statuses[0]["id"] == 3
        assert config.cpu_time_limit == 1.0
        assert language.id == 92
        await client.aclose()

    asyncio.run(_run())


def test_async_client_create_and_get_submission() -> None:
    async def _run() -> None:
        client = AsyncClient(
            endpoint="https://example.invalid",
            http_client=_async_http_client(),
        )
        submission = Submission(source_code="print(1)", language=92)
        created = await client.create_submission(submission)
        assert created.token == "tok-1"
        fetched = await client.get_submission(created)
        assert fetched.status is not None
        await client.aclose()

    asyncio.run(_run())


def test_async_client_create_and_get_submissions_batch() -> None:
    async def _run() -> None:
        client = AsyncClient(
            endpoint="https://example.invalid",
            http_client=_async_http_client(),
        )
        submissions = [
            Submission(source_code="print(1)", language=92),
            Submission(source_code="print(2)", language=92),
        ]
        created = await client.create_submissions(submissions)
        assert [item.token for item in created] == ["t1", "t2"]
        fetched = await client.get_submissions(created)
        assert all(item.status is not None for item in fetched)
        await client.aclose()

    asyncio.run(_run())


def test_async_rapid_client_sets_auth_headers() -> None:
    async def _run() -> None:
        from judge0.clients import AsyncRapidJudge0CE

        client = AsyncRapidJudge0CE(
            api_key="rapid-key",
            http_client=_async_http_client(),
        )
        await client.get_about()
        assert client.headers["x-rapidapi-key"] == "rapid-key"
        assert client.headers["x-rapidapi-host"] == "judge0-ce.p.rapidapi.com"
        await client.aclose()

    asyncio.run(_run())


def test_async_atd_client_sets_operation_endpoint_header() -> None:
    captured: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request.headers.get("x-apihub-endpoint"))
        path = request.url.path
        if path.endswith("/about"):
            return httpx.Response(200, json={"version": "1.13.1"})
        if path.endswith("/config_info"):
            return httpx.Response(200, json=CONFIG_PAYLOAD)
        if path.endswith("/languages"):
            return httpx.Response(200, json=LANGUAGES_PAYLOAD)
        return httpx.Response(404)

    async def _run() -> None:
        from judge0.clients import AsyncATDJudge0CE

        http_client = httpx.AsyncClient(
            base_url="https://example.invalid",
            transport=httpx.MockTransport(handler),
        )
        client = AsyncATDJudge0CE(api_key="atd-key", http_client=http_client)
        await client.get_about()
        assert AsyncATDJudge0CE.DEFAULT_LANGUAGES_ENDPOINT in captured
        assert AsyncATDJudge0CE.DEFAULT_CONFIG_INFO_ENDPOINT in captured
        assert AsyncATDJudge0CE.DEFAULT_ABOUT_ENDPOINT in captured
        await client.aclose()

    asyncio.run(_run())


def test_async_cloud_client_uses_cloud_endpoint() -> None:
    async def _run() -> None:
        from judge0.clients import AsyncJudge0CloudCE

        client = AsyncJudge0CloudCE(
            headers={"Authorization": "Bearer x"},
            http_client=_async_http_client(),
        )
        await client.get_about()
        assert client.endpoint == "https://ce.judge0.com"
        await client.aclose()

    asyncio.run(_run())


def test_async_client_context_manager() -> None:
    async def _run() -> None:
        http_client = _async_http_client()
        async with AsyncClient(
            endpoint="https://example.invalid",
            http_client=http_client,
        ) as client:
            about = await client.get_about()
            assert about["version"] == "1.13.1"

    asyncio.run(_run())

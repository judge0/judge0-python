from typing import Union

from .common import decode, encode, Language, Status

ENCODED_REQUEST_FIELDS = {
    "additional_files",
    "expected_output",
    "source_code",
    "stdin",
}
ENCODED_RESPONSE_FIELDS = {"stdout", "stderr", "compile_output"}
ENCODED_FIELDS = ENCODED_REQUEST_FIELDS | ENCODED_RESPONSE_FIELDS
EXTRA_REQUEST_FIELDS = {
    "callback_url",
    "command_line_arguments",
    "compiler_options",
    "cpu_extra_time",
    "cpu_time_limit",
    "enable_network",
    "enable_per_process_and_thread_memory_limit",
    "enable_per_process_and_thread_time_limit",
    "max_file_size",
    "max_processes_and_or_threads",
    "memory_limit",
    "number_of_runs",
    "redirect_stderr_to_stdout",
    "stack_limit",
    "wall_time_limit",
}
EXTRA_RESPONSE_FIELDS = {
    "created_at",
    "exit_code",
    "exit_signal",
    "finished_at",
    "memory",
    "message",
    "post_execution_filesystem",
    "status",
    "time",
    "token",
    "wall_time",
}
REQUEST_FIELDS = ENCODED_REQUEST_FIELDS | EXTRA_REQUEST_FIELDS
RESPONSE_FIELDS = ENCODED_RESPONSE_FIELDS | EXTRA_RESPONSE_FIELDS
FIELDS = REQUEST_FIELDS | RESPONSE_FIELDS
SKIP_FIELDS = {"language_id", "language", "status_id"}


class Submission:
    """
    Stores a representation of a Submission to/from Judge0.
    """

    def __init__(
        self,
        source_code: str,
        language_id: Union[Language, int] = Language.PYTHON,
        *,
        additional_files=None,
        compiler_options=None,
        command_line_arguments=None,
        stdin=None,
        expected_output=None,
        cpu_time_limit=None,
        cpu_extra_time=None,
        wall_time_limit=None,
        memory_limit=None,
        stack_limit=None,
        max_processes_and_or_threads=None,
        enable_per_process_and_thread_time_limit=None,
        enable_per_process_and_thread_memory_limit=None,
        max_file_size=None,
        redirect_stderr_to_stdout=None,
        enable_network=None,
        number_of_runs=None,
        callback_url=None,
    ):
        self.source_code = source_code
        self.language_id = language_id
        self.additional_files = additional_files

        # Extra pre-execution submission attributes.
        self.compiler_options = compiler_options
        self.command_line_arguments = command_line_arguments
        self.stdin = stdin
        self.expected_output = expected_output
        self.cpu_time_limit = cpu_time_limit
        self.cpu_extra_time = cpu_extra_time
        self.wall_time_limit = wall_time_limit
        self.memory_limit = memory_limit
        self.stack_limit = stack_limit
        self.max_processes_and_or_threads = max_processes_and_or_threads
        self.enable_per_process_and_thread_time_limit = (
            enable_per_process_and_thread_time_limit
        )
        self.enable_per_process_and_thread_memory_limit = (
            enable_per_process_and_thread_memory_limit
        )
        self.max_file_size = max_file_size
        self.redirect_stderr_to_stdout = redirect_stderr_to_stdout
        self.enable_network = enable_network
        self.number_of_runs = number_of_runs
        self.callback_url = callback_url

        # Post-execution submission attributes.
        self.stdout = None
        self.stderr = None
        self.compile_output = None
        self.message = None
        self.exit_code = None
        self.exit_signal = None
        self.status = None
        self.created_at = None
        self.finished_at = None
        self.token = ""
        self.time = None
        self.wall_time = None
        self.memory = None
        self.post_execution_filesystem = None

    def set_attributes(self, attributes):
        for attr, value in attributes.items():
            if attr in SKIP_FIELDS:
                continue

            if attr in ENCODED_FIELDS:
                setattr(self, attr, decode(value) if value else None)
            else:
                setattr(self, attr, value)

    # TODO: Rename to as_body that accepts a Client.
    def to_dict(self) -> dict:
        body = {
            "source_code": encode(self.source_code),
            "language_id": self.language_id,
        }

        for field in ENCODED_REQUEST_FIELDS:
            value = getattr(self, field)
            if value is not None:
                body[field] = encode(value)

        for field in EXTRA_REQUEST_FIELDS:
            value = getattr(self, field)
            if value is not None:
                body[field] = value

        return body

    def is_done(self) -> bool:
        if self.status is None:
            return False
        else:
            # TODO: When status is changed to `Status`, refactor this as well.
            return self.status["id"] not in (Status.IN_QUEUE, Status.PROCESSING)

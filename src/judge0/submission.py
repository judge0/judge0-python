import copy
from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, UUID4

from .base_types import Iterable, LanguageAlias, Status
from .common import decode, encode
from .filesystem import Filesystem

ENCODED_REQUEST_FIELDS = {
    "source_code",
    "additional_files",
    "stdin",
    "expected_output",
}
ENCODED_RESPONSE_FIELDS = {
    "stdout",
    "stderr",
    "compile_output",
    # "post_execution_filesystem",
}
ENCODED_FIELDS = ENCODED_REQUEST_FIELDS | ENCODED_RESPONSE_FIELDS
EXTRA_REQUEST_FIELDS = {
    "compiler_options",
    "command_line_arguments",
    "cpu_time_limit",
    "cpu_extra_time",
    "wall_time_limit",
    "memory_limit",
    "stack_limit",
    "max_processes_and_or_threads",
    "enable_per_process_and_thread_time_limit",
    "enable_per_process_and_thread_memory_limit",
    "max_file_size",
    "redirect_stderr_to_stdout",
    "enable_network",
    "number_of_runs",
    "callback_url",
}
EXTRA_RESPONSE_FIELDS = {
    "message",
    "exit_code",
    "exit_signal",
    "status",
    "created_at",
    "finished_at",
    "token",
    "time",
    "wall_time",
    "memory",
}
REQUEST_FIELDS = ENCODED_REQUEST_FIELDS | EXTRA_REQUEST_FIELDS
RESPONSE_FIELDS = ENCODED_RESPONSE_FIELDS | EXTRA_RESPONSE_FIELDS
FIELDS = REQUEST_FIELDS | RESPONSE_FIELDS
SKIP_FIELDS = {"language_id", "language", "status_id"}
DATETIME_FIELDS = {"created_at", "finished_at"}
FLOATING_POINT_FIELDS = {
    "cpu_time_limit",
    "cpu_extra_time",
    "time",
    "wall_time",
    "wall_time_limit",
}

Submissions = Iterable["Submission"]


class Submission(BaseModel):
    """
    Stores a representation of a Submission to/from Judge0.

    Parameters
    ----------
    source_code : str, optional
        The source code to be executed.
    language : LanguageAlias or int, optional
        The programming language of the source code. Defaults to `LanguageAlias.PYTHON`.
    additional_files : base64 encoded string, optional
        Additional files that should be available alongside the source code.
        Value of this string should represent the content of a .zip that
        contains additional files. This attribute is required for multi-file
        programs.
    compiler_options : str, optional
        Options for the compiler (i.e. compiler flags).
    command_line_arguments : str, optional
        Command line arguments for the program.
    stdin : str, optional
        Input to be fed via standard input during execution.
    expected_output : str, optional
        The expected output of the program.
    cpu_time_limit : float, optional
        Maximum CPU time allowed for execution, in seconds. Time in which the
        OS assigns the processor to different tasks is not counted. Depends on
        configuration.
    cpu_extra_time : float, optional
        Additional CPU time allowance in case of time extension. Depends on
        configuration.
    wall_time_limit : float, optional
        Maximum wall clock time allowed for execution, in seconds. Depends on
        configuration.
    memory_limit : float, optional
        Maximum memory allocation allowed for the process, in kilobytes.
        Depends on configuration.
    stack_limit : int, optional
        Maximum stack size allowed, in kilobytes. Depends on configuration.
    max_processes_and_or_threads : int, optional
        Maximum number of processes and/or threads program can create. Depends
        on configuration.
    enable_per_process_and_thread_time_limit : bool, optional
        If True, enforces time limits per process/thread. Depends on
        configuration.
    enable_per_process_and_thread_memory_limit : bool, optional
        If True, enforces memory limits per process/thread. Depends on
        configuration.
    max_file_size : int, optional
        Maximum file size allowed for output files, in kilobytes. Depends on
        configuration.
    redirect_stderr_to_stdout : bool, optional
        If True, redirects standard error output to standard output.
    enable_network : bool, optional
        If True, enables network access during execution.
    number_of_runs : int, optional
        Number of times the code should be executed.
    callback_url : str, optional
        URL for a callback to report execution results or status.
    """

    source_code: Optional[Union[str, bytes]] = Field(default=None, repr=True)
    language: Union[LanguageAlias, int] = Field(
        default=LanguageAlias.PYTHON_FOR_ML,
        repr=True,
    )
    additional_files: Optional[Union[str, Filesystem]] = Field(default=None, repr=True)
    compiler_options: Optional[str] = Field(default=None, repr=True)
    command_line_arguments: Optional[str] = Field(default=None, repr=True)
    stdin: Optional[str] = Field(default=None, repr=True)
    expected_output: Optional[str] = Field(default=None, repr=True)
    cpu_time_limit: Optional[float] = Field(default=None, repr=True)
    cpu_extra_time: Optional[float] = Field(default=None, repr=True)
    wall_time_limit: Optional[float] = Field(default=None, repr=True)
    memory_limit: Optional[float] = Field(default=None, repr=True)
    stack_limit: Optional[int] = Field(default=None, repr=True)
    max_processes_and_or_threads: Optional[int] = Field(default=None, repr=True)
    enable_per_process_and_thread_time_limit: Optional[bool] = Field(
        default=None, repr=True
    )
    enable_per_process_and_thread_memory_limit: Optional[bool] = Field(
        default=None, repr=True
    )
    max_file_size: Optional[int] = Field(default=None, repr=True)
    redirect_stderr_to_stdout: Optional[bool] = Field(default=None, repr=True)
    enable_network: Optional[bool] = Field(default=None, repr=True)
    number_of_runs: Optional[int] = Field(default=None, repr=True)
    callback_url: Optional[str] = Field(default=None, repr=True)

    # Post-execution submission attributes.
    stdout: Optional[str] = Field(default=None, repr=True)
    stderr: Optional[str] = Field(default=None, repr=True)
    compile_output: Optional[str] = Field(default=None, repr=True)
    message: Optional[str] = Field(default=None, repr=True)
    exit_code: Optional[int] = Field(default=None, repr=True)
    exit_signal: Optional[int] = Field(default=None, repr=True)
    status: Optional[Status] = Field(default=None, repr=True)
    created_at: Optional[datetime] = Field(default=None, repr=True)
    finished_at: Optional[datetime] = Field(default=None, repr=True)
    token: Optional[UUID4] = Field(default=None, repr=True)
    time: Optional[float] = Field(default=None, repr=True)
    wall_time: Optional[float] = Field(default=None, repr=True)
    memory: Optional[float] = Field(default=None, repr=True)
    post_execution_filesystem: Optional[Filesystem] = Field(default=None, repr=True)

    model_config = ConfigDict(extra="ignore")

    @field_validator(*ENCODED_FIELDS, mode="before")
    @classmethod
    def process_encoded_fields(cls, value: str) -> Optional[str]:
        """Validate all encoded attributes."""
        if value is None:
            return None
        else:
            try:
                return decode(value)
            except Exception:
                return value

    @field_validator("post_execution_filesystem", mode="before")
    @classmethod
    def process_post_execution_filesystem(cls, content: str) -> Filesystem:
        """Validate post_execution_filesystem attribute."""
        return Filesystem(content=content)

    @field_validator("status", mode="before")
    @classmethod
    def process_status(cls, value: dict) -> Status:
        """Validate status attribute."""
        return Status(value["id"])

    @field_validator("language", mode="before")
    @classmethod
    def process_language(
        cls, value: Union[LanguageAlias, dict]
    ) -> Union[LanguageAlias, int]:
        """Validate status attribute."""
        if isinstance(value, dict):
            return value["id"]
        else:
            return value

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        """Set submissions attributes while taking into account different
        attribute's types.

        Parameters
        ----------
        attributes : dict
            Key-value pairs of Submission attributes and the corresponding
            value.
        """
        for attr, value in attributes.items():
            if attr in SKIP_FIELDS:
                continue

            if attr in ENCODED_FIELDS:
                value = decode(value) if value else None
            elif attr == "status":
                value = Status(value["id"])
            elif attr in DATETIME_FIELDS and value is not None:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif attr in FLOATING_POINT_FIELDS and value is not None:
                value = float(value)
            elif attr == "post_execution_filesystem":
                value = Filesystem(content=value)

            setattr(self, attr, value)

    def as_body(self, client: "Client") -> dict:
        """Prepare Submission as a dictionary while taking into account
        the client's restrictions.
        """
        body = {
            "source_code": encode(self.source_code),
            "language_id": client.get_language_id(self.language),
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
        """Check if submission is finished processing.

        Submission is considered finished if the submission status is not
        IN_QUEUE and not PROCESSING.
        """
        if self.status is None:
            return False
        else:
            return self.status not in (Status.IN_QUEUE, Status.PROCESSING)

    def pre_execution_copy(self) -> "Submission":
        """Create a deep copy of a submission."""
        new_submission = Submission()
        for attr in REQUEST_FIELDS:
            setattr(new_submission, attr, copy.deepcopy(getattr(self, attr)))
        new_submission.language = self.language
        return new_submission

    def __iter__(self):
        if self.post_execution_filesystem is None:
            return iter([])
        else:
            return iter(self.post_execution_filesystem)

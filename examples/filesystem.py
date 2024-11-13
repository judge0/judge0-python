from base64 import b64decode, b64encode
import zipfile
import io
import judge0
from typing import Optional, Union, Iterable
import collections.abc
import copy


class File:
    def __init__(self, name: str, content: Optional[Union[str, bytes]] = None):
        self.name = name

        if isinstance(content, str):
            self.content = content.encode()
        elif isinstance(content, bytes):
            self.content = content
        else:
            self.content = None

    def __str__(self):
        return self.content.decode(errors="backslashreplace") if self.content else ""


class Filesystem:
    def __init__(
        self,
        content: Optional[Union[str, bytes, File, Iterable[File], "Filesystem"]] = None,
    ):
        self.files: list[File] = []

        if isinstance(content, (str, bytes)):
            zip_bytes = (
                b64decode(content.encode()) if isinstance(content, str) else content
            )
            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
                for file_name in zip_file.namelist():
                    with zip_file.open(file_name) as file:
                        self.files.append(File(file_name, file.read()))
        elif isinstance(content, collections.abc.Iterable):
            self.files = content
        elif isinstance(content, File):
            self.files = [content]
        elif isinstance(content, Filesystem):
            self.files = copy.deepcopy(content.files)

    def encode(self) -> bytes:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for file in self.files:
                zip_file.writestr(file.name, file.content)
        return zip_buffer.getvalue()

    def __str__(self) -> str:
        return b64encode(self.encode()).decode()

    def __iter__(self):
        return iter(self.files)


print("Subexample 1")
result = judge0.run(source_code="print('hello, world')")
fs = Filesystem(result.post_execution_filesystem)
for f in fs:
    print(f.name)
    print(f)
    print()


print("Subexample 2")
fs = Filesystem(File("my_file.txt", "hello, world"))
result = judge0.run(source_code="print(open('my_file.txt').read())", additional_files=fs)
print(result.stdout)
for f in Filesystem(result.post_execution_filesystem):
    print(f.name)
    print(f)
    print()


print("Subexample 3")
fs = Filesystem([
    File("my_file.txt", "hello, world"),
    File("./dir1/dir2/dir3/my_file2.txt", "hello, world2"),
])
result = judge0.run(source_code="find .", additional_files=fs, language_id=46)
print(result.stdout)
for f in Filesystem(result.post_execution_filesystem):
    print(f.name)
    print(f)
    print()

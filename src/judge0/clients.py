from typing import Any, ClassVar, cast

import httpx

from .base_types import (
    Config,
    Headers,
    Iterable,
    JsonObject,
    Language,
    LanguageAlias,
)
from .data import LANGUAGE_TO_LANGUAGE_ID
from .retry import RetryStrategy
from .submission import Submission, Submissions
from .utils import handle_too_many_requests_error_for_free_tier_cloud_client
from .version import __version__


class Client:
    """Base class for all clients.

    Parameters
    ----------
    endpoint : str
        Client's default endpoint.
    headers : dict
        Request authentication headers.

    Attributes
    ----------
    API_KEY_ENV : str
        Environment variable where judge0-python should look for API key for
        the client. Set to default values for RapidAPI and ATD clients.
    """

    # Environment variable where judge0-python should look for API key for
    # the client. Set to default values for RapidAPI and ATD clients.
    API_KEY_ENV: ClassVar[str | None] = None

    def __init__(
        self,
        endpoint: str,
        headers: Headers | None = None,
        *,
        retry_strategy: RetryStrategy | None = None,
    ) -> None:
        self.endpoint: str = endpoint
        self.headers: Headers = headers if headers is not None else {}
        self.headers.update(
            {
                "X-Judge0-App": "Judge0 Python SDK",
                "X-Judge0-App-Version": __version__,
            }
        )
        self.retry_strategy = retry_strategy
        self.client = httpx.Client(base_url=self.endpoint)
        self._version: str | None = None

        try:
            self.languages = self.get_languages()
            self.config = self.get_config_info()
        except Exception as e:
            home_url = getattr(self, "HOME_URL", None)
            raise RuntimeError(
                f"Authentication failed. Visit {home_url} to get or "
                "review your authentication credentials."
            ) from e

    def __del__(self) -> None:
        self.client.close()

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_about(self) -> JsonObject:
        """Get general information about judge0.

        Returns
        -------
        dict
            General information about judge0.
        """
        response = self.client.get(
            "/about",
            headers=self.headers,
        )
        response.raise_for_status()
        return cast(JsonObject, response.json())

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_config_info(self) -> Config:
        """Get information about client's configuration.

        Returns
        -------
        Config
            Client's configuration.
        """
        response = self.client.get(
            "/config_info",
            headers=self.headers,
        )
        response.raise_for_status()
        return Config.model_validate(response.json())

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_language(self, language_id: int) -> Language:
        """Get language corresponding to the id.

        Parameters
        ----------
        language_id : int
            Language id.

        Returns
        -------
        Language
            Language corresponding to the passed id.
        """
        request_url = f"/languages/{language_id}"
        response = self.client.get(request_url, headers=self.headers)
        response.raise_for_status()
        return Language.model_validate(response.json())

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_languages(self) -> list[Language]:
        """Get a list of supported languages.

        Returns
        -------
        list of language
            A list of supported languages.
        """
        response = self.client.get("/languages", headers=self.headers)
        response.raise_for_status()
        languages = cast(list[JsonObject], response.json())
        return [Language.model_validate(language) for language in languages]

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_statuses(self) -> list[JsonObject]:
        """Get a list of possible submission statuses.

        Returns
        -------
        list of dict
            A list of possible submission statues.
        """
        response = self.client.get(
            "/statuses",
            headers=self.headers,
        )
        response.raise_for_status()
        return cast(list[JsonObject], response.json())

    @property
    def version(self) -> str:
        """Property corresponding to the current client's version."""
        if self._version is None:
            self._version = cast(str, self.get_about()["version"])
        return self._version

    def get_language_id(self, language: LanguageAlias | int) -> int:
        """Get language id corresponding to the language alias for the client.

        Parameters
        ----------
        language : LanguageAlias or int
            Language alias or language id.

        Returns
        -------
            Language id corresponding to the language alias.
        """
        if isinstance(language, LanguageAlias):
            supported_language_ids = LANGUAGE_TO_LANGUAGE_ID[self.version]
            language = supported_language_ids.get(language, -1)
        return language

    def is_language_supported(self, language: LanguageAlias | int) -> bool:
        """Check if language is supported by the client.

        Parameters
        ----------
        language : LanguageAlias or int
            Language alias or language id.

        Returns
        -------
        bool
            Return True if language is supported by the client, otherwise returns
            False.
        """
        language_id = self.get_language_id(language)
        return any(language_id == lang.id for lang in self.languages)

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def create_submission(self, submission: Submission) -> Submission:
        """Send submission for execution to a client.

        Directly send a submission to create_submission route for execution.

        Parameters
        ----------
        submission : Submission
            A submission to create.

        Returns
        -------
        Submission
            A submission with updated token attribute.
        """
        # Check if the client supports the language specified in the submission.
        if not self.is_language_supported(language=submission.language):
            raise RuntimeError(
                f"Client {type(self).__name__} does not support language with "
                f"id {submission.language}!"
            )

        params = {
            "base64_encoded": "true",
            "wait": "false",
        }

        body = submission.as_body(self)

        response = self.client.post(
            "/submissions",
            json=body,
            params=params,
            headers=self.headers,
        )
        response.raise_for_status()

        submission.set_attributes(response.json())

        return submission

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_submission(
        self,
        submission: Submission,
        *,
        fields: str | Iterable[str] | None = None,
    ) -> Submission:
        """Get submissions status.

        Directly send submission's token to get_submission route for status
        check. By default, all submissions attributes (fields) are requested.

        Parameters
        ----------
        submission : Submission
            Submission to update.

        Returns
        -------
        Submission
            A Submission with updated attributes.
        """
        params = {
            "base64_encoded": "true",
        }

        if isinstance(fields, str):
            fields = [fields]

        if fields is not None:
            params["fields"] = ",".join(fields)
        else:
            params["fields"] = "*"

        response = self.client.get(
            f"/submissions/{submission.token}",
            params=params,
            headers=self.headers,
        )
        response.raise_for_status()

        submission.set_attributes(response.json())

        return submission

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def create_submissions(self, submissions: Submissions) -> Submissions:
        """Send submissions for execution to a client.

        Directly send submissions to create_submissions route for execution.
        Cannot handle more submissions than the client supports.

        Parameters
        ----------
        submissions : Submissions
            A sequence of submissions to create.

        Returns
        -------
        Submissions
            A sequence of submissions with updated token attribute.
        """
        for submission in submissions:
            if not self.is_language_supported(language=submission.language):
                raise RuntimeError(
                    f"Client {type(self).__name__} does not support language "
                    f"{submission.language}!"
                )

        submissions_body = [submission.as_body(self) for submission in submissions]

        response = self.client.post(
            "/submissions/batch",
            headers=self.headers,
            params={"base64_encoded": "true"},
            json={"submissions": submissions_body},
        )
        response.raise_for_status()

        attributes = cast(list[dict[str, Any]], response.json())
        for submission, attrs in zip(submissions, attributes):
            submission.set_attributes(attrs)

        return submissions

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: str | Iterable[str] | None = None,
    ) -> Submissions:
        """Get submissions status.

        Directly send submissions' tokens to get_submissions route for status
        check. By default, all submissions attributes (fields) are requested.
        Cannot handle more submissions than the client supports.

        Parameters
        ----------
        submissions : Submissions
            Submissions to update.

        Returns
        -------
        Submissions
            A sequence of submissions with updated attributes.

        Raises
        ------
        ValueError
            If any submission does not have a token.
        """
        params = {
            "base64_encoded": "true",
        }

        if isinstance(fields, str):
            fields = [fields]

        if fields is not None:
            params["fields"] = ",".join(fields)
        else:
            params["fields"] = "*"

        tokens: list[str] = []
        for submission in submissions:
            if submission.token is None:
                raise ValueError("Every submission must have a token before retrieval.")
            tokens.append(str(submission.token))
        params["tokens"] = ",".join(tokens)

        response = self.client.get(
            "/submissions/batch",
            params=params,
            headers=self.headers,
        )
        response.raise_for_status()

        response_body = cast(dict[str, list[dict[str, Any]]], response.json())
        for submission, attrs in zip(submissions, response_body["submissions"]):
            submission.set_attributes(attrs)

        return submissions


class ATD(Client):
    """Base class for all AllThingsDev clients.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    host_header_value : str
        Value for the x-apihub-host header.
    api_key : str
        AllThingsDev API key.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    API_KEY_ENV: ClassVar[str | None] = "JUDGE0_ATD_API_KEY"

    def __init__(
        self,
        endpoint: str,
        host_header_value: str,
        api_key: str,
        **kwargs: Any,
    ) -> None:
        self.api_key = api_key
        super().__init__(
            endpoint,
            {
                "x-apihub-host": host_header_value,
                "x-apihub-key": api_key,
            },
            **kwargs,
        )

    def _update_endpoint_header(self, header_value: str) -> None:
        self.headers["x-apihub-endpoint"] = header_value


class ATDJudge0CE(ATD):
    """AllThingsDev client for CE flavor.

    Parameters
    ----------
    api_key : str
        AllThingsDev API key.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = (
        "https://judge0-ce.proxy-production.allthingsdev.co"
    )
    DEFAULT_HOST: ClassVar[str] = "Judge0-CE.allthingsdev.co"
    HOME_URL: ClassVar[str] = (
        "https://www.allthingsdev.co/apimarketplace/judge0-ce/66b683c8b7b7ad054eb6ff8f"
    )

    DEFAULT_ABOUT_ENDPOINT: ClassVar[str] = "01fc1c98-ceee-4f49-8614-f2214703e25f"
    DEFAULT_CONFIG_INFO_ENDPOINT: ClassVar[str] = "b7aab45d-5eb0-4519-b092-89e5af4fc4f3"
    DEFAULT_LANGUAGE_ENDPOINT: ClassVar[str] = "a50ae6b1-23c1-40eb-b34c-88bc8cf2c764"
    DEFAULT_LANGUAGES_ENDPOINT: ClassVar[str] = "03824deb-bd18-4456-8849-69d78e1383cc"
    DEFAULT_STATUSES_ENDPOINT: ClassVar[str] = "c37b603f-6f99-4e31-a361-7154c734f19b"
    DEFAULT_CREATE_SUBMISSION_ENDPOINT: ClassVar[str] = (
        "6e65686d-40b0-4bf7-a12f-1f6d033c4473"
    )
    DEFAULT_GET_SUBMISSION_ENDPOINT: ClassVar[str] = (
        "b7032b8b-86da-40b4-b9d3-b1f5e2b4ee1e"
    )
    DEFAULT_CREATE_SUBMISSIONS_ENDPOINT: ClassVar[str] = (
        "402b857c-1126-4450-bfd8-22e1f2cbff2f"
    )
    DEFAULT_GET_SUBMISSIONS_ENDPOINT: ClassVar[str] = (
        "e42f2a26-5b02-472a-80c9-61c4bdae32ec"
    )

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
            **kwargs,
        )

    def get_about(self) -> JsonObject:
        self._update_endpoint_header(self.DEFAULT_ABOUT_ENDPOINT)
        return super().get_about()

    def get_config_info(self) -> Config:
        self._update_endpoint_header(self.DEFAULT_CONFIG_INFO_ENDPOINT)
        return super().get_config_info()

    def get_language(self, language_id: int) -> Language:
        self._update_endpoint_header(self.DEFAULT_LANGUAGE_ENDPOINT)
        return super().get_language(language_id)

    def get_languages(self) -> list[Language]:
        self._update_endpoint_header(self.DEFAULT_LANGUAGES_ENDPOINT)
        return super().get_languages()

    def get_statuses(self) -> list[JsonObject]:
        self._update_endpoint_header(self.DEFAULT_STATUSES_ENDPOINT)
        return super().get_statuses()

    def create_submission(self, submission: Submission) -> Submission:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSION_ENDPOINT)
        return super().create_submission(submission)

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: str | Iterable[str] | None = None,
    ) -> Submission:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSION_ENDPOINT)
        return super().get_submission(submission, fields=fields)

    def create_submissions(self, submissions: Submissions) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSIONS_ENDPOINT)
        return super().create_submissions(submissions)

    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: str | Iterable[str] | None = None,
    ) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSIONS_ENDPOINT)
        return super().get_submissions(submissions, fields=fields)


class ATDJudge0ExtraCE(ATD):
    """AllThingsDev client for Extra CE flavor.

    Parameters
    ----------
    api_key : str
        AllThingsDev API key.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = (
        "https://judge0-extra-ce.proxy-production.allthingsdev.co"
    )
    DEFAULT_HOST: ClassVar[str] = "Judge0-Extra-CE.allthingsdev.co"
    HOME_URL: ClassVar[str] = (
        "https://www.allthingsdev.co/apimarketplace/judge0-extra-ce/"
        "66b68838b7b7ad054eb70690"
    )

    DEFAULT_ABOUT_ENDPOINT: ClassVar[str] = "1fd631a1-be6a-47d6-bf4c-987e357e3096"
    DEFAULT_CONFIG_INFO_ENDPOINT: ClassVar[str] = "46e05354-2a43-436a-9458-5d111456f0ff"
    DEFAULT_LANGUAGE_ENDPOINT: ClassVar[str] = "10465a84-2a2c-4213-845f-45e3c04a5867"
    DEFAULT_LANGUAGES_ENDPOINT: ClassVar[str] = "774ecece-1200-41f7-a992-38f186c90803"
    DEFAULT_STATUSES_ENDPOINT: ClassVar[str] = "a2843b3c-673d-4966-9a14-2e7d76dcd0cb"
    DEFAULT_CREATE_SUBMISSION_ENDPOINT: ClassVar[str] = (
        "be2d195e-dd58-4770-9f3c-d6c0fbc2b6e5"
    )
    DEFAULT_GET_SUBMISSION_ENDPOINT: ClassVar[str] = (
        "c3a457cd-37a6-4106-97a8-9e60a223abbc"
    )
    DEFAULT_CREATE_SUBMISSIONS_ENDPOINT: ClassVar[str] = (
        "c64df5d3-edfd-4b08-8687-561af2f80d2f"
    )
    DEFAULT_GET_SUBMISSIONS_ENDPOINT: ClassVar[str] = (
        "5d173718-8e6a-4cf5-9d8c-db5e6386d037"
    )

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
            **kwargs,
        )

    def get_about(self) -> JsonObject:
        self._update_endpoint_header(self.DEFAULT_ABOUT_ENDPOINT)
        return super().get_about()

    def get_config_info(self) -> Config:
        self._update_endpoint_header(self.DEFAULT_CONFIG_INFO_ENDPOINT)
        return super().get_config_info()

    def get_language(self, language_id: int) -> Language:
        self._update_endpoint_header(self.DEFAULT_LANGUAGE_ENDPOINT)
        return super().get_language(language_id)

    def get_languages(self) -> list[Language]:
        self._update_endpoint_header(self.DEFAULT_LANGUAGES_ENDPOINT)
        return super().get_languages()

    def get_statuses(self) -> list[JsonObject]:
        self._update_endpoint_header(self.DEFAULT_STATUSES_ENDPOINT)
        return super().get_statuses()

    def create_submission(self, submission: Submission) -> Submission:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSION_ENDPOINT)
        return super().create_submission(submission)

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: str | Iterable[str] | None = None,
    ) -> Submission:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSION_ENDPOINT)
        return super().get_submission(submission, fields=fields)

    def create_submissions(self, submissions: Submissions) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSIONS_ENDPOINT)
        return super().create_submissions(submissions)

    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: str | Iterable[str] | None = None,
    ) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSIONS_ENDPOINT)
        return super().get_submissions(submissions, fields=fields)


class Rapid(Client):
    """Base class for all RapidAPI clients.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    host_header_value : str
        Value for the x-rapidapi-host header.
    api_key : str
        RapidAPI API key.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    API_KEY_ENV: ClassVar[str | None] = "JUDGE0_RAPID_API_KEY"

    def __init__(
        self,
        endpoint: str,
        host_header_value: str,
        api_key: str,
        **kwargs: Any,
    ) -> None:
        self.api_key = api_key
        super().__init__(
            endpoint,
            {
                "x-rapidapi-host": host_header_value,
                "x-rapidapi-key": api_key,
            },
            **kwargs,
        )


class RapidJudge0CE(Rapid):
    """RapidAPI client for CE flavor.

    Parameters
    ----------
    api_key : str
        RapidAPI API key.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = "https://judge0-ce.p.rapidapi.com"
    DEFAULT_HOST: ClassVar[str] = "judge0-ce.p.rapidapi.com"
    HOME_URL: ClassVar[str] = "https://rapidapi.com/judge0-official/api/judge0-ce"

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
            **kwargs,
        )


class RapidJudge0ExtraCE(Rapid):
    """RapidAPI client for Extra CE flavor.

    Parameters
    ----------
    api_key : str
        RapidAPI API key.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = "https://judge0-extra-ce.p.rapidapi.com"
    DEFAULT_HOST: ClassVar[str] = "judge0-extra-ce.p.rapidapi.com"
    HOME_URL: ClassVar[str] = "https://rapidapi.com/judge0-official/api/judge0-extra-ce"

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
            **kwargs,
        )


class Judge0Cloud(Client):
    """Base class for all Judge0 Cloud clients.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    headers : str or dict
        Judge0 Cloud authentication headers, either as a JSON string or a dictionary.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    def __init__(
        self,
        endpoint: str,
        headers: str | Headers | None = None,
        **kwargs: Any,
    ) -> None:
        self.api_key = headers
        if isinstance(headers, str):
            from json import loads

            headers = cast(Headers, loads(headers))

        super().__init__(
            endpoint,
            headers,
            **kwargs,
        )


class Judge0CloudCE(Judge0Cloud):
    """Judge0 Cloud client for CE flavor.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    headers : str or dict
        Judge0 Cloud authentication headers, either as a JSON string or a dictionary.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = "https://ce.judge0.com"
    HOME_URL: ClassVar[str] = "https://ce.judge0.com"
    API_KEY_ENV: ClassVar[str | None] = "JUDGE0_CLOUD_CE_AUTH_HEADERS"

    def __init__(self, headers: str | Headers | None = None, **kwargs: Any) -> None:
        super().__init__(
            self.DEFAULT_ENDPOINT,
            headers,
            **kwargs,
        )


class Judge0CloudExtraCE(Judge0Cloud):
    """Judge0 Cloud client for Extra CE flavor.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    headers : str or dict
        Judge0 Cloud authentication headers, either as a JSON string or a dictionary.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = "https://extra-ce.judge0.com"
    HOME_URL: ClassVar[str] = "https://extra-ce.judge0.com"
    API_KEY_ENV: ClassVar[str | None] = "JUDGE0_CLOUD_EXTRA_CE_AUTH_HEADERS"

    def __init__(self, headers: str | Headers | None = None, **kwargs: Any) -> None:
        super().__init__(self.DEFAULT_ENDPOINT, headers, **kwargs)


CE = (Judge0CloudCE, RapidJudge0CE, ATDJudge0CE)
EXTRA_CE = (Judge0CloudExtraCE, RapidJudge0ExtraCE, ATDJudge0ExtraCE)

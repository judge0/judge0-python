from typing import ClassVar, Optional, Union

import requests

from .base_types import Config, Iterable, Language, LanguageAlias
from .data import LANGUAGE_TO_LANGUAGE_ID
from .retry import RetryStrategy
from .submission import Submission, Submissions
from .utils import handle_too_many_requests_error_for_preview_client


class Client:
    """Base class for all clients.

    Parameters
    ----------
    endpoint : str
        Client's default endpoint.
    auth_headers : dict
        Request authentication headers.

    Attributes
    ----------
    API_KEY_ENV : str
        Environment variable where judge0-python should look for API key for
        the client. Set to default values for RapidAPI and ATD clients.
    """

    # Environment variable where judge0-python should look for API key for
    # the client. Set to default values for RapidAPI and ATD clients.
    API_KEY_ENV: ClassVar[str] = None

    def __init__(
        self,
        endpoint,
        auth_headers=None,
        *,
        retry_strategy: Optional[RetryStrategy] = None,
    ) -> None:
        self.endpoint = endpoint
        self.auth_headers = auth_headers
        self.retry_strategy = retry_strategy
        self.session = requests.Session()

        try:
            self.languages = self.get_languages()
            self.config = self.get_config_info()
        except Exception as e:
            home_url = getattr(self, "HOME_URL", None)
            raise RuntimeError(
                f"Authentication failed. Visit {home_url} to get or "
                "review your authentication credentials."
            ) from e

    def __del__(self):
        self.session.close()

    @handle_too_many_requests_error_for_preview_client
    def get_about(self) -> dict:
        """Get general information about judge0.

        Returns
        -------
        dict
            General information about judge0.
        """
        response = self.session.get(
            f"{self.endpoint}/about",
            headers=self.auth_headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_too_many_requests_error_for_preview_client
    def get_config_info(self) -> Config:
        """Get information about client's configuration.

        Returns
        -------
        Config
            Client's configuration.
        """
        response = self.session.get(
            f"{self.endpoint}/config_info",
            headers=self.auth_headers,
        )
        response.raise_for_status()
        return Config(**response.json())

    @handle_too_many_requests_error_for_preview_client
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
        request_url = f"{self.endpoint}/languages/{language_id}"
        response = self.session.get(request_url, headers=self.auth_headers)
        response.raise_for_status()
        return Language(**response.json())

    @handle_too_many_requests_error_for_preview_client
    def get_languages(self) -> list[Language]:
        """Get a list of supported languages.

        Returns
        -------
        list of language
            A list of supported languages.
        """
        request_url = f"{self.endpoint}/languages"
        response = self.session.get(request_url, headers=self.auth_headers)
        response.raise_for_status()
        return [Language(**lang_dict) for lang_dict in response.json()]

    @handle_too_many_requests_error_for_preview_client
    def get_statuses(self) -> list[dict]:
        """Get a list of possible submission statuses.

        Returns
        -------
        list of dict
            A list of possible submission statues.
        """
        response = self.session.get(
            f"{self.endpoint}/statuses",
            headers=self.auth_headers,
        )
        response.raise_for_status()
        return response.json()

    @property
    def version(self):
        """Property corresponding to the current client's version."""
        if not hasattr(self, "_version"):
            _version = self.get_about()["version"]
            setattr(self, "_version", _version)
        return self._version

    def get_language_id(self, language: Union[LanguageAlias, int]) -> int:
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

    def is_language_supported(self, language: Union[LanguageAlias, int]) -> bool:
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

    @handle_too_many_requests_error_for_preview_client
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

        response = self.session.post(
            f"{self.endpoint}/submissions",
            json=body,
            params=params,
            headers=self.auth_headers,
        )
        response.raise_for_status()

        submission.set_attributes(response.json())

        return submission

    @handle_too_many_requests_error_for_preview_client
    def get_submission(
        self,
        submission: Submission,
        *,
        fields: Optional[Union[str, Iterable[str]]] = None,
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

        response = self.session.get(
            f"{self.endpoint}/submissions/{submission.token}",
            params=params,
            headers=self.auth_headers,
        )
        response.raise_for_status()

        submission.set_attributes(response.json())

        return submission

    @handle_too_many_requests_error_for_preview_client
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

        response = self.session.post(
            f"{self.endpoint}/submissions/batch",
            headers=self.auth_headers,
            params={"base64_encoded": "true"},
            json={"submissions": submissions_body},
        )
        response.raise_for_status()

        for submission, attrs in zip(submissions, response.json()):
            submission.set_attributes(attrs)

        return submissions

    @handle_too_many_requests_error_for_preview_client
    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: Optional[Union[str, Iterable[str]]] = None,
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

        tokens = ",".join([submission.token for submission in submissions])
        params["tokens"] = tokens

        response = self.session.get(
            f"{self.endpoint}/submissions/batch",
            params=params,
            headers=self.auth_headers,
        )
        response.raise_for_status()

        for submission, attrs in zip(submissions, response.json()["submissions"]):
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

    API_KEY_ENV: ClassVar[str] = "JUDGE0_ATD_API_KEY"

    def __init__(self, endpoint, host_header_value, api_key, **kwargs):
        self.api_key = api_key
        super().__init__(
            endpoint,
            {
                "x-apihub-host": host_header_value,
                "x-apihub-key": api_key,
            },
            **kwargs,
        )

    def _update_endpoint_header(self, header_value):
        self.auth_headers["x-apihub-endpoint"] = header_value


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

    def __init__(self, api_key, **kwargs):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
            **kwargs,
        )

    def get_about(self) -> dict:
        self._update_endpoint_header(self.DEFAULT_ABOUT_ENDPOINT)
        return super().get_about()

    def get_config_info(self) -> Config:
        self._update_endpoint_header(self.DEFAULT_CONFIG_INFO_ENDPOINT)
        return super().get_config_info()

    def get_language(self, language_id) -> Language:
        self._update_endpoint_header(self.DEFAULT_LANGUAGE_ENDPOINT)
        return super().get_language(language_id)

    def get_languages(self) -> list[Language]:
        self._update_endpoint_header(self.DEFAULT_LANGUAGES_ENDPOINT)
        return super().get_languages()

    def get_statuses(self) -> list[dict]:
        self._update_endpoint_header(self.DEFAULT_STATUSES_ENDPOINT)
        return super().get_statuses()

    def create_submission(self, submission: Submission) -> Submission:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSION_ENDPOINT)
        return super().create_submission(submission)

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: Optional[Union[str, Iterable[str]]] = None,
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
        fields: Optional[Union[str, Iterable[str]]] = None,
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

    def __init__(self, api_key, **kwargs):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
            **kwargs,
        )

    def get_about(self) -> dict:
        self._update_endpoint_header(self.DEFAULT_ABOUT_ENDPOINT)
        return super().get_about()

    def get_config_info(self) -> Config:
        self._update_endpoint_header(self.DEFAULT_CONFIG_INFO_ENDPOINT)
        return super().get_config_info()

    def get_language(self, language_id) -> Language:
        self._update_endpoint_header(self.DEFAULT_LANGUAGE_ENDPOINT)
        return super().get_language(language_id)

    def get_languages(self) -> list[Language]:
        self._update_endpoint_header(self.DEFAULT_LANGUAGES_ENDPOINT)
        return super().get_languages()

    def get_statuses(self) -> list[dict]:
        self._update_endpoint_header(self.DEFAULT_STATUSES_ENDPOINT)
        return super().get_statuses()

    def create_submission(self, submission: Submission) -> Submission:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSION_ENDPOINT)
        return super().create_submission(submission)

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: Optional[Union[str, Iterable[str]]] = None,
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
        fields: Optional[Union[str, Iterable[str]]] = None,
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

    API_KEY_ENV: ClassVar[str] = "JUDGE0_RAPID_API_KEY"

    def __init__(self, endpoint, host_header_value, api_key, **kwargs):
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

    def __init__(self, api_key, **kwargs):
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

    def __init__(self, api_key, **kwargs):
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
    auth_headers : str or dict
        Judge0 Cloud authentication headers, either as a JSON string or a dictionary.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    def __init__(self, endpoint, auth_headers=None, **kwargs):
        if isinstance(auth_headers, str):
            from json import loads

            auth_headers = loads(auth_headers)

        super().__init__(
            endpoint,
            auth_headers,
            **kwargs,
        )


class Judge0CloudCE(Judge0Cloud):
    """Judge0 Cloud client for CE flavor.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    auth_headers : str or dict
        Judge0 Cloud authentication headers, either as a JSON string or a dictionary.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = "https://ce.judge0.com"
    HOME_URL: ClassVar[str] = "https://ce.judge0.com"
    API_KEY_ENV: ClassVar[str] = "JUDGE0_CLOUD_CE_AUTH_HEADERS"

    def __init__(self, auth_headers=None, **kwargs):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            auth_headers,
            **kwargs,
        )


class Judge0CloudExtraCE(Judge0Cloud):
    """Judge0 Cloud client for Extra CE flavor.

    Parameters
    ----------
    endpoint : str
        Default request endpoint.
    auth_headers : str or dict
        Judge0 Cloud authentication headers, either as a JSON string or a dictionary.
    **kwargs : dict
        Additional keyword arguments for the base Client.
    """

    DEFAULT_ENDPOINT: ClassVar[str] = "https://extra-ce.judge0.com"
    HOME_URL: ClassVar[str] = "https://extra-ce.judge0.com"
    API_KEY_ENV: ClassVar[str] = "JUDGE0_CLOUD_EXTRA_CE_AUTH_HEADERS"

    def __init__(self, auth_headers=None, **kwargs):
        super().__init__(self.DEFAULT_ENDPOINT, auth_headers, **kwargs)


CE = (Judge0CloudCE, RapidJudge0CE, ATDJudge0CE)
EXTRA_CE = (Judge0CloudExtraCE, RapidJudge0ExtraCE, ATDJudge0ExtraCE)

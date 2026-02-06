Client Resolution
=================

The Judge0 Python SDK supports two main client flavors: Community Edition (CE) and Extra Community Edition (Extra CE), which correspond to the Judge0 Cloud editions. When you use functions like ``judge0.run`` or ``judge0.execute`` without explicitly providing a client instance, the SDK automatically resolves and initializes a client for you. This process, handled by the internal ``_get_implicit_client`` function, follows a specific order of priority.

The SDK determines which client to use based on environment variables. Here's the resolution order:

1. **Custom Client (Self-Hosted)**

The SDK first checks for a self-hosted Judge0 instance. If you have your own deployment of Judge0, you can configure the SDK to use it by setting the following environment variables:

* For CE flavor:
    * ``JUDGE0_CE_ENDPOINT``: The URL of your self-hosted Judge0 CE instance.
    * ``JUDGE0_CE_AUTH_HEADERS``: A JSON string representing the authentication headers.
* For Extra CE flavor:
    * ``JUDGE0_EXTRA_CE_ENDPOINT``: The URL of your self-hosted Judge0 Extra CE instance.
    * ``JUDGE0_EXTRA_CE_AUTH_HEADERS``: A JSON string representing the authentication headers.

If these variables are set, the SDK will initialize a ``Client`` instance with your custom endpoint and headers.

2. **Hub Clients**

If a custom client is not configured, the SDK will try to find API keys for one of the supported hub clients. The SDK checks for the following environment variables in order:

* **Judge0 Cloud**:
    * ``JUDGE0_CLOUD_CE_AUTH_HEADERS`` for ``Judge0CloudCE``
    * ``JUDGE0_CLOUD_EXTRA_CE_AUTH_HEADERS`` for ``Judge0CloudExtraCE``

* **RapidAPI**:
    *   ``JUDGE0_RAPID_API_KEY`` for both ``RapidJudge0CE`` and ``RapidJudge0ExtraCE``

* **AllThingsDev**:
    * ``JUDGE0_ATD_API_KEY`` for both ``ATDJudge0CE`` and ``ATDJudge0ExtraCE``

The first API key found determines the client that will be used.

3. **Preview Client**

If none of the above environment variables are set, the SDK falls back to using a **preview client**. This is an unauthenticated client that connects to the official Judge0 Cloud service. It initializes ``Judge0CloudCE()`` and ``Judge0CloudExtraCE()`` for the CE and Extra CE flavors, respectively.

When the preview client is used, a warning message is logged to the console, as this option is not recommended for production use. To suppress this warning, you can set the ``JUDGE0_SUPPRESS_PREVIEW_WARNING`` environment variable.

Example Resolution Flow
-----------------------

When you call a function like ``judge0.run(..., flavor=judge0.CE)``, the SDK will:

1.  Check if ``JUDGE0_IMPLICIT_CE_CLIENT`` is already initialized. If so, use it.
2.  Check for ``JUDGE0_CE_ENDPOINT`` and ``JUDGE0_CE_AUTH_HEADERS`` to configure a ``Client``.
3.  Check for ``JUDGE0_CLOUD_CE_AUTH_HEADERS`` to configure a ``Judge0CloudCE`` client.
4.  Check for ``JUDGE0_RAPID_API_KEY`` to configure a ``RapidJudge0CE`` client.
5.  Check for ``JUDGE0_ATD_API_KEY`` to configure an ``ATDJudge0CE`` client.
6.  If none of the above are found, initialize a preview ``Judge0CloudCE`` client and log a warning.

This implicit client resolution makes it easy to get started with the Judge0 Python SDK while providing the flexibility to configure it for different environments and services.

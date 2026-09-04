import asyncio
import json
import re
from typing import Any

import httpx

from .config import settings


class LLMClientError(RuntimeError):
    """Base exception for local LLM client failures."""


class LLMConnectionError(LLMClientError):
    """Raised when the Ollama server cannot be reached."""


class LLMTimeoutError(LLMClientError):
    """Raised when Ollama does not respond within the timeout."""


class LLMResponseError(LLMClientError):
    """Raised when the Ollama API returns an invalid response."""


class LLMValidationError(LLMClientError):
    """Raised when the model output fails validation."""


def extract_json_object(
    model_output: str,
) -> dict[str, Any]:
    """
    Extract a JSON object from an Ollama response.

    The model is instructed to return JSON, but this function also
    handles Markdown code blocks or limited text around the JSON.
    """

    cleaned = model_output.strip()

    if not cleaned:
        raise LLMValidationError(
            "Ollama returned an empty response."
        )

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    ).strip()

    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{[\s\S]*\}",
        cleaned,
    )

    if not match:
        raise LLMValidationError(
            "Ollama did not return a JSON object."
        )

    try:
        parsed = json.loads(
            match.group(0)
        )

    except json.JSONDecodeError as exc:
        raise LLMValidationError(
            "Ollama returned malformed JSON."
        ) from exc

    if not isinstance(parsed, dict):
        raise LLMValidationError(
            "Ollama response is not a JSON object."
        )

    return parsed


def normalise_prompt(
    prompt: str,
) -> str:
    """
    Validate and clean a prompt before sending it to Ollama.
    """

    cleaned = prompt.strip()

    if not cleaned:
        raise ValueError(
            "The LLM prompt cannot be empty."
        )

    return cleaned


def validate_required_fields(
    result: dict[str, Any],
    required_fields: list[str] | None,
) -> None:
    """
    Confirm that required top-level fields exist in the result.
    """

    if not required_fields:
        return

    missing_fields = [
        field
        for field in required_fields
        if field not in result
    ]

    if missing_fields:
        raise LLMValidationError(
            "The model response is missing required fields: "
            + ", ".join(missing_fields)
        )


def build_request_body(
    prompt: str,
    *,
    temperature: float,
    num_ctx: int,
    num_predict: int,
    force_cpu: bool,
    keep_alive: str,
    json_mode: bool,
) -> dict[str, Any]:
    """
    Construct the Ollama API request body.

    CPU execution is enabled by default because the local GPU runner
    previously experienced a CUDA initialisation failure.
    """

    options: dict[str, Any] = {
        "temperature": temperature,
        "num_ctx": num_ctx,
        "num_predict": num_predict,
    }

    if force_cpu:
        options["num_gpu"] = 0

    request_body: dict[str, Any] = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": keep_alive,
        "options": options,
    }

    if json_mode:
        request_body["format"] = "json"

    return request_body


async def call_ollama(
    prompt: str,
    *,
    temperature: float = 0.1,
    num_ctx: int = 3072,
    num_predict: int = 900,
    force_cpu: bool = True,
    keep_alive: str = "10m",
    json_mode: bool = True,
    read_timeout: float = 240.0,
) -> str:
    """
    Send a prompt to Ollama and return the raw model response.

    Use this function for agents that need either plain text or
    structured output without automatic JSON validation.
    """

    if not settings.enable_ollama:
        raise LLMConnectionError(
            "Ollama is disabled. "
            "Set ENABLE_OLLAMA=true in backend/.env."
        )

    cleaned_prompt = normalise_prompt(
        prompt
    )

    endpoint = (
        f"{settings.ollama_base_url.rstrip('/')}"
        "/api/generate"
    )

    request_body = build_request_body(
        cleaned_prompt,
        temperature=temperature,
        num_ctx=num_ctx,
        num_predict=num_predict,
        force_cpu=force_cpu,
        keep_alive=keep_alive,
        json_mode=json_mode,
    )

    timeout = httpx.Timeout(
        connect=10.0,
        read=read_timeout,
        write=30.0,
        pool=10.0,
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
        ) as client:
            response = await client.post(
                endpoint,
                json=request_body,
            )

            response.raise_for_status()

            response_body = response.json()

    except httpx.ConnectError as exc:
        raise LLMConnectionError(
            "Ollama is not reachable at "
            f"{settings.ollama_base_url}. "
            "Confirm that Ollama is running."
        ) from exc

    except httpx.TimeoutException as exc:
        raise LLMTimeoutError(
            "Ollama inference timed out."
        ) from exc

    except httpx.HTTPStatusError as exc:
        response_text = (
            exc.response.text[:1000]
        )

        raise LLMResponseError(
            "Ollama returned HTTP status "
            f"{exc.response.status_code}: "
            f"{response_text}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise LLMResponseError(
            "The Ollama API response could not be decoded as JSON."
        ) from exc

    except httpx.HTTPError as exc:
        raise LLMResponseError(
            "An HTTP error occurred while communicating with Ollama: "
            f"{exc}"
        ) from exc

    if not isinstance(
        response_body,
        dict,
    ):
        raise LLMResponseError(
            "The Ollama API returned an unexpected response structure."
        )

    model_output = response_body.get(
        "response"
    )

    if not isinstance(
        model_output,
        str,
    ):
        raise LLMResponseError(
            "The Ollama API response does not contain "
            "a valid text response."
        )

    if not model_output.strip():
        raise LLMResponseError(
            "Ollama returned an empty model response."
        )

    return model_output


async def generate_json(
    prompt: str,
    *,
    required_fields: list[str] | None = None,
    temperature: float = 0.1,
    num_ctx: int = 3072,
    num_predict: int = 900,
    force_cpu: bool = True,
    keep_alive: str = "10m",
    read_timeout: float = 240.0,
    retry_count: int = 1,
) -> dict[str, Any]:
    """
    Generate and validate a structured JSON response.

    retry_count represents additional attempts after the first call.
    retry_count=1 therefore permits a maximum of two calls.
    """

    attempts = max(
        1,
        retry_count + 1,
    )

    last_error: Exception | None = None

    for attempt in range(
        1,
        attempts + 1,
    ):
        try:
            model_output = await call_ollama(
                prompt,
                temperature=temperature,
                num_ctx=num_ctx,
                num_predict=num_predict,
                force_cpu=force_cpu,
                keep_alive=keep_alive,
                json_mode=True,
                read_timeout=read_timeout,
            )

            result = extract_json_object(
                model_output
            )

            validate_required_fields(
                result,
                required_fields,
            )

            return result

        except (
            LLMTimeoutError,
            LLMResponseError,
            LLMValidationError,
        ) as exc:
            last_error = exc

            if attempt < attempts:
                await asyncio.sleep(0.5)

    if last_error is not None:
        raise last_error

    raise LLMClientError(
        "Ollama generation failed for an unknown reason."
    )


async def generate_json_with_fallback(
    prompt: str,
    fallback: dict[str, Any],
    *,
    required_fields: list[str] | None = None,
    temperature: float = 0.1,
    num_ctx: int = 3072,
    num_predict: int = 900,
    force_cpu: bool = True,
    keep_alive: str = "10m",
    read_timeout: float = 240.0,
    retry_count: int = 1,
) -> dict[str, Any]:
    """
    Generate a JSON response and return a deterministic fallback
    if Ollama or response validation fails.

    The response identifies whether Ollama or the fallback produced
    the result.
    """

    try:
        result = await generate_json(
            prompt,
            required_fields=required_fields,
            temperature=temperature,
            num_ctx=num_ctx,
            num_predict=num_predict,
            force_cpu=force_cpu,
            keep_alive=keep_alive,
            read_timeout=read_timeout,
            retry_count=retry_count,
        )

        result["llm_status"] = "COMPLETED"
        result["llm_warning"] = None
        result["llm_model"] = settings.ollama_model

        return result

    except (
        LLMClientError,
        ValueError,
    ) as exc:
        fallback_result = dict(
            fallback
        )

        fallback_result["llm_status"] = "FALLBACK"

        fallback_result["llm_warning"] = (
            f"{type(exc).__name__}: {exc}"
        )

        fallback_result["llm_model"] = (
            settings.ollama_model
        )

        return fallback_result


def ollama_configuration() -> dict[str, Any]:
    """
    Return non-secret Ollama configuration for diagnostics.
    """

    return {
        "enabled": settings.enable_ollama,
        "base_url": settings.ollama_base_url,
        "model": settings.ollama_model,
        "default_execution": "CPU",
    }
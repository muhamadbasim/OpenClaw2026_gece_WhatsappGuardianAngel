"""URL redirect chain resolver for the Link Scanner Agent.

This module provides functionality to follow HTTP redirect chains,
recording each hop from the initial URL to the final destination.
Used by the Link Scanner Agent to detect suspicious redirect patterns
(e.g., excessive redirects used to obfuscate malicious destinations).

Implements Property 6: Redirect Chain Bounded Length - the chain must
have at most 11 entries (initial URL + 10 redirects).
"""

from dataclasses import dataclass, field
from typing import Optional

import httpx


@dataclass
class RedirectResult:
    """Result of following a URL's redirect chain.

    Attributes:
        chain: The sequence of URLs from the initial URL to the final
            destination. Always contains at least the initial URL.
        final_url: The last URL in the chain (the ultimate destination,
            or the last URL reached before an error/limit).
        exceeded_max_hops: True if the redirect chain hit the max_hops
            limit before reaching a non-redirect response.
        error: Error message if resolution failed (timeout, connection
            error, etc.). None if resolution completed successfully.
    """

    chain: list[str] = field(default_factory=list)
    final_url: str = ""
    exceeded_max_hops: bool = False
    error: Optional[str] = None


async def follow_redirects(
    url: str, max_hops: int = 10, timeout: float = 10.0
) -> RedirectResult:
    """Follow HTTP redirects from a URL and record the full chain.

    Makes sequential HTTP requests, following redirect responses (3xx
    status codes) by extracting the Location header. Uses HEAD requests
    for efficiency, falling back to GET if HEAD is not supported.

    The chain is bounded to max_hops redirects (default 10), meaning
    the chain list will contain at most max_hops + 1 entries (the
    initial URL plus up to max_hops redirected URLs).

    Args:
        url: The initial URL to resolve.
        max_hops: Maximum number of redirects to follow. Defaults to 10.
        timeout: Timeout in seconds for each individual HTTP request.
            Defaults to 10.0.

    Returns:
        A RedirectResult containing the full redirect chain, the final
        URL reached, whether the max hop limit was exceeded, and any
        error that occurred during resolution.

    Examples:
        >>> import asyncio
        >>> result = asyncio.run(follow_redirects("https://example.com"))
        >>> result.final_url
        'https://example.com'
        >>> result.exceeded_max_hops
        False
    """
    result = RedirectResult(chain=[url], final_url=url)

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout), verify=False
        ) as client:
            current_url = url

            for hop in range(max_hops):
                # Try HEAD first (more efficient), fall back to GET
                try:
                    response = await client.request(
                        "HEAD", current_url, follow_redirects=False
                    )
                except httpx.HTTPStatusError:
                    response = await client.request(
                        "GET", current_url, follow_redirects=False
                    )

                # Check if response is a redirect (3xx status)
                if response.is_redirect or response.has_redirect_location:
                    location = response.headers.get("location")
                    if not location:
                        # No Location header despite redirect status
                        break

                    # Handle relative URLs by resolving against current URL
                    if not location.startswith(("http://", "https://")):
                        # Resolve relative URL against the current URL
                        base = str(response.url)
                        if location.startswith("/"):
                            # Absolute path - combine with scheme+host
                            from urllib.parse import urlparse

                            parsed = urlparse(base)
                            location = (
                                f"{parsed.scheme}://{parsed.netloc}{location}"
                            )
                        else:
                            # Relative path - combine with base directory
                            location = base.rsplit("/", 1)[0] + "/" + location

                    current_url = location
                    result.chain.append(current_url)
                    result.final_url = current_url
                else:
                    # Not a redirect - we've reached the final destination
                    break
            else:
                # Loop completed without break - we hit max_hops
                # Check if the last URL in chain would redirect further
                try:
                    response = await client.request(
                        "HEAD", current_url, follow_redirects=False
                    )
                except httpx.HTTPStatusError:
                    response = await client.request(
                        "GET", current_url, follow_redirects=False
                    )

                if response.is_redirect or response.has_redirect_location:
                    result.exceeded_max_hops = True

    except httpx.TimeoutException as e:
        result.error = f"Timeout error: {str(e)}"
    except httpx.ConnectError as e:
        result.error = f"Connection error: {str(e)}"
    except httpx.HTTPError as e:
        result.error = f"HTTP error: {str(e)}"
    except Exception as e:
        result.error = f"Unexpected error: {str(e)}"

    return result

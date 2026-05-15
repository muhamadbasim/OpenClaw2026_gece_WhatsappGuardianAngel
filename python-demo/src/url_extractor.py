"""URL extraction utility for the WhatsApp Scam & Phishing Guardian Agent.

This module provides functionality to extract all valid URLs from message text,
supporting various URL formats including those with schemes, ports, paths,
query parameters, and fragments. It feeds into the Link Scanner Agent for
threat analysis.
"""

import re


# Regex pattern for extracting URLs from text.
# Matches:
#   - http:// and https:// URLs with full paths, query params, fragments
#   - URLs with port numbers (e.g., http://example.com:8080/path)
#   - www. prefixed URLs without a scheme (will be normalized to https://)
# Does NOT match:
#   - Email addresses (excluded via negative lookbehind for @)
#   - Bare domain names without www. prefix or scheme
_URL_PATTERN = re.compile(
    r'(?<![@\w])'                        # Negative lookbehind: not preceded by @ or word char (excludes emails)
    r'('
    r'(?:https?://)'                     # Scheme: http:// or https://
    r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+' # Domain labels
    r'[a-zA-Z]{2,}'                      # TLD (at least 2 chars)
    r'(?::\d{1,5})?'                     # Optional port
    r'(?:/[^\s<>\"\'\]},;]*)?'           # Optional path (allows parens for Wikipedia-style URLs)
    r'|'                                 # OR
    r'(?:www\.)'                          # www. prefix (no scheme)
    r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)*' # Optional subdomains
    r'[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.'      # Domain label
    r'[a-zA-Z]{2,}'                      # TLD
    r'(?::\d{1,5})?'                     # Optional port
    r'(?:/[^\s<>\"\'\]},;]*)?'           # Optional path
    r')',
    re.IGNORECASE
)


def _clean_trailing_punctuation(url: str) -> str:
    """Remove trailing punctuation that is likely not part of the URL.

    Handles cases like URLs at the end of sentences where periods,
    commas, or unbalanced parentheses get captured.

    Args:
        url: The raw extracted URL string.

    Returns:
        The URL with trailing punctuation stripped.
    """
    # Strip trailing punctuation that's unlikely to be part of the URL
    while url and url[-1] in '.,;:!?':
        url = url[:-1]

    # Handle unbalanced trailing parentheses/brackets
    # Only strip if there are more closing than opening
    for open_char, close_char in [('(', ')'), ('[', ']')]:
        while url.endswith(close_char) and url.count(close_char) > url.count(open_char):
            url = url[:-1]

    return url


def _extract_url_with_parens(text: str, start: int, end: int) -> str:
    """Extend a URL match to include balanced parentheses.

    When a URL contains parentheses (e.g., Wikipedia links), the regex
    may stop at the closing paren. This function extends the match to
    include balanced parentheses that are part of the URL.

    Args:
        text: The full message text.
        start: Start index of the regex match.
        end: End index of the regex match.

    Returns:
        The URL string, potentially extended to include balanced parens.
    """
    url = text[start:end]

    # If the URL has unbalanced open parens and the next char is ')',
    # extend to include the closing paren
    while (end < len(text)
           and text[end] == ')'
           and url.count('(') > url.count(')')):
        url += ')'
        end += 1

    return url


def extract_urls(text: str) -> list[str]:
    """Extract all valid URLs from message text.

    Finds URLs with http/https schemes and www-prefixed URLs in the given
    text. URLs without a scheme (www. prefix) are normalized to use https://.
    Returns a deduplicated list preserving order of first appearance.

    Args:
        text: The message text to extract URLs from.

    Returns:
        A deduplicated list of extracted URLs in order of first appearance.
        URLs without a scheme are prefixed with 'https://'.

    Examples:
        >>> extract_urls("Check this http://example.com now")
        ['http://example.com']

        >>> extract_urls("Visit www.example.com or https://test.org/path?q=1")
        ['https://www.example.com', 'https://test.org/path?q=1']

        >>> extract_urls("Email user@example.com is not a URL")
        []
    """
    if not text:
        return []

    seen: set[str] = set()
    urls: list[str] = []

    for match in _URL_PATTERN.finditer(text):
        # Extend match to include balanced parentheses
        url = _extract_url_with_parens(text, match.start(), match.end())

        # Clean trailing punctuation
        url = _clean_trailing_punctuation(url)

        # Skip empty results after cleaning
        if not url:
            continue

        # Normalize www. URLs by prepending https://
        if url.lower().startswith('www.'):
            url = 'https://' + url

        # Deduplicate while preserving order
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls

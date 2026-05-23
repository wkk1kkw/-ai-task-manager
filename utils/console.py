"""Console utilities with emoji-safe output for Windows GBK terminals."""

import click

_EMOJI_MAP = {
    "✅": "[OK]",
    "❌": "[ERROR]",
    "📭": "[EMPTY]",
    "📋": "[LIST]",
    "🟢": "[>]",
    "🟡": "[~]",
    "📦": "[ARCH]",
    "⚪": "[.]",
    "🔴": "[!]",
    "🔄": "[...]",
    "👀": "[REV]",
    "🔵": "[DONE]",
    "█": "#",
    "░": "-",
}


def echo(message="", **kwargs):
    """Safe echo that handles Windows GBK terminals.

    Tries to output the message as-is first. If a UnicodeEncodeError
    occurs (e.g. GBK terminal cannot encode emoji), replaces emoji
    characters with ASCII-safe alternatives and retries.
    """
    try:
        click.echo(message, **kwargs)
    except UnicodeEncodeError:
        safe = message
        for em, repl in _EMOJI_MAP.items():
            safe = safe.replace(em, repl)
        click.echo(safe, **kwargs)

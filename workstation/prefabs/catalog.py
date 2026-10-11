"""Fixed, auditable, read-only navigation recipes.

Only complete matches from trusted HUMAN turns qualify for provider-free
navigation. Never interpolate a user-provided URL into a privileged fast path.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Destination:
    key: str
    title: str
    url: str
    aliases: tuple[str, ...]


DESTINATIONS: tuple[Destination, ...] = (
    Destination("trello", "Trello", "https://trello.com/", ("trello",)),
    Destination("trello_editorial", "Calend\u00e1rio Editorial \u2014 Trello",
                "https://trello.com/b/Edq32SNp/calendario-editorial",
                ("calendario editorial", "quadro calendario editorial", "trello calendario editorial")),
    Destination("trello_scrum", "ACIRV + VCOM: SCRUM \u2014 Trello",
                "https://trello.com/b/GDM8ZE3r/acirv-vcom-scrum",
                ("acirv vcom scrum", "quadro scrum", "trello scrum", "quadro acirv vcom")),
    Destination("whatsapp", "WhatsApp Web", "https://web.whatsapp.com/",
                ("whatsapp", "whatsapp web")),
    Destination("chatgpt", "ChatGPT", "https://chatgpt.com/", ("chatgpt", "chat gpt")),
    Destination("instagram", "Instagram", "https://www.instagram.com/", ("instagram",)),
    Destination("instagram_acirv", "Instagram ACIRV", "https://www.instagram.com/acirvoficial/",
                ("instagram da acirv", "perfil da acirv no instagram", "perfil acirvoficial")),
)

_DESTINATIONS = {d.key: d for d in DESTINATIONS}
_VERBS = "abrir|abre|abra|acesse|acessar|va para|ir para|navegue para|navegar para|open"
_NAV_REQUEST = re.compile(rf"^(?:por favor\s+)?(?:{_VERBS})(?:\s+o|\s+a|\s+meu|\s+minha)?\s+(.+?)(?:\s+por favor)?[.!?]*$", re.I)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^\w\s]", " ", value.casefold())
    return " ".join(value.split())


def match_navigation(text: str) -> Destination | None:
    """Whitelist-only closed-vocabulary intent recognizer (no LLM)."""
    if not isinstance(text, str) or len(text) > 180 or "\n" in text:
        return None
    normalized = normalize(text)
    m = _NAV_REQUEST.fullmatch(normalized)
    if m is None:
        return None
    target = m.group(1).strip()
    for d in DESTINATIONS:
        if target in d.aliases:
            return d
    return None


def get_destination(key: str) -> Destination:
    if key not in _DESTINATIONS:
        raise ValueError(f"Unknown prefab destination: {key!r}")
    return _DESTINATIONS[key]


def canonical_browser_url(url: str) -> tuple[str, str]:
    """Host + path, excluding query/hash, for scoped verification only."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port:
        raise ValueError("Only canonical HTTPS hosts are admissible")
    return parsed.hostname.lower(), parsed.path.rstrip("/") or "/"


def same_destination(actual_url: str, desired_url: str) -> bool:
    """Domain exact, path exact (no subdomain/substring confused-deputy)."""
    try:
        actual_host, actual_path = canonical_browser_url(actual_url)
        desired_host, desired_path = canonical_browser_url(desired_url)
    except (ValueError, TypeError):
        return False
    if desired_host == "trello.com" and desired_path == "/":
        return actual_host == desired_host   # logged-in redirect may be /u/name/boards
    if desired_host == "www.instagram.com" and desired_path == "/":
        return actual_host in {"www.instagram.com", "instagram.com"}
    return actual_host == desired_host and actual_path == desired_path


@dataclass(frozen=True)
class TrelloReadIntent:
    board: str
    search: str = ""


def match_trello_read(text: str) -> TrelloReadIntent | None:
    """Literal, human-origin command grammar, never an open-ended NL parser."""
    if not isinstance(text, str) or len(text) > 190 or "\n" in text:
        return None
    sentence = normalize(text)
    board_names = {
        "calendario editorial": "editorial",
        "quadro calendario editorial": "editorial",
        "quadro scrum": "scrum",
        "acirv vcom scrum": "scrum",
    }
    for name, board in board_names.items():
        if sentence in {f"liste os cards do {name}", f"listar os cards do {name}",
                        f"mostre os cards do {name}", f"quais os cards do {name}",
                        f"liste os cartoes do {name}", f"liste os cards da {name}"}:
            return TrelloReadIntent(board)
        for prefix in ("encontre o card ", "busque o card ", "procure o card "):
            suffix = f" no {name}"
            if sentence.startswith(prefix) and sentence.endswith(suffix):
                search = sentence[len(prefix):-len(suffix)].strip()
                if 2 <= len(search) <= 80:
                    return TrelloReadIntent(board, search)
    return None
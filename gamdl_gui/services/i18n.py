"""Tiny JSON based translator with a Qt signal for live language switching."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class Translator(QObject):
    languageChanged = Signal()

    def __init__(self, langs_dir: Path, language: str = "en") -> None:
        super().__init__()
        self._langs_dir = Path(langs_dir)
        self._language = "en"
        self._texts: dict[str, str] = {}
        self.set_language(language)

    # -- properties -----------------------------------------------------
    @property
    def language(self) -> str:
        return self._language

    @property
    def available(self) -> list[str]:
        if not self._langs_dir.exists():
            return ["en"]
        return sorted(p.stem for p in self._langs_dir.glob("*.json"))

    # -- API ------------------------------------------------------------
    def set_language(self, language: str) -> None:
        if language not in self.available:
            language = "en"
        self._language = language
        self._texts = self._read(language)
        if not self._texts and language != "en":
            self._texts = self._read("en")
        self.languageChanged.emit()

    def tr(self, key: str, *args: object, **kwargs: object) -> str:
        text = self._texts.get(key, key)
        if args or kwargs:
            try:
                return text.format(*args, **kwargs)
            except (IndexError, KeyError):
                return text
        return text

    # -- internals ------------------------------------------------------
    def _read(self, language: str) -> dict[str, str]:
        path = self._langs_dir / f"{language}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

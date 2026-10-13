"""Visão pré-processada do documento, calculada uma única vez e compartilhada pelos analisadores."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cached_property

from detector_ia.core.models import Paragraph, Sentence
from detector_ia.core.text import split_sentences, tokens

MIN_BODY_TOKENS = 6


class AnalysisDocument:
    def __init__(self, paragraphs: Sequence[Paragraph]):
        self.paragraphs = list(paragraphs)
        self.body_indices: list[int] = [
            i for i, p in enumerate(self.paragraphs)
            if not p.is_heading and len(tokens(p.text)) >= MIN_BODY_TOKENS
        ]
        self.sentences: list[Sentence] = []
        for i in self.body_indices:
            text = self.paragraphs[i].text
            for s, e in split_sentences(text):
                chunk = text[s:e]
                self.sentences.append(Sentence(i, s, e, chunk, tuple(tokens(chunk))))

    @cached_property
    def text(self) -> str:
        return " ".join(self.paragraphs[i].text for i in self.body_indices)

    @cached_property
    def lower(self) -> str:
        return self.text.lower()

    @cached_property
    def tokens(self) -> list[str]:
        return tokens(self.text)

    @property
    def word_count(self) -> int:
        return len(self.tokens)

    @cached_property
    def paragraph_lengths(self) -> list[int]:
        return [len(tokens(self.paragraphs[i].text)) for i in self.body_indices]

    def per_1000(self, count: float) -> float:
        return count / self.word_count * 1000 if self.word_count else 0.0

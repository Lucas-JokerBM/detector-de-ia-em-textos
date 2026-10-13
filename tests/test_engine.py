import unittest
from dataclasses import dataclass

from detector_ia.core.analyzers.base import Analyzer, AnalyzerOutput
from detector_ia.core.docx_reader import read_docx
from detector_ia.core.engine import AnalysisEngine, verdict_for
from detector_ia.core.models import Paragraph
from helpers import AI_TEXT, HUMAN_TEXT, make_docx


def analyze(texts, engine=None):
    return (engine or AnalysisEngine()).analyze(read_docx(make_docx(texts)))


class EngineTests(unittest.TestCase):
    def test_ai_text_scores_higher_than_human(self):
        self.assertGreater(analyze(AI_TEXT).score, analyze(HUMAN_TEXT).score + 20)

    def test_flags_have_reasons_and_suggestions(self):
        r = analyze(AI_TEXT)
        self.assertTrue(r.flags)
        for f in r.flags:
            self.assertTrue(f.reasons and f.suggestions)

    def test_segments_reconstruct_original_text(self):
        r = analyze(AI_TEXT)
        rebuilt = ["".join(s.text for s in p.segments) for p in r.paragraphs]
        self.assertEqual(rebuilt, AI_TEXT)

    def test_flag_ids_in_segments_exist(self):
        r = analyze(AI_TEXT)
        ids = {f.id for f in r.flags}
        used = {s.flag for p in r.paragraphs for s in p.segments if s.flag is not None}
        self.assertEqual(used, ids)

    def test_short_text_warns(self):
        self.assertTrue(analyze(HUMAN_TEXT).warnings)

    def test_empty_document(self):
        r = AnalysisEngine().analyze([Paragraph("curto")])
        self.assertEqual(r.score, 0.0)
        self.assertTrue(r.warnings)

    def test_weights_override(self):
        base = analyze(AI_TEXT)
        only_phrases = analyze(AI_TEXT, AnalysisEngine(weights={m.id: 0 for m in base.metrics} | {"phrases": 1}))
        phrases = next(m for m in base.metrics if m.id == "phrases")
        self.assertAlmostEqual(only_phrases.score, round(phrases.score * 100, 1), places=1)

    def test_custom_analyzer_plugs_in(self):
        class AlwaysAi(Analyzer):
            id, name, default_weight = "always", "Sempre I.A.", 1.0

            def analyze(self, doc):
                return AnalyzerOutput(self.metric("x", 1.0, "teste"))

        r = analyze(HUMAN_TEXT, AnalysisEngine(analyzers=[AlwaysAi()]))
        self.assertEqual(r.score, 100.0)

    def test_failing_analyzer_is_isolated(self):
        class Broken(Analyzer):
            id, name, default_weight = "broken", "Quebrado", 1.0

            def analyze(self, doc):
                raise RuntimeError("boom")

        base = AnalysisEngine().analyzers
        r = analyze(AI_TEXT, AnalysisEngine(analyzers=[Broken(), *base]))
        self.assertGreater(r.score, 0)

    def test_verdict_bands(self):
        self.assertIn("humano", verdict_for(10))
        self.assertIn("Muito provável", verdict_for(90))


if __name__ == "__main__":
    unittest.main()

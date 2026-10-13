import io
import unittest
import zipfile

from detector_ia.core.docx_reader import DocxError, DocxLimits, DocxTooLargeError, read_docx
from helpers import NS, make_docx


class ReaderTests(unittest.TestCase):
    def test_reads_paragraphs_and_headings(self):
        paras = read_docx(make_docx(["Primeiro parágrafo de teste com texto."], heading="Título"))
        self.assertEqual(len(paras), 2)
        self.assertTrue(paras[0].is_heading)
        self.assertFalse(paras[1].is_heading)

    def test_rejects_non_zip(self):
        with self.assertRaises(DocxError):
            read_docx(b"isto nao e um docx")

    def test_rejects_zip_without_document_xml(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("outro.txt", "x")
        with self.assertRaises(DocxError):
            read_docx(buf.getvalue())

    def test_rejects_oversized_file(self):
        with self.assertRaises(DocxTooLargeError):
            read_docx(make_docx(["texto " * 50]), DocxLimits(max_bytes=100))

    def test_rejects_zip_bomb_ratio(self):
        bomb = make_docx(["a"], raw_xml=f'<w:document xmlns:w="{NS}"><w:body>' + "<!--" + "A" * 5_000_000 + "-->" + "</w:body></w:document>")
        with self.assertRaises(DocxError):
            read_docx(bomb, DocxLimits(max_ratio=50))

    def test_rejects_xml_entity_expansion(self):
        evil = ('<?xml version="1.0"?><!DOCTYPE d [<!ENTITY a "AAAA"><!ENTITY b "&a;&a;&a;&a;">]>'
                f'<w:document xmlns:w="{NS}"><w:body><w:p><w:r><w:t>&b;</w:t></w:r></w:p></w:body></w:document>')
        with self.assertRaises(DocxError):
            read_docx(make_docx([], raw_xml=evil))


if __name__ == "__main__":
    unittest.main()

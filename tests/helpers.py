import io
import zipfile

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

AI_TEXT = [
    "No cenário atual, a inteligência artificial desempenha um papel crucial em diversos setores. "
    "Além disso, é importante ressaltar que essa tecnologia é cada vez mais utilizada. "
    "Dessa forma, as empresas buscam soluções inovadoras para potencializar resultados.",
    "Além disso, a tecnologia oferece uma abordagem holística para os desafios modernos. "
    "Portanto, é fundamental compreender seus impactos. "
    "Dessa forma, a sociedade pode navegar por esse panorama multifacetado — com segurança.",
    "Além disso, os dados mostram que o uso cresce. Portanto, as organizações devem se adaptar. "
    "Em suma, a jornada rumo à inovação é essencial para todos os envolvidos no processo.",
]
HUMAN_TEXT = [
    "Ontem fui ao mercado e a fila estava enorme. Sinceramente, não aguentei! Comprei só pão. "
    "Minha vó dizia que paciência é coisa de quem tem tempo, e eu nunca tive muito, "
    "então voltei pra casa comendo o pão no caminho mesmo.",
]


def make_docx(paragraphs, heading=None, raw_xml=None) -> bytes:
    body = "".join(f"<w:p><w:r><w:t>{t}</w:t></w:r></w:p>" for t in paragraphs)
    if heading:
        body = (f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>{heading}</w:t></w:r></w:p>' + body)
    xml = raw_xml or (f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{NS}"><w:body>{body}</w:body></w:document>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("word/document.xml", xml)
    return buf.getvalue()

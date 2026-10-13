"""Léxico (dados) separado da lógica: fácil de estender, traduzir ou carregar de arquivo/banco."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

GENERIC = "Troque por uma formulação mais direta e específica ao seu contexto."

PHRASES = {
    # Português
    "vale ressaltar": "Corte a expressão e vá direto ao ponto que quer enfatizar.",
    "vale destacar": "Corte a expressão e vá direto ao ponto que quer enfatizar.",
    "é importante ressaltar": "Diga o fato e explique por que importa, sem o aviso prévio.",
    "é importante destacar": "Diga o fato e explique por que importa, sem o aviso prévio.",
    "é importante salientar": "Diga o fato e explique por que importa, sem o aviso prévio.",
    "é importante notar": "Diga o fato e explique por que importa, sem o aviso prévio.",
    "é fundamental": "Justifique a importância com um dado, exemplo ou consequência concreta.",
    "é essencial": "Justifique a importância com um dado, exemplo ou consequência concreta.",
    "em suma": "Se precisar concluir, retome um dado ou decisão específica em vez de resumir de forma genérica.",
    "em conclusão": "Conclua com uma posição própria ou próximo passo concreto.",
    "em última análise": "Substitua por uma conclusão objetiva, ou elimine.",
    "no cenário atual": "Cite o contexto real (ano, setor, fato) em vez de 'cenário atual'.",
    "no mundo atual": "Cite o contexto real (ano, setor, fato) em vez de 'mundo atual'.",
    "no mundo contemporâneo": "Cite o contexto real em vez de fórmula genérica.",
    "na era digital": "Especifique a tecnologia ou o fenômeno de que está falando.",
    "ao longo da história": "Indique o período ou evento específico.",
    "cada vez mais": "Use um número, comparação ou data para mostrar a tendência.",
    "desempenha um papel crucial": "Use verbo mais específico: o que exatamente ele faz?",
    "desempenha um papel fundamental": "Use verbo mais específico: o que exatamente ele faz?",
    "papel fundamental": "Use verbo mais específico: o que exatamente ele faz?",
    "papel crucial": "Use verbo mais específico: o que exatamente ele faz?",
    "multifacetad": "Nomeie as facetas em vez de rotulá-las.",
    "panorama": "Prefira 'situação', 'quadro' ou descreva o conteúdo diretamente.",
    "abordagem holística": "Explique o que a abordagem inclui na prática.",
    "de forma holística": "Explique o que está sendo integrado.",
    "nesse sentido": "Muitas vezes pode ser removido sem perda de sentido.",
    "dessa forma": "Experimente remover ou usar 'assim' / ligar as frases com vírgula.",
    "dessa maneira": "Experimente remover ou usar 'assim'.",
    "por outro lado": "Use com moderação; confira se há mesmo contraste.",
    "além disso": "Una as ideias numa só frase ou deixe a sequência falar por si.",
    "ademais": "Troque por 'também' ou una as frases.",
    "outrossim": "Troque por 'também' (tom muito rebuscado).",
    "por fim": "Evite marcar o encerramento de forma mecânica.",
    "em primeiro lugar": "Estrutura de lista mecânica; reescreva de forma narrativa.",
    "em segundo lugar": "Estrutura de lista mecânica; reescreva de forma narrativa.",
    "mergulhar": "Metáfora comum em texto de I.A.; use 'examinar', 'analisar'.",
    "jornada": "Metáfora comum em texto de I.A.; use o termo literal.",
    "navegar por": "Metáfora comum em texto de I.A.; use o termo literal.",
    "potencializar": "Prefira 'aumentar', 'melhorar' + dado concreto.",
    "impulsionar": "Prefira 'aumentar', 'acelerar' + dado concreto.",
    "fomentar": "Prefira 'estimular', 'incentivar' + exemplo.",
    "robusto": "Diga em que o item é forte (desempenho, segurança, escala...).",
    "inovador": "Mostre a novidade em vez de rotulá-la.",
    "soluções inovadoras": "Descreva a solução concreta.",
    "desbloquear o potencial": "Clichê; descreva o resultado esperado.",
    "pode ser definido como": "Defina com suas palavras, direto ao ponto.",
    "tecido social": "Clichê; seja específico sobre o grupo ou efeito.",
    "ecossistema": "Verifique se o termo é realmente necessário.",
    "sem dúvida": "Evite certezas vazias; apresente a evidência.",
    "é inegável": "Evite certezas vazias; apresente a evidência.",
    "é crucial": "Justifique a importância com um dado ou exemplo.",
    "em linhas gerais": "Seja mais específico.",
    "diante disso": "Pode ser removido ou trocado por conectivo mais simples.",
    # Inglês
    "delve": "Palavra muito associada a I.A.; use 'explore', 'examine' ou seja específico.",
    "it is important to note": "Diga o fato diretamente.",
    "it's important to note": "Diga o fato diretamente.",
    "in conclusion": "Conclua com posição própria ou próximo passo concreto.",
    "furthermore": "Use 'also' ou una as frases.",
    "moreover": "Use 'also' ou una as frases.",
    "plays a crucial role": "Use verbo mais específico.",
    "plays a vital role": "Use verbo mais específico.",
    "in today's": "Cite o contexto real (ano, setor, fato).",
    "tapestry": "Metáfora típica de I.A.; use o termo literal.",
    "landscape of": "Troque por descrição direta.",
    "in the realm of": "Troque por 'in' ou 'in the field of'.",
    "leverage": "Prefira 'use'.",
    "holistic": "Explique o que está sendo integrado.",
    "seamless": "Mostre o benefício concreto.",
    "testament to": "Clichê; descreva a evidência.",
    "multifaceted": "Nomeie as facetas.",
}

TRANSITIONS = [
    "além disso", "portanto", "dessa forma", "dessa maneira", "nesse sentido", "ademais",
    "contudo", "no entanto", "por outro lado", "em suma", "em conclusão", "por fim",
    "assim", "diante disso", "consequentemente", "ainda assim", "por conseguinte",
    "furthermore", "moreover", "however", "therefore", "additionally", "in conclusion",
    "thus", "consequently",
]

# Marcadores de voz pessoal/informal (ausência é sinal fraco de texto de I.A.)
VOICE = {
    "eu", "meu", "minha", "meus", "minhas", "acho", "acredito", "pra", "né", "tá", "cara",
    "gente", "tipo", "sinceramente", "confesso", "lembro", "vi", "senti", "nós", "nosso",
    "i", "my", "me", "mine", "we", "our", "honestly", "gonna", "kinda", "yeah", "don't",
    "can't", "i'm", "i've",
}


@dataclass(frozen=True)
class Lexicon:
    phrases: Mapping[str, str]
    transitions: tuple[str, ...]
    voice: frozenset[str]


DEFAULT_LEXICON = Lexicon(PHRASES, tuple(TRANSITIONS), frozenset(VOICE))

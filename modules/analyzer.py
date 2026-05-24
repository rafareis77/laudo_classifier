# modules/analyzer.py
# Análise clínica do laudo: detecção de status e sugestão de condutas.

import re

# ---------------------------------------------------------------------------
# Palavras-chave por domínio
# ---------------------------------------------------------------------------

_URGENCIA_KEYWORDS = [
    "urgência", "urgente", "imediata", "emergência", "ativar protocolo",
    "acionar", "cirurgia de urgência", "internação", "uti", "centro cirúrgico",
    "neurocirurgia", "vascular urgente", "trombólise", "trombectomia",
    "avc", "hematoma expansivo", "hemorragia", "pneumotórax",
    "apendicite aguda", "aneurisma",
]

_ALTERADO_KEYWORDS = [
    "consolidação", "derrame", "nódulo", "cálculo", "fratura", "hérnia",
    "atelectasia", "cardiomegalia", "esplenomegalia", "hidronefrose",
    "estenose", "escoliose", "espondilolistese", "esteatose", "pancreatite",
    "lesão", "massa", "tumor", "metástase", "hipodensidade", "hiperdensidade",
    "edema", "coleção", "ascite", "dilatação", "rotura", "adenoma",
    "desmielinização", "calcificação", "infarto", "hematoma",
    "osteófito", "osteopenia", "redução da altura", "velamento",
    "alterado", "alteração", "anormal", "patológico",
]

_NORMAL_KEYWORDS = [
    "sem alterações", "dentro da normalidade", "normal", "preservado",
    "íntegro", "sem achados patológicos", "habitual", "livre",
    "homogêneo", "regular", "simétrico",
]

# ---------------------------------------------------------------------------
# Condutas sugeridas por tipo de exame e gravidade
# ---------------------------------------------------------------------------

_CONDUTAS: dict[str, dict[str, list[str]]] = {
    "Raio-X de Tórax": {
        "urgente": [
            "⚠️ Avaliar antibioticoterapia endovenosa para pneumonia grave.",
            "⚠️ Considerar drenagem pleural se derrame volumoso.",
            "⚠️ Solicitar TC de tórax com contraste imediatamente.",
        ],
        "alterado": [
            "📋 Solicitar TC de tórax para melhor caracterização.",
            "📋 Encaminhar pneumologia ou cardiologia conforme achado.",
            "📋 Correlacionar com clínica e exames laboratoriais.",
        ],
        "normal": [
            "✅ Exame sem alterações. Manter acompanhamento de rotina.",
        ],
    },
    "Radiografia de Coluna": {
        "urgente": [
            "⚠️ Imobilizar e encaminhar neurocirurgia para fratura vertebral.",
            "⚠️ Avaliar déficit neurológico e solicitar RM urgente.",
        ],
        "alterado": [
            "📋 Encaminhar ortopedia ou cirurgia da coluna.",
            "📋 Solicitar RM de coluna para avaliação complementar.",
            "📋 Iniciar analgesia e fisioterapia conforme indicação.",
        ],
        "normal": [
            "✅ Coluna sem alterações estruturais. Orientar postura e ergonomia.",
        ],
    },
    "Tomografia de Crânio": {
        "urgente": [
            "🚨 ATIVAR PROTOCOLO DE AVC — Avaliar trombólise/trombectomia.",
            "🚨 Acionar neurocirurgia imediatamente.",
            "🚨 Solicitar angiotomografia cerebral e internar em UTI.",
        ],
        "alterado": [
            "📋 Solicitar RM encefálica com contraste para complementação.",
            "📋 Encaminhar neurologia para avaliação.",
            "📋 Monitorizar nível de consciência e sinais vitais.",
        ],
        "normal": [
            "✅ TC de crânio sem alterações agudas. Conduta conforme quadro clínico.",
        ],
    },
    "Tomografia de Abdômen": {
        "urgente": [
            "🚨 Encaminhar centro cirúrgico de emergência.",
            "🚨 Acionar cirurgia vascular para aneurisma de aorta.",
            "⚠️ Internação para monitorização de pancreatite aguda.",
        ],
        "alterado": [
            "📋 Encaminhar cirurgia geral para avaliação.",
            "📋 Solicitar RM hepática para lesões focais indeterminadas.",
            "📋 Correlacionar com marcadores tumorais e história clínica.",
        ],
        "normal": [
            "✅ Abdômen sem alterações. Acompanhamento conforme indicação clínica.",
        ],
    },
    "Ressonância Magnética": {
        "urgente": [
            "🚨 Encaminhar neurocirurgia para lesão expansiva.",
            "⚠️ Solicitar biópsia estereotáxica conforme avaliação.",
        ],
        "alterado": [
            "📋 Encaminhar especialidade conforme achado (neurologia, ortopedia, endocrinologia).",
            "📋 Correlacionar com clínica para definição de conduta.",
            "📋 Considerar tratamento conservador vs. cirúrgico.",
        ],
        "normal": [
            "✅ RM sem alterações. Acompanhamento clínico conforme quadro.",
        ],
    },
    "Ultrassonografia": {
        "urgente": [
            "⚠️ Encaminhar cirurgia para avaliação urgente.",
            "⚠️ Solicitar exames complementares para estadiamento.",
        ],
        "alterado": [
            "📋 Encaminhar especialidade correspondente ao achado.",
            "📋 Solicitar exames laboratoriais complementares.",
            "📋 Agendar PAAF se nódulo suspeito.",
        ],
        "normal": [
            "✅ Ultrassonografia sem alterações. Seguimento de rotina.",
        ],
    },
}

_CONDUTA_GENERICA = {
    "urgente": ["🚨 Achados críticos identificados. Avaliação especializada urgente necessária."],
    "alterado": ["📋 Achados alterados. Correlacionar clinicamente e encaminhar especialidade."],
    "normal": ["✅ Sem achados patológicos relevantes."],
}


# ---------------------------------------------------------------------------
# Funções públicas
# ---------------------------------------------------------------------------

def detecta_status(texto: str) -> str:
    """
    Detecta o status clínico do laudo: 'urgente', 'alterado' ou 'normal'.

    Retorna:
        str: 'urgente' | 'alterado' | 'normal'
    """
    texto_lower = texto.lower()

    if any(k in texto_lower for k in _URGENCIA_KEYWORDS):
        return "urgente"
    if any(k in texto_lower for k in _ALTERADO_KEYWORDS):
        return "alterado"
    return "normal"


def sugere_condutas(tipo_exame: str, status: str) -> list[str]:
    """
    Retorna lista de condutas sugeridas com base no tipo e status.

    Parâmetros:
        tipo_exame: Classe prevista pelo modelo.
        status:     'urgente' | 'alterado' | 'normal'.

    Retorna:
        list[str]: Condutas formatadas com emoji de prioridade.
    """
    condutas_tipo = _CONDUTAS.get(tipo_exame, _CONDUTA_GENERICA)
    return condutas_tipo.get(status, _CONDUTA_GENERICA[status])


def extrai_achados_principais(campos: dict) -> list[str]:
    """
    Extrai lista de achados principais a partir do bloco de achados do laudo.

    Parâmetros:
        campos: Dict retornado por pdf_reader.extrai_campos().

    Retorna:
        list[str]: Achados como itens de lista.
    """
    texto_achados = campos.get("achados", "")
    if not texto_achados:
        return ["Achados não identificados no texto."]

    linhas = [l.strip().lstrip("-•* ") for l in texto_achados.splitlines() if l.strip()]
    return linhas if linhas else ["Achados não estruturados no laudo."]


def badge_status(status: str) -> str:
    """Retorna emoji + label legível para o status."""
    return {
        "urgente": "🔴 URGENTE",
        "alterado": "🟡 ALTERADO",
        "normal": "🟢 NORMAL",
    }.get(status, "⚪ INDEFINIDO")

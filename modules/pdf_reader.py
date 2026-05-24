# modules/pdf_reader.py
# Extração de texto de PDFs digitais e parsing de campos médicos.

import re

import pdfplumber


def extrai_texto(caminho_pdf: str) -> str:
    """
    Extrai o texto completo de um PDF digital (gerado por sistema).

    Parâmetros:
        caminho_pdf: Caminho para o arquivo .pdf.

    Retorna:
        Texto extraído como string única. Retorna "" se falhar.
    """
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            paginas = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(paginas).strip()
    except Exception:
        return ""


def extrai_campos(texto: str) -> dict:
    """
    Faz parsing do texto do laudo e extrai campos estruturados.

    Campos extraídos:
        - paciente, data_exame, medico_responsavel
        - tecnica, achados, conclusao, conduta

    Retorna:
        dict com os campos encontrados (valor "" se ausente).
    """
    campos = {
        "paciente":           _extrai_campo(texto, r"PACIENTE[:\s]+(.+)"),
        "data_exame":         _extrai_campo(texto, r"DATA DO EXAME[:\s]+(.+)"),
        "medico_responsavel": _extrai_campo(texto, r"MÉDICO RESPONSÁVEL[:\s]+(.+)"),
        "tecnica":            _extrai_bloco(texto, "TÉCNICA", ["ACHADOS", "CONCLUSÃO", "CONDUTA"]),
        "achados":            _extrai_bloco(texto, "ACHADOS", ["CONCLUSÃO", "CONDUTA", "Documento"]),
        "conclusao":          _extrai_bloco(texto, "CONCLUSÃO", ["CONDUTA", "Documento"]),
        "conduta":            _extrai_bloco(texto, "CONDUTA SUGERIDA", ["Documento"]),
    }
    return campos


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _extrai_campo(texto: str, padrao: str) -> str:
    match = re.search(padrao, texto, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _extrai_bloco(texto: str, inicio: str, fins: list[str]) -> str:
    """Extrai o bloco de texto entre a seção 'inicio' e a primeira seção de 'fins'."""
    fins_pattern = "|".join(re.escape(f) for f in fins)
    padrao = rf"{re.escape(inicio)}[:\s]*\n(.*?)(?={fins_pattern})"
    match  = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()

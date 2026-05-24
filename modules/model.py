# modules/model.py
# Treinamento, persistência e inferência do classificador TF-IDF + LinearSVC.

import os
import pickle
import re
import unicodedata

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC

MODEL_PATH = os.path.join("models", "classifier.pkl")

# ---------------------------------------------------------------------------
# Pré-processamento de texto
# ---------------------------------------------------------------------------

# Campos administrativos que não ajudam a classificar o tipo de exame —
# nomes, datas, CRMs e CPFs são ruído puro para o TF-IDF.
_CAMPOS_ADMINISTRATIVOS = re.compile(
    r"(PACIENTE|NASCIMENTO|PRONTUÁRIO|DATA DO EXAME|SOLICITANTE"
    r"|MÉDICO RESPONSÁVEL|MÉDICO SOLICITANTE|CRM|ASSINATURA"
    r"|INDICAÇÃO CLÍNICA|Documento gerado|Válido sem|CFM)[^\n]*\n?",
    re.IGNORECASE,
)

# Expressões que não carregam semântica médica útil
_RUIDO = re.compile(
    r"\b(\d{2}/\d{2}/\d{4}|\d{2}:\d{2}h?|Dr\.?\s+\w+|CRM\s+\w+-\d+)\b",
    re.IGNORECASE,
)


def preprocessa_texto(texto: str) -> str:
    """
    Aplica pipeline de limpeza em um laudo:

    1. Remove campos administrativos (paciente, data, médico, CRM).
       Esses campos são idênticos em todos os tipos de exame e ensinam
       o modelo a memorizar nomes em vez de aprender terminologia médica.

    2. Converte para minúsculas — padroniza "Consolidação" e "consolidação".

    3. Remove acentos — evita que "consolidação" e "consolidacao" sejam
       tratados como tokens diferentes pelo TF-IDF.

    4. Remove múltiplos espaços e linhas em branco — limpeza final.

    Parâmetros:
        texto (str): Texto bruto extraído do PDF.

    Retorna:
        str: Texto limpo, pronto para vetorização.
    """
    # 1. Remove campos administrativos
    texto = _CAMPOS_ADMINISTRATIVOS.sub(" ", texto)

    # 2. Minúsculas
    texto = texto.lower()

    # 3. Remove acentos (normalização Unicode NFD → mantém só ASCII)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")

    # 4. Remove dígitos isolados e pontuação excessiva
    texto = re.sub(r"\b\d+\b", " ", texto)
    texto = re.sub(r"[^\w\s]", " ", texto)

    # 5. Colapsa espaços múltiplos
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def preprocessa_serie(textos) -> list[str]:
    """Aplica preprocessa_texto a uma lista ou Series de textos."""
    return [preprocessa_texto(t) for t in textos]


# ---------------------------------------------------------------------------
# Treino
# ---------------------------------------------------------------------------

def treina_modelo(df: pd.DataFrame) -> tuple[Pipeline, dict]:
    """
    Treina o pipeline de pré-processamento + TF-IDF + SVM.

    Tratamentos para o desbalanceamento:
    - class_weight='balanced' no LinearSVC: penaliza mais os erros nas
      classes minoritárias (ex: TC de Crânio com 50 registros) em vez de
      deixar o modelo enviesar para as classes maiores (Raio-X com 160).
    - stratify=y no train_test_split: garante proporção de classes no teste.
    - StratifiedKFold: idem na validação cruzada.

    Parâmetros:
        df: DataFrame com colunas 'tipo_exame' e 'descricao'.

    Retorna:
        (modelo treinado, dict com métricas de avaliação)
    """
    X = df["descricao"].tolist()
    y = df["tipo_exame"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        # Etapa 1: pré-processamento — remove ruído administrativo
        ("preprocessor", FunctionTransformer(preprocessa_serie)),

        # Etapa 2: vetorização TF-IDF
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),     # unigramas + bigramas
            max_features=15_000,    # limita dimensionalidade
            sublinear_tf=True,      # log-scaling da frequência
            min_df=2,               # ignora termos que aparecem em < 2 docs
            max_df=0.95,            # ignora termos em > 95% dos docs (stop words implícitas)
            strip_accents="unicode",# segunda camada de normalização de acentos
        )),

        # Etapa 3: classificador com compensação de desbalanceamento
        ("clf", CalibratedClassifierCV(
            LinearSVC(
                C=1.0,
                max_iter=2000,
                random_state=42,
                class_weight="balanced",  # ← compensa desbalanceamento
            ),
            cv=3,
        )),
    ])

    pipeline.fit(X_train, y_train)

    # Métricas no conjunto de teste
    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Validação cruzada estratificada (5 folds)
    cv_scores = cross_val_score(
        pipeline, X, y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="accuracy",
    )

    metricas = {
        "report":        report,
        "cv_mean":       float(cv_scores.mean()),
        "cv_std":        float(cv_scores.std()),
        "test_accuracy": float(report["accuracy"]),
    }

    return pipeline, metricas


def salva_modelo(modelo: Pipeline, path: str = MODEL_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(modelo, f)


def carrega_modelo(path: str = MODEL_PATH) -> Pipeline | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def prediz(modelo: Pipeline, texto: str) -> dict:
    """
    Classifica um texto de laudo.

    Retorna:
        dict com 'tipo_previsto', 'confianca' e 'probabilidades'.
    """
    probs   = modelo.predict_proba([texto])[0]
    classes = modelo.classes_
    idx     = probs.argmax()

    return {
        "tipo_previsto": classes[idx],
        "confianca":     float(probs[idx]),
        "probabilidades": dict(zip(classes, [float(p) for p in probs])),
    }

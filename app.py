# app.py
# Laudo Classifier — Triagem Médica Inteligente
# Ponto de entrada principal do app Streamlit.

import tempfile

import streamlit as st

from modules import (
    badge_confianca,
    badge_status,
    busca_detalhe,
    carrega_dados_treino,
    carrega_modelo,
    cria_conexao,
    detecta_status,
    extrai_achados_principais,
    extrai_campos,
    extrai_texto,
    init_db,
    prediz,
    renderiza_sidebar,
    salva_historico,
    salva_modelo,
    set_theme,
    sugere_condutas,
    treina_modelo,
)

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Laudo Classifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Inicialização (executada uma vez por sessão)
# ---------------------------------------------------------------------------

@st.cache_resource
def init_recursos():
    """Inicializa banco e retorna conexão + modelo treinado."""
    conn   = cria_conexao()
    init_db(conn)
    modelo = carrega_modelo()
    if modelo is None:
        df     = carrega_dados_treino(conn)
        modelo, metricas = treina_modelo(df)
        salva_modelo(modelo)
        return conn, modelo, metricas
    return conn, modelo, None


# ---------------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------------

def main() -> None:
    set_theme()

    conn, modelo, metricas_treino = init_recursos()

    # Sidebar com histórico
    laudo_id_selecionado = renderiza_sidebar(conn)

    # Cabeçalho
    st.title("🏥 Laudo Classifier")
    st.subheader("Triagem Médica Inteligente — Classificação e Sugestão de Condutas")
    st.markdown(
        "Faça upload de um ou mais laudos em PDF. O sistema classifica o tipo de exame, "
        "detecta o status clínico e sugere as próximas condutas para triagem rápida."
    )
    st.markdown("---")

    # Abas principais
    tab_upload, tab_detalhe, tab_modelo = st.tabs([
        "📤 Analisar Laudos",
        "🔎 Detalhe do Laudo",
        "🤖 Informações do Modelo",
    ])

    with tab_upload:
        _aba_upload(conn, modelo)

    with tab_detalhe:
        _aba_detalhe(conn, laudo_id_selecionado)

    with tab_modelo:
        _aba_modelo(conn, metricas_treino)


# ---------------------------------------------------------------------------
# Aba 1 — Upload e análise
# ---------------------------------------------------------------------------

def _aba_upload(conn, modelo) -> None:
    st.markdown("### 📂 Upload de Laudos (PDF)")

    arquivos = st.file_uploader(
        "Arraste ou selecione um ou mais arquivos PDF",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if not arquivos:
        st.info("Aguardando upload de laudos para análise.")
        return

    st.markdown(f"**{len(arquivos)} arquivo(s) carregado(s).** Clique em Analisar para processar.")

    if not st.button("🔬 Analisar Laudos", use_container_width=True):
        return

    st.markdown("---")

    for arquivo in arquivos:
        with st.spinner(f"Analisando {arquivo.name}…"):
            _processa_laudo(conn, modelo, arquivo)


def _processa_laudo(conn, modelo, arquivo) -> None:
    """Processa um único arquivo PDF e exibe o resultado."""

    # 1. Salva temporariamente e extrai texto
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(arquivo.read())
        tmp_path = tmp.name

    texto  = extrai_texto(tmp_path)
    campos = extrai_campos(texto)

    if not texto.strip():
        st.error(f"❌ **{arquivo.name}**: Não foi possível extrair texto. Verifique se o PDF é digital.")
        return

    # 2. Classificação
    resultado = prediz(modelo, texto)
    tipo      = resultado["tipo_previsto"]
    confianca = resultado["confianca"]

    # 3. Análise clínica
    status   = detecta_status(texto)
    achados  = extrai_achados_principais(campos)
    condutas = sugere_condutas(tipo, status)

    # 4. Persiste no banco
    salva_historico(
        conn,
        nome_arquivo   = arquivo.name,
        tipo_previsto  = tipo,
        confianca      = confianca,
        status         = status,
        achados        = "\n".join(achados),
        conduta        = "\n".join(condutas),
        texto_extraido = texto,
    )

    # 5. Renderiza resultado
    _renderiza_resultado(arquivo.name, tipo, confianca, status, achados, condutas, campos)


def _renderiza_resultado(nome, tipo, confianca, status, achados, condutas, campos) -> None:
    """Exibe o card de resultado de um laudo analisado."""

    cor_classe = {"urgente": "card-urgente", "alterado": "card-alterado", "normal": "card-normal"}
    classe_css = cor_classe.get(status, "card")

    st.markdown(f"""
    <div class="card {classe_css}">
        <span class="laudo-titulo">📄 {nome}</span><br><br>
        <b>Tipo de Exame:</b> {tipo} &nbsp;&nbsp; {badge_confianca(confianca)}<br>
        <b>Status Clínico:</b> {badge_status(status)}
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**🔍 Achados Principais**")
        for a in achados:
            st.markdown(f"<div class='conduta-item'>• {a}</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("**📋 Condutas Sugeridas**")
        for c in condutas:
            st.markdown(f"<div class='conduta-item'>{c}</div>", unsafe_allow_html=True)

    # Distribuição de probabilidades
    with st.expander("📊 Distribuição de probabilidades por tipo de exame"):
        resultado_full = prediz(modelo_global(), campos.get("achados", "") + campos.get("conclusao", ""))
        probs = resultado_full["probabilidades"]
        import pandas as pd
        import plotly.express as px
        df_probs = pd.DataFrame(list(probs.items()), columns=["Tipo", "Probabilidade"])
        df_probs = df_probs.sort_values("Probabilidade", ascending=True)
        fig = px.bar(df_probs, x="Probabilidade", y="Tipo", orientation="h",
                     template="plotly_dark", height=300, text_auto=".1%")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")


# ---------------------------------------------------------------------------
# Aba 2 — Detalhe do laudo
# ---------------------------------------------------------------------------

def _aba_detalhe(conn, laudo_id) -> None:
    st.markdown("### 🔎 Detalhes do Laudo Selecionado")

    if laudo_id is None:
        st.info("Selecione um laudo no histórico (barra lateral) para ver os detalhes.")
        return

    detalhe = busca_detalhe(conn, laudo_id)
    if not detalhe:
        st.warning("Laudo não encontrado.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Tipo de Exame",   detalhe["tipo_previsto"])
    c2.metric("Confiança",       f"{detalhe['confianca']*100:.1f}%")
    c3.metric("Status",          badge_status(detalhe["status"]))

    st.markdown("**📋 Condutas Registradas**")
    for linha in detalhe["conduta"].splitlines():
        if linha.strip():
            st.markdown(f"<div class='conduta-item'>{linha}</div>", unsafe_allow_html=True)

    st.markdown("**🔍 Achados Registrados**")
    for linha in detalhe["achados"].splitlines():
        if linha.strip():
            st.markdown(f"<div class='conduta-item'>• {linha}</div>", unsafe_allow_html=True)

    with st.expander("📄 Texto completo extraído do PDF"):
        st.text(detalhe["texto_extraido"])


# ---------------------------------------------------------------------------
# Aba 3 — Informações do modelo
# ---------------------------------------------------------------------------

def _aba_modelo(conn, metricas) -> None:
    st.markdown("### 🤖 Informações do Modelo de Classificação")

    st.markdown("""
    | Componente | Detalhe |
    |---|---|
    | **Algoritmo** | LinearSVC com calibração de probabilidade (CalibratedClassifierCV) |
    | **Vetorização** | TF-IDF com n-gramas (1,2), max 15.000 features, sublinear TF |
    | **Classes** | Raio-X de Tórax, Radiografia de Coluna, Tomografia de Crânio, Tomografia de Abdômen, Ressonância Magnética, Ultrassonografia |
    | **Dados de treino** | 540 laudos sintéticos (90 por classe) |
    | **Validação** | Holdout 80/20 + Validação cruzada estratificada 5-fold |
    """)

    if metricas:
        st.markdown("#### Métricas desta sessão (modelo recém-treinado)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Acurácia no Teste",  f"{metricas['test_accuracy']*100:.1f}%")
        c2.metric("CV Média (5-fold)",  f"{metricas['cv_mean']*100:.1f}%")
        c3.metric("CV Desvio Padrão",   f"±{metricas['cv_std']*100:.1f}%")

        st.markdown("#### Relatório por classe")
        import pandas as pd
        report = metricas["report"]
        rows = []
        for label, vals in report.items():
            if isinstance(vals, dict):
                rows.append({"Classe": label, **vals})
        df_report = pd.DataFrame(rows).set_index("Classe")
        st.dataframe(df_report.style.format("{:.2f}"), use_container_width=True)
    else:
        st.info("Modelo carregado do cache. Remova `models/classifier.pkl` e reinicie para ver métricas.")

    st.markdown("#### 📦 Volume de dados no banco")
    import pandas as pd
    df_vol = pd.read_sql_query(
        "SELECT tipo_exame, COUNT(*) as registros FROM tb_laudos_treino GROUP BY tipo_exame ORDER BY tipo_exame",
        conn,
    )
    st.dataframe(df_vol, use_container_width=True)


# ---------------------------------------------------------------------------
# Helper global para acesso ao modelo na aba de distribuição
# ---------------------------------------------------------------------------

@st.cache_resource
def modelo_global():
    return carrega_modelo()


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# modules/sidebar.py
# Barra lateral: histórico de laudos analisados e estatísticas.

import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.database import carrega_historico, estatisticas


def renderiza_sidebar(conn: sqlite3.Connection) -> int | None:
    """
    Renderiza a sidebar com histórico e gráfico de distribuição.

    Retorna:
        int | None: ID do laudo selecionado para detalhe, ou None.
    """
    st.sidebar.markdown(
        """
        <div style="background-color:#1A6B8A; padding:10px; border-radius:6px;
                    text-align:center; margin-bottom:15px;">
            <h3 style="color:white; margin:0; font-weight:bold;">🏥 Laudo Classifier</h3>
            <p style="color:#cce8f4; margin:4px 0 0 0; font-size:0.85rem;">Triagem Médica Inteligente</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### 📂 Histórico de Análises")

    historico = carrega_historico(conn)

    if historico.empty:
        st.sidebar.info("Nenhum laudo analisado ainda.")
        return None

    laudo_id = _renderiza_tabela_historico(historico)
    _renderiza_grafico_distribuicao(conn)

    return laudo_id


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _renderiza_tabela_historico(df: pd.DataFrame) -> int | None:
    """Exibe tabela de histórico com badge de status colorido."""
    df_exib = df.copy()
    df_exib.columns = ["ID", "Arquivo", "Tipo", "Confiança (%)", "Status", "Analisado em"]

    st.sidebar.dataframe(df_exib, use_container_width=True, height=220)

    ids_disponiveis = df_exib["ID"].tolist()
    if not ids_disponiveis:
        return None

    selecionado = st.sidebar.selectbox(
        "🔍 Ver detalhe do laudo (ID):",
        options=[None] + ids_disponiveis,
        format_func=lambda x: "— selecione —" if x is None else f"Laudo #{x}",
    )
    return selecionado


def _renderiza_grafico_distribuicao(conn: sqlite3.Connection) -> None:
    """Exibe gráfico de pizza com distribuição por tipo de exame."""
    df_stats = estatisticas(conn)
    if df_stats.empty:
        return

    st.sidebar.markdown("### 📊 Distribuição por Tipo")
    fig = px.pie(
        df_stats,
        values="total",
        names="tipo_previsto",
        hole=0.4,
        template="plotly_dark",
        height=280,
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
    st.sidebar.plotly_chart(fig, use_container_width=True)

# modules/theme.py
# Injeção do CSS customizado — tema médico profissional.

import streamlit as st


def set_theme() -> None:
    st.markdown("""
    <style>

        /* Cards de resultado */
        .card {
            background-color: #1e2130;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #333;
            margin-bottom: 12px;
        }

        /* Card de urgência */
        .card-urgente {
            border-left: 5px solid #FF4B4B;
        }

        /* Card alterado */
        .card-alterado {
            border-left: 5px solid #FFA500;
        }

        /* Card normal */
        .card-normal {
            border-left: 5px solid #00CC96;
        }

        /* Badge de confiança */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        .badge-alta  { background-color: #00CC96; color: #000; }
        .badge-media { background-color: #FFA500; color: #000; }
        .badge-baixa { background-color: #FF4B4B; color: #fff; }

        /* Tabela de condutas */
        .conduta-item {
            background-color: #262730;
            border-radius: 6px;
            padding: 10px 14px;
            margin: 6px 0;
            font-size: 0.95rem;
        }

        /* Título do laudo */
        .laudo-titulo {
            font-size: 1.4rem;
            font-weight: bold;
            color: #4fc3f7;
        }

    </style>
    """, unsafe_allow_html=True)


def badge_confianca(confianca: float) -> str:
    """Retorna HTML do badge colorido conforme nível de confiança."""
    pct = confianca * 100
    if pct >= 80:
        cls, label = "badge-alta", f"{pct:.1f}% Alta confiança"
    elif pct >= 55:
        cls, label = "badge-media", f"{pct:.1f}% Confiança média"
    else:
        cls, label = "badge-baixa", f"{pct:.1f}% Baixa confiança"
    return f'<span class="badge {cls}">{label}</span>'

# modules/__init__.py

from modules.analyzer  import badge_status, detecta_status, extrai_achados_principais, sugere_condutas
from modules.database  import (busca_detalhe, carrega_dados_treino, cria_conexao,
                                init_db, salva_historico)
from modules.model     import carrega_modelo, prediz, preprocessa_texto, salva_modelo, treina_modelo
from modules.pdf_reader import extrai_campos, extrai_texto
from modules.seed_data import gera_dataset
from modules.sidebar   import renderiza_sidebar
from modules.theme     import badge_confianca, set_theme

__all__ = [
    "badge_status", "detecta_status", "extrai_achados_principais", "sugere_condutas",
    "busca_detalhe", "carrega_dados_treino", "cria_conexao", "init_db", "salva_historico",
    "carrega_modelo", "prediz", "preprocessa_texto", "salva_modelo", "treina_modelo",
    "extrai_campos", "extrai_texto",
    "gera_dataset",
    "renderiza_sidebar",
    "badge_confianca", "set_theme",
]

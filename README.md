# 🏥 Laudo Classifier — Triagem Médica Inteligente

> Classificação automática de laudos médicos com sugestão de condutas clínicas.  
> Desenvolvido com **Python**, **Streamlit**, **scikit-learn** e **SQLite**.

---

## 🎯 Objetivo

Auxiliar médicos na **triagem rápida** de laudos de imagem, automatizando:

- A **classificação do tipo de exame** (Raio-X, TC, RM, etc.)
- A **detecção do status clínico** (Normal / Alterado / Urgente)
- A **sugestão de condutas** baseadas no tipo e gravidade do achado

---

## 🗂️ Estrutura do Projeto

```
laudo_classifier/
│
├── app.py                    # Ponto de entrada — orquestra todos os módulos
│
├── modules/                  # Pacote Python com a lógica modularizada
│   ├── __init__.py           # Expõe as funções públicas do pacote
│   ├── seed_data.py          # Gerador de 620 laudos sintéticos para treino
│   ├── database.py           # Conexão SQLite, init, histórico e consultas
│   ├── model.py              # Treino, persistência e inferência (TF-IDF + SVM)
│   ├── pdf_reader.py         # Extração de texto e parsing de campos do PDF
│   ├── analyzer.py           # Detecção de status e sugestão de condutas
│   ├── sidebar.py            # Histórico de análises e gráfico de distribuição
│   └── theme.py              # CSS customizado — tema médico profissional
│
├── models/
│   └── .gitkeep              # Pasta mantida no repo — classifier.pkl gerado automaticamente
│
├── laudos_teste/             # PDFs de exemplo para testar o app
│   ├── laudo_teste_01_rm_coluna_alterado.pdf
│   ├── laudo_teste_02_tc_abdomen_urgente.pdf
│   └── laudo_teste_03_rx_coluna_cervical_normal.pdf
│
├── laudos.db                 # Banco SQLite (gerado automaticamente)
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este arquivo
```

---

## 📦 Responsabilidade de Cada Módulo

| Módulo | Responsabilidade |
|---|---|
| `app.py` | Orquestrador — configura página, inicializa recursos, renderiza abas |
| `seed_data.py` | Gera 620 laudos sintéticos com distribuição desbalanceada realista |
| `database.py` | Cria tabelas SQLite, popula dados de treino, salva e consulta histórico |
| `model.py` | Pré-processamento de texto + Pipeline TF-IDF + LinearSVC + CV |
| `pdf_reader.py` | Extrai texto de PDFs digitais e faz parsing dos campos estruturados |
| `analyzer.py` | Detecta status clínico por palavras-chave e sugere condutas por tipo |
| `sidebar.py` | Renderiza histórico de laudos e gráfico de pizza por tipo na sidebar |
| `theme.py` | Injeta CSS com cards coloridos por prioridade e badges de confiança |

---

## 🤖 Modelo de Machine Learning

| Componente | Detalhe |
|---|---|
| **Algoritmo** | LinearSVC com calibração de probabilidade (`CalibratedClassifierCV`) |
| **Vetorização** | TF-IDF com n-gramas (1,2), 15.000 features, sublinear TF |
| **Pré-processamento** | Remoção de campos administrativos, normalização de acentos e minúsculas |
| **Dados de treino** | 620 laudos sintéticos com distribuição desbalanceada |
| **Desbalanceamento** | Tratado com `class_weight='balanced'` no LinearSVC |
| **Validação** | Holdout 80/20 + Validação cruzada estratificada 5-fold |
| **Saída** | Tipo de exame + probabilidade de confiança por classe |

### Distribuição dos dados de treino

| Tipo de Exame | Registros | Representatividade |
|---|---|---|
| Raio-X de Tórax | 160 | Exame mais solicitado na rotina |
| Ultrassonografia | 140 | Segundo mais comum — ambulatorial |
| Tomografia de Abdômen | 110 | Frequente em urgência e eletivo |
| Radiografia de Coluna | 90 | Ortopedia e rotina |
| Ressonância Magnética | 70 | Eletivo, menor volume |
| Tomografia de Crânio | 50 | Urgência, menor volume relativo |
| **Total** | **620** | |

### Por que TF-IDF + LinearSVC?

- Excelente desempenho com texto médico técnico e curto
- Treinamento rápido mesmo com poucos exemplos
- `CalibratedClassifierCV` converte os scores em probabilidades reais
- `class_weight='balanced'` compensa o desbalanceamento entre classes
- Totalmente offline — sem necessidade de API ou GPU

---

## 🖥️ Fluxo do App

```
Médico faz upload de PDF(s)
          ↓
Extração do texto (pdfplumber)
          ↓
Pré-processamento (remove campos administrativos, normaliza texto)
          ↓
Classificação do tipo de exame (TF-IDF + SVM)
          ↓
Detecção do status: Normal / Alterado / Urgente
          ↓
Sugestão de condutas clínicas por tipo e status
          ↓
Resultado visual com cards coloridos por prioridade
          ↓
Salvo no histórico SQLite para consulta posterior
```

---

## 📊 Tipos de Exame Suportados

| Tipo de Exame | Status Possíveis |
|---|---|
| Raio-X de Tórax | Normal / Alterado / Urgente |
| Radiografia de Coluna | Normal / Alterado / Urgente |
| Tomografia de Crânio | Normal / Alterado / Urgente |
| Tomografia de Abdômen | Normal / Alterado / Urgente |
| Ressonância Magnética | Normal / Alterado / Urgente |
| Ultrassonografia | Normal / Alterado / Urgente |

---

## 🚀 Como Executar

### 1. Criar o ambiente virtual (Conda)

```bash
conda create --name laudoclf python=3.11
```

### 2. Ativar o ambiente

```bash
conda activate laudoclf
```

### 3. Instalar as dependências

```bash
conda install pip
pip install -r requirements.txt
```

### 4. Executar o app

```bash
streamlit run app.py
```

> Na primeira execução o banco SQLite é criado, os 620 laudos são inseridos e o modelo é treinado automaticamente. Isso leva cerca de 30 segundos.

---

## 🧪 Laudos de Teste

A pasta `laudos_teste/` contém 3 PDFs prontos para testar o app:

| Arquivo | Exame | Status Esperado |
|---|---|---|
| `laudo_teste_01_rm_coluna_alterado.pdf` | Ressonância Magnética | 🟡 Alterado |
| `laudo_teste_02_tc_abdomen_urgente.pdf` | Tomografia de Abdômen | 🔴 Urgente |
| `laudo_teste_03_rx_coluna_cervical_normal.pdf` | Radiografia de Coluna | 🟢 Normal |

---

## 🛑 Desativar / Remover o Ambiente (opcional)

```bash
conda deactivate
conda remove --name laudoclf --all
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| **Python 3.11** | Linguagem principal |
| **Streamlit 1.40** | Interface web interativa |
| **scikit-learn** | Pipeline TF-IDF + LinearSVC + validação cruzada |
| **pdfplumber** | Extração de texto de PDFs digitais |
| **SQLite** | Banco de dados local para treino e histórico |
| **Pandas** | Manipulação de dados |
| **Plotly Express** | Gráficos interativos (pizza, barras horizontais) |

---

## ⚠️ Aviso Importante

> Este sistema é uma **ferramenta de apoio à decisão clínica** e **não substitui o julgamento médico**.  
> As condutas sugeridas são baseadas em regras heurísticas e devem sempre ser avaliadas pelo profissional de saúde responsável.

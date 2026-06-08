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
│   ├── seed_data.py          # Gerador de 540 laudos sintéticos para treino
│   ├── database.py           # Conexão SQLite, init, histórico e consultas
│   ├── model.py              # Treino, persistência e inferência (TF-IDF + SVM)
│   ├── pdf_reader.py         # Extração de texto e parsing de campos do PDF
│   ├── analyzer.py           # Detecção de status e sugestão de condutas
│   ├── sidebar.py            # Histórico de análises e gráfico de distribuição
│   └── theme.py              # CSS customizado — tema médico profissional
│
├── models/
│   └── classifier.pkl        # Modelo treinado (gerado automaticamente)
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
| `seed_data.py` | Gera 540 laudos sintéticos realistas com achados, conclusões e condutas |
| `database.py` | Cria tabelas SQLite, popula dados de treino, salva e consulta histórico |
| `model.py` | Pipeline TF-IDF + LinearSVC, treino com CV, persistência e predição |
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
| **Dados de treino** | 540 laudos sintéticos — 90 por classe |
| **Validação** | Holdout 80/20 + Validação cruzada estratificada 5-fold |
| **Saída** | Tipo de exame + probabilidade de confiança por classe |

### Por que TF-IDF + LinearSVC?

- Excelente desempenho com texto médico técnico e curto
- Treinamento rápido mesmo com poucos exemplos
- `CalibratedClassifierCV` converte os scores em probabilidades reais
- Totalmente offline — sem necessidade de API ou GPU

---

## 🖥️ Fluxo do App

```
Médico faz upload de PDF(s)
          ↓
Extração do texto (pdfplumber)
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

> Na primeira execução o banco SQLite é criado, os 540 laudos são inseridos e o modelo é treinado automaticamente. Isso leva cerca de 30 segundos.

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

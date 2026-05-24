# modules/seed_data.py
# Gerador de dados sintéticos de laudos médicos para treino do modelo.
# Produz 540 registros balanceados (90 por classe × 6 tipos de exame).

import random

# ---------------------------------------------------------------------------
# Corpus de frases por tipo de exame
# ---------------------------------------------------------------------------

_CORPUS: dict[str, dict] = {

    "Raio-X de Tórax": {
        "normais": [
            "Campos pulmonares com transparência preservada.",
            "Área cardíaca dentro dos limites da normalidade.",
            "Seios costofrênicos livres bilateralmente.",
            "Mediastino com dimensões normais.",
            "Traqueia centrada sem desvios.",
            "Hilos pulmonares com morfologia habitual.",
            "Parênquima pulmonar sem consolidações ou infiltrados.",
            "Arcabouço ósseo do tórax sem alterações.",
            "Diafragma com contornos regulares.",
            "Vascularização pulmonar normal.",
        ],
        "alterados": [
            "Opacidade em base pulmonar direita, sugestiva de consolidação.",
            "Aumento da área cardíaca compatível com cardiomegalia grau II.",
            "Velamento do seio costofrênico esquerdo, possível derrame pleural.",
            "Infiltrado intersticial difuso bilateral.",
            "Nódulo pulmonar solitário no lobo superior direito, mede cerca de 1,2 cm.",
            "Hiperinsuflação pulmonar com retificação dos diafragmas.",
            "Alargamento mediastinal superior.",
            "Linfonodomegalia hilar bilateral.",
            "Pneumotórax apical direito de pequena monta.",
            "Calcificações pleurais residuais à esquerda.",
            "Atelectasia laminar em base esquerda.",
            "Processo inflamatório em lobo médio direito.",
        ],
        "conclusoes_normais": [
            "Radiografia de tórax sem alterações significativas.",
            "Estudo radiográfico do tórax dentro da normalidade.",
            "Exame de tórax sem achados patológicos relevantes.",
        ],
        "conclusoes_alteradas": [
            "Achados sugestivos de pneumonia em base pulmonar direita. Correlacionar clinicamente.",
            "Cardiomegalia. Recomenda-se avaliação cardiológica.",
            "Derrame pleural à esquerda. Seguimento clínico recomendado.",
            "Nódulo pulmonar identificado. Recomenda-se tomografia para melhor caracterização.",
            "Achados compatíveis com DPOC. Correlação clínica e funcional recomendada.",
        ],
        "condutas_normal": [
            "Nenhuma conduta imediata necessária. Manter acompanhamento de rotina.",
            "Exame sem alterações. Repetir conforme protocolo clínico.",
        ],
        "condutas_alterada": [
            "Iniciar antibioticoterapia empírica para pneumonia comunitária. Reavaliar em 48-72h.",
            "Encaminhar para cardiologia. Solicitar ecocardiograma.",
            "Solicitar ultrassonografia pleural para quantificação do derrame. Avaliar toracocentese.",
            "Solicitar TC de tórax com contraste para caracterização do nódulo. Seguir protocolo Lung-RADS.",
            "Solicitar espirometria. Encaminhar para pneumologia.",
        ],
    },

    "Radiografia de Coluna": {
        "normais": [
            "Alinhamento vertebral preservado em todos os segmentos.",
            "Espaços intervertebrais com altura mantida.",
            "Corpos vertebrais com densidade e morfologia normais.",
            "Pedículos íntegros bilateralmente.",
            "Lordose cervical e lombar fisiológicas.",
            "Cifose torácica dentro dos parâmetros normais.",
            "Processos espinhosos alinhados na linha média.",
            "Articulações facetárias sem alterações degenerativas.",
            "Foramens de conjugação com dimensões preservadas.",
            "Transição lombossacral sem particularidades.",
        ],
        "alterados": [
            "Redução da altura do disco intervertebral em L4-L5.",
            "Osteófitos marginais anteriores em vértebras torácicas.",
            "Escoliose lombar com convexidade à direita, Cobb de aproximadamente 18 graus.",
            "Espondilolistese grau I em L5-S1.",
            "Retificação da lordose lombar, compatível com contratura muscular.",
            "Osteopenia difusa da coluna vertebral.",
            "Fratura por compressão em corpo de T12.",
            "Espondiloartrose cervical com redução dos espaços em C5-C6 e C6-C7.",
            "Hiperostose esquelética difusa idiopática (DISH).",
            "Sacralização de L5 bilateral.",
            "Acunhamento anterior do corpo vertebral de L1.",
            "Estenose do canal vertebral em nível lombar.",
        ],
        "conclusoes_normais": [
            "Radiografia de coluna sem alterações estruturais significativas.",
            "Estudo radiográfico da coluna dentro dos limites da normalidade.",
            "Coluna vertebral sem achados patológicos ao exame radiográfico.",
        ],
        "conclusoes_alteradas": [
            "Alterações degenerativas em coluna lombar. Correlação clínica recomendada.",
            "Escoliose lombar leve. Acompanhamento ortopédico sugerido.",
            "Fratura vertebral identificada. Avaliação especializada urgente.",
            "Espondilolistese em L5-S1. Recomenda-se RM para avaliação dos tecidos moles.",
            "Osteopenia vertebral. Investigação de causa base indicada.",
        ],
        "condutas_normal": [
            "Sem conduta imediata. Orientar sobre postura e ergonomia.",
            "Exame dentro da normalidade. Acompanhamento clínico conforme sintomatologia.",
        ],
        "condutas_alterada": [
            "Encaminhar para ortopedia. Considerar fisioterapia e analgesia.",
            "Solicitar RM de coluna lombar para avaliação de partes moles e compressão radicular.",
            "Conduta de emergência: imobilização e avaliação neurocirúrgica imediata para fratura vertebral.",
            "Solicitar densitometria óssea. Iniciar investigação de osteoporose.",
            "Encaminhar para ortopedia pediátrica ou cirurgia da coluna conforme grau da escoliose.",
        ],
    },

    "Tomografia de Crânio": {
        "normais": [
            "Parênquima encefálico com densidade e morfologia preservadas.",
            "Sistema ventricular com dimensões normais e simétrico.",
            "Sulcos e cisternas com aspecto habitual para a faixa etária.",
            "Linha média centrada sem desvios.",
            "Estruturas da fossa posterior sem alterações.",
            "Interface substância branca e cinzenta bem definida.",
            "Ausência de coleções extra-axiais.",
            "Ossos do crânio sem soluções de continuidade.",
            "Seios da face com aeração normal.",
            "Órbitas simétricas sem alterações.",
        ],
        "alterados": [
            "Hipodensidade em território da artéria cerebral média esquerda, sugestiva de infarto isquêmico agudo.",
            "Hiperdensidade espontânea em putâmen direito, compatível com hematoma hipertensivo.",
            "Edema cerebral difuso com apagamento dos sulcos corticais.",
            "Desvio da linha média para a direita em aproximadamente 8 mm.",
            "Coleção subdural aguda frontoparietal esquerda.",
            "Fratura linear do osso temporal direito com pneumoencéfalo associado.",
            "Lesão expansiva com realce pelo contraste em lobo frontal direito.",
            "Hidrocefalia com dilatação do sistema ventricular.",
            "Calcificações nos núcleos da base bilateralmente.",
            "Atrofia cortical difusa desproporcional para a idade.",
            "Hemorragia subaracnóidea nas cisternas basais.",
            "Múltiplas lesões hipodensas bilaterais sugestivas de metástases.",
        ],
        "conclusoes_normais": [
            "Tomografia de crânio sem alterações agudas.",
            "Estudo tomográfico do crânio dentro da normalidade.",
            "Tomografia craniana sem achados patológicos identificados.",
        ],
        "conclusoes_alteradas": [
            "Achados compatíveis com AVC isquêmico agudo. Conduta neurológica urgente.",
            "Hematoma intraparenquimatoso hipertensivo. Avaliação neurocirúrgica imediata.",
            "Lesão expansiva intracraniana. Investigação complementar com RM.",
            "Hidrocefalia. Avaliação neurocirúrgica recomendada.",
            "Hemorragia subaracnóidea. Investigação de aneurisma indicada.",
        ],
        "condutas_normal": [
            "TC sem alterações agudas. Conduta conforme quadro clínico.",
            "Sem achados tomográficos. Investigação adicional se sintomatologia persistir.",
        ],
        "condutas_alterada": [
            "URGÊNCIA: Ativar protocolo de AVC. Avaliar trombólise ou trombectomia mecânica conforme tempo de janela.",
            "URGÊNCIA: Acionar neurocirurgia imediatamente para avaliação de hematoma expansivo.",
            "Solicitar RM com contraste para melhor caracterização da lesão. Encaminhar neurologia/neurocirurgia.",
            "Acionar neurocirurgia para avaliação de derivação ventricular.",
            "URGÊNCIA: Solicitar angiotomografia cerebral para pesquisa de aneurisma. Internação em UTI.",
        ],
    },

    "Tomografia de Abdômen": {
        "normais": [
            "Fígado com dimensões normais, contornos regulares e parênquima homogêneo.",
            "Vesícula biliar sem cálculos ou espessamento parietal.",
            "Pâncreas com morfologia e densidade preservadas.",
            "Baço com dimensões normais e ecotextura homogênea.",
            "Rins com dimensões, contornos e realce normais.",
            "Alças intestinais sem distensão ou espessamento parietal.",
            "Aorta abdominal com calibre normal.",
            "Ausência de linfonodomegalias abdominais.",
            "Ausência de líquido livre na cavidade abdominal.",
            "Glândulas adrenais sem nodulações.",
        ],
        "alterados": [
            "Múltiplos cálculos na vesícula biliar, o maior medindo 1,5 cm.",
            "Dilatação das vias biliares intra e extra-hepáticas.",
            "Lesão hipodensa no segmento VI do fígado medindo 3,2 cm.",
            "Pancreatite aguda com coleção peripancreática.",
            "Esplenomegalia com baço medindo 16 cm.",
            "Cisto renal simples no rim direito medindo 4 cm, Bosniak I.",
            "Apendicite aguda com apêndice medindo 1,1 cm de diâmetro.",
            "Massa retroperitoneal sólida à direita.",
            "Ascite de moderado volume.",
            "Nódulos hepáticos múltiplos sugestivos de metástases.",
            "Aneurisma de aorta abdominal medindo 5,2 cm.",
            "Hérnia inguinal direta à esquerda com alça encarcerada.",
        ],
        "conclusoes_normais": [
            "Tomografia de abdômen sem alterações significativas.",
            "Estudo tomográfico abdominal dentro dos limites da normalidade.",
            "Órgãos abdominais sem achados patológicos ao estudo tomográfico.",
        ],
        "conclusoes_alteradas": [
            "Colelitíase. Avaliação cirúrgica recomendada.",
            "Lesão hepática focal. RM com contraste indicada para melhor caracterização.",
            "Pancreatite aguda. Tratamento clínico e monitorização intensiva.",
            "Apendicite aguda. Cirurgia de urgência indicada.",
            "Aneurisma de aorta abdominal. Avaliação vascular urgente.",
        ],
        "condutas_normal": [
            "TC de abdômen sem alterações. Seguimento clínico conforme indicação.",
            "Sem achados patológicos. Manter acompanhamento de rotina.",
        ],
        "condutas_alterada": [
            "Encaminhar para cirurgia geral para avaliação de colecistectomia.",
            "Solicitar RM hepática com hepatospecific contrast. Discutir em equipe multidisciplinar.",
            "URGÊNCIA: Internação, jejum, hidratação venosa, analgesia e monitorização para pancreatite aguda. Escore de Ranson.",
            "URGÊNCIA: Encaminhar para centro cirúrgico para apendicectomia de emergência.",
            "URGÊNCIA: Acionar cirurgia vascular para avaliação de correção do aneurisma de aorta.",
        ],
    },

    "Ressonância Magnética": {
        "normais": [
            "Sinal do parênquima cerebral homogêneo em todas as sequências.",
            "Substância branca sem alterações de sinal.",
            "Hipocampos com volume e sinal normais bilateralmente.",
            "Corpo caloso íntegro com espessura normal.",
            "Cerebelo e tronco encefálico sem alterações.",
            "Nervos cranianos com trajeto e sinal normais.",
            "Hipófise com dimensões e sinal habituais.",
            "Articulações sem derrame ou alteração da cartilagem.",
            "Meniscos com morfologia e sinal normais.",
            "Ligamentos cruzados íntegros.",
        ],
        "alterados": [
            "Lesões em substância branca periventricular hiperintensas em T2/FLAIR, sugestivas de desmielinização.",
            "Redução volumétrica hipocampal bilateral, compatível com atrofia hipocampal.",
            "Lesão expansiva sólido-cística em lobo temporal direito com edema perilesional.",
            "Rotura parcial do ligamento cruzado anterior.",
            "Lesão meniscal complexa em corno posterior do menisco medial.",
            "Hérnia discal em L4-L5 com compressão radicular.",
            "Artrose glenoumeral com irregularidade da cartilagem articular.",
            "Coleção articular moderada no joelho esquerdo.",
            "Edema ósseo em côndilo femoral medial.",
            "Microangiopatia hipertensiva com múltiplos focos lacunares.",
            "Adenoma hipofisário medindo 8 mm.",
            "Lesões metastáticas ósseas em vértebras lombares.",
        ],
        "conclusoes_normais": [
            "Ressonância magnética sem alterações de sinal ou morfologia.",
            "Estudo por ressonância magnética dentro dos limites da normalidade.",
            "Exame de ressonância magnética sem achados patológicos.",
        ],
        "conclusoes_alteradas": [
            "Achados compatíveis com esclerose múltipla. Correlação clínica e laboratorial recomendada.",
            "Lesão expansiva intracraniana. Investigação neurológica e neurocirúrgica urgente.",
            "Rotura ligamentar identificada. Avaliação ortopédica recomendada.",
            "Hérnia discal com compressão radicular. Tratamento conservador ou cirúrgico conforme avaliação.",
            "Adenoma hipofisário. Investigação endocrinológica indicada.",
        ],
        "condutas_normal": [
            "RM sem alterações. Acompanhamento clínico conforme quadro.",
            "Exame dentro da normalidade. Reavaliar se houver progressão sintomática.",
        ],
        "condutas_alterada": [
            "Encaminhar para neurologia. Solicitar potencial evocado e LCR para confirmação de esclerose múltipla.",
            "URGÊNCIA: Encaminhar para neurocirurgia. Considerar biópsia estereotáxica.",
            "Encaminhar para ortopedia. Avaliar indicação cirúrgica de reconstrução ligamentar.",
            "Iniciar tratamento conservador: analgesia, fisioterapia. Reavaliar em 6 semanas. Se refratário, discutir cirurgia.",
            "Solicitar dosagem de hormônios hipofisários. Encaminhar endocrinologia. Avaliar campimetria visual.",
        ],
    },

    "Ultrassonografia": {
        "normais": [
            "Fígado com ecogenicidade e dimensões normais.",
            "Vesícula biliar de paredes finas sem cálculos.",
            "Pâncreas com ecotextura homogênea.",
            "Baço com ecogenicidade e dimensões normais.",
            "Rins com dimensões e índice córtico-medular preservados.",
            "Bexiga com paredes regulares e conteúdo anecoico.",
            "Útero com dimensões normais e endométrio regular.",
            "Ovários com volume e morfologia normais.",
            "Próstata com volume normal estimado em 25 gramas.",
            "Ausência de líquido livre na cavidade.",
        ],
        "alterados": [
            "Esteatose hepática difusa de grau moderado.",
            "Cálculo único na vesícula biliar medindo 0,8 cm com sombra acústica posterior.",
            "Esplenomegalia homogênea medindo 14 cm.",
            "Cisto renal simples no rim esquerdo medindo 3 cm.",
            "Hidronefrose leve à direita.",
            "Nódulo sólido em tireoide com 1,1 cm, TIRADS 4.",
            "Miomatose uterina com nódulo intramural de 4 cm.",
            "Cisto ovariano simples à esquerda medindo 5 cm.",
            "Hiperplasia prostática benigna com volume de 65 gramas.",
            "Linfonodomegalia inguinal bilateral.",
            "Derrame pericárdico de pequena monta.",
            "Nódulo hepático hipoecogênico no lobo direito medindo 2 cm.",
        ],
        "conclusoes_normais": [
            "Ultrassonografia abdominal sem alterações.",
            "Estudo ultrassonográfico dentro dos limites da normalidade.",
            "Ultrassonografia sem achados patológicos identificados.",
        ],
        "conclusoes_alteradas": [
            "Esteatose hepática. Correlação clínica e laboratorial recomendada.",
            "Colelitíase. Avaliação cirúrgica conforme sintomatologia.",
            "Nódulo tireoidiano TIRADS 4. Biópsia por punção aspirativa recomendada.",
            "Mioma uterino. Acompanhamento ginecológico.",
            "Hiperplasia prostática. Avaliação urológica.",
        ],
        "condutas_normal": [
            "Ultrassonografia sem alterações. Seguimento de rotina.",
            "Sem achados patológicos. Repetir conforme protocolo clínico.",
        ],
        "condutas_alterada": [
            "Solicitar perfil lipídico e enzimas hepáticas. Orientar dieta e atividade física para esteatose.",
            "Encaminhar cirurgia geral para avaliação de colecistectomia laparoscópica.",
            "PAAF (punção aspirativa por agulha fina) guiada por US para nódulo TIRADS 4. Encaminhar endocrinologia.",
            "Encaminhar ginecologia. Avaliar indicação de miomectomia ou histerectomia.",
            "Encaminhar urologia. Solicitar PSA e urofluxometria.",
        ],
    },
}

_TECNICAS: dict[str, list[str]] = {
    "Raio-X de Tórax": [
        "Radiografia do tórax em incidências póstero-anterior (PA) e perfil.",
        "Radiografia do tórax em AP portátil à beira leito.",
        "Radiografia do tórax em PA com técnica digital.",
    ],
    "Radiografia de Coluna": [
        "Radiografia da coluna lombar em AP e perfil, com incidências oblíquas.",
        "Radiografia da coluna cervical em AP, perfil e oblíquas.",
        "Radiografia da coluna total em AP e perfil.",
    ],
    "Tomografia de Crânio": [
        "Tomografia computadorizada do crânio sem contraste, cortes axiais de 5 mm.",
        "Tomografia computadorizada do crânio com e sem contraste endovenoso.",
        "Tomografia de crânio sem contraste com reconstruções multiplanares.",
    ],
    "Tomografia de Abdômen": [
        "Tomografia computadorizada de abdômen e pelve com contraste nas fases arterial, portal e tardia.",
        "Tomografia de abdômen total sem contraste.",
        "Tomografia de abdômen com contraste endovenoso — fase portal.",
    ],
    "Ressonância Magnética": [
        "Ressonância magnética com sequências T1, T2, FLAIR, DWI e T1 pós-contraste.",
        "RM de joelho com sequências DP Fat-Sat, T2 e T1 nos três planos.",
        "RM de coluna lombossacra com sequências sagitais T1, T2 e axiais T2.",
    ],
    "Ultrassonografia": [
        "Ultrassonografia abdominal total com transdutor convexo de 3,5 MHz.",
        "Ultrassonografia pélvica transvaginal.",
        "Ultrassonografia de tireoide com transdutor linear de alta frequência.",
    ],
}

_NOMES = [
    "Ana Paula Silva", "Carlos Eduardo Souza", "Maria Fernanda Lima",
    "João Pedro Oliveira", "Beatriz Santos", "Rafael Alves Costa",
    "Juliana Martins", "Lucas Ferreira", "Patricia Rocha", "Fernando Nunes",
    "Camila Araújo", "Diego Carvalho", "Aline Ribeiro", "Thiago Mendes",
    "Larissa Gomes", "Bruno Pereira", "Gabriela Castro", "Rodrigo Teixeira",
    "Isabela Barbosa", "Marcelo Freitas",
]

_SOLICITANTES = [
    "Ricardo Andrade", "Claudia Borges", "Henrique Dias", "Simone Ramos",
    "Paulo Nascimento", "Vanessa Pinto", "Alexandre Moura", "Renata Azevedo",
]

_RESPONSAVEIS = [
    ("Felipe Cardoso",  "SP-45231"),
    ("Mariana Lopes",   "RJ-38741"),
    ("André Monteiro",  "MG-52187"),
    ("Tatiana Correia", "RS-29634"),
    ("Eduardo Fonseca", "BA-41093"),
]

_DATAS = [
    f"{d:02d}/{m:02d}/2025"
    for m in range(1, 13)
    for d in range(1, 29, 4)
]

_TEMPLATE = """LAUDO MÉDICO — {tipo_exame}

PACIENTE: {nome}
DATA DO EXAME: {data}
MÉDICO SOLICITANTE: Dr(a). {solicitante}
MÉDICO RESPONSÁVEL: Dr(a). {responsavel} — CRM {crm}

TÉCNICA:
{tecnica}

ACHADOS:
{achados}

CONCLUSÃO:
{conclusao}

CONDUTA SUGERIDA:
{conduta}

Documento gerado eletronicamente. Válido sem assinatura física conforme CFM 1.821/2007.
"""


def gera_dataset(n_por_classe: int = None) -> list[dict]:
    """
    Gera laudos sintéticos com distribuição levemente desbalanceada,
    refletindo a frequência relativa de cada exame na prática clínica real.

    Distribuição:
        Raio-X de Tórax        → 160  (exame mais solicitado na rotina)
        Ultrassonografia       → 140  (segundo mais comum — ambulatorial)
        Tomografia de Abdômen  → 110  (urgência + eletivo)
        Radiografia de Coluna  →  90  (ortopedia / rotina)
        Ressonância Magnética  →  70  (eletivo, menor volume)
        Tomografia de Crânio   →  50  (urgência, menor volume relativo)
                               ------
        Total                  → 620 registros

    O parâmetro n_por_classe é ignorado quando None (mantido por
    compatibilidade com chamadas antigas).

    Retorna:
        list[dict] com chaves 'tipo_exame' e 'descricao'.
    """
    # Quantidade por classe — levemente desbalanceada (~3:1 entre maior e menor)
    DISTRIBUICAO: dict[str, int] = {
        "Raio-X de Tórax":       160,
        "Ultrassonografia":      140,
        "Tomografia de Abdômen": 110,
        "Radiografia de Coluna":  90,
        "Ressonância Magnética":  70,
        "Tomografia de Crânio":   50,
    }

    random.seed(42)
    dataset: list[dict] = []

    for tipo, n in DISTRIBUICAO.items():
        corpus = _CORPUS[tipo]
        for i in range(n):
            alterado = (i % 3 != 0)  # ~66% alterados, ~33% normais

            pool      = corpus["alterados"] if alterado else corpus["normais"]
            achados   = random.sample(pool, random.randint(3, min(5, len(pool))))
            conclusao = random.choice(corpus["conclusoes_alteradas"] if alterado else corpus["conclusoes_normais"])
            conduta   = random.choice(corpus["condutas_alterada"] if alterado else corpus["condutas_normal"])

            resp, crm = random.choice(_RESPONSAVEIS)
            descricao = _TEMPLATE.format(
                tipo_exame  = tipo,
                nome        = random.choice(_NOMES),
                data        = random.choice(_DATAS),
                solicitante = random.choice(_SOLICITANTES),
                responsavel = resp,
                crm         = crm,
                tecnica     = random.choice(_TECNICAS[tipo]),
                achados     = "\n".join(f"- {a}" for a in achados),
                conclusao   = conclusao,
                conduta     = conduta,
            )

            dataset.append({"tipo_exame": tipo, "descricao": descricao})

    random.shuffle(dataset)
    return dataset

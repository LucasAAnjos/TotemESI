import base64
import os
import requests
import streamlit as st
import streamlit.components.v1 as components


# ==============================================================================
# CONFIGURAÇÃO DO TOTEM
# ==============================================================================

st.set_page_config(
    page_title="Totem de Autoatendimento Hospitalar",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==============================================================================
# FUNÇÕES
# ==============================================================================
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

# --- FUNÇÃO PARA REPRODUZIR ÁUDIO VIA NAVEGADOR (WEB SPEECH API) ---
def falar_orientacao(texto: str):
    """Injeta um script JavaScript para executar a síntese de voz nativa do navegador em português."""
    js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                // Cancela qualquer fala anterior em andamento
                window.speechSynthesis.cancel();
                
                var msg = new SpeechSynthesisUtterance();
                msg.text = "{texto}";
                msg.lang = 'pt-BR';
                msg.rate = 1.0;  // Velocidade normal da fala
                msg.pitch = 1.0; // Tom normal
                
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """
    # Executa o componente HTML/JS de forma invisível
    components.html(js_code, height=0, width=0)


# ==============================================================================
# ESTADO DA APLICAÇÃO
# ==============================================================================

if "etapa" not in st.session_state:
    st.session_state.etapa = 0

if "dados_paciente" not in st.session_state:
    st.session_state.dados_paciente = {
        "nome": "",
        "idade": 18,
        "queixa": "",
        "temperatura": 36.5,
        "spo2": 98,
        "frequencia_cardiaca": 75,
        "frequencia_respiratoria": 16,
        "dor": 0,
    }


# ==============================================================================
# CSS GLOBAL
# ==============================================================================

st.markdown(
    """
    <style>

    /* ==========================================================================
       INTERFACE DO STREAMLIT
       ========================================================================== */

    /* Remove barra superior */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* Remove rodapé "Made with Streamlit" */
    footer {
        display: none;
    }

    /* Remove menu lateral */
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Espaçamento principal */
    .stMainBlockContainer {
        padding-top: 2rem;
        padding-bottom: 125px;
    }


    /* ==========================================================================
       CABEÇALHO DAS ETAPAS
       ========================================================================== */

    .etapa-header {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 10px;
    }

    .etapa-numero {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 24px;
        font-weight: 700;

        background-color: #e8f0fe;
        color: #1a5fb4;

        flex-shrink: 0;
    }

    .etapa-header h1 {
        margin: 0;
        font-size: 32px;
        line-height: 1.2;
    }

    .etapa-header p {
        margin: 4px 0 0 0;
        font-size: 18px;
        color: #5f6368;
    }


    /* ==========================================================================
       FORMULÁRIOS
       ========================================================================== */

    .form-titulo {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .form-ajuda {
        font-size: 17px;
        color: #5f6368;
        line-height: 1.4;
    }

    .campo-opcional {
        font-size: 15px;
        color: #6b7280;
        margin-top: -10px;
    }


    /* ==========================================================================
       CAMPOS
       ========================================================================== */

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        min-height: 58px;
        font-size: 20px !important;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 130px;
    }


    /* ==========================================================================
       LABELS
       ========================================================================== */

    div[data-testid="stTextInput"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSlider"] label {
        font-size: 18px !important;
        font-weight: 600 !important;
    }


    /* ==========================================================================
       BOTÕES
       ========================================================================== */

    div[data-testid="stButton"] > button {
        min-height: 64px;
        border-radius: 8px;
    }

    div[data-testid="stButton"] > button p {
        font-size: 21px !important;
        font-weight: 600;
    }


    /* ==========================================================================
       NAVEGAÇÃO FIXA DO TOTEM
       ========================================================================== */

    /*
       O container criado com:

           st.container(key="navegacao-totem")

       recebe automaticamente a classe:

           .st-key-navegacao-totem
    */

    .st-key-navegacao-totem {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;

        z-index: 999;

        padding: 14px 5vw 18px 5vw;

        background-color: #ffffff;
        border-top: 1px solid #dfe3e8;

        box-shadow: 0 -3px 12px rgba(0, 0, 0, 0.08);
    }

    /* Botões dentro da barra inferior */
    .st-key-navegacao-totem div[data-testid="stButton"] > button {
        min-height: 64px;
        border-radius: 8px;
    }

    .st-key-navegacao-totem div[data-testid="stButton"] > button p {
        font-size: 21px !important;
        font-weight: 600;
    }


    /* ==========================================================================
       RESPONSIVIDADE
       ========================================================================== */

    @media (max-width: 800px) {

        .stMainBlockContainer {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 120px;
        }

        .etapa-header h1 {
            font-size: 28px;
        }

        .etapa-header p {
            font-size: 16px;
        }

        .st-key-navegacao-totem {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .st-key-navegacao-totem div[data-testid="stButton"] > button p {
            font-size: 18px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# ETAPA 0: TELA DE STANDBY
# ==============================================================================

if st.session_state.etapa == 0:

    st.space(4)

    # --------------------------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align: center;
            margin-top: 40px;
            margin-bottom: 55px;
        ">
            <div style="
                font-size: 42px;
                font-weight: 600;
                color: #263238;
                margin-bottom: 12px;
            ">
                Estação de Autoatendimento
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # BOTÕES
    # --------------------------------------------------------------------------

    col_l, col_buttons, col_r = st.columns([1, 2, 1])

    with col_buttons:

        if st.button(
            "Iniciar atendimento",
            width="stretch",
            type="primary",
        ):
            st.session_state.dados_paciente = {
                "nome": "",
                "idade": 18,
                "queixa": "",
                "temperatura": 36.5,
                "spo2": 98,
                "frequencia_cardiaca": 75,
                "frequencia_respiratoria": 16,
                "dor": 0,
            }

            if "resultado_classificacao" in st.session_state:
                del st.session_state.resultado_classificacao

            st.session_state.etapa = 1
            st.rerun()

        st.space(1)

        if st.button(
            "Pedir ajuda",
            width="stretch",
        ):
            st.session_state.mostrar_ajuda = True
            st.rerun()


# ==============================================================================
# ETAPAS DE ATENDIMENTO
# ==============================================================================

else:

    # ==========================================================================
    # INDICADOR DE PROGRESSO
    # ==========================================================================

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        if st.session_state.etapa == 1:
            st.subheader("1. Identificação")
        else:
            st.write("1. Identificação")

    with col_p2:
        if st.session_state.etapa == 2:
            st.subheader("2. Temperatura")
        else:
            st.write("2. Temperatura")

    with col_p3:
        if st.session_state.etapa == 3:
            st.subheader("3. Sinais vitais")
        else:
            st.write("3. Sinais vitais")

    st.progress(st.session_state.etapa / 3)


    # ==========================================================================
    # ETAPA 1: CADASTRO DO PACIENTE
    # ==========================================================================

    if st.session_state.etapa == 1:

        falar_orientacao(
            "Por favor, informe seu nome completo e sua idade para iniciar o atendimento."
        )

        # ----------------------------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------------------------

        with st.container(border=False):

            st.markdown(
                '<div class="form-titulo">Dados do paciente</div>',
                unsafe_allow_html=True,
            )

            st.space(1)

            nome = st.text_input(
                "Nome completo *",
                value=st.session_state.dados_paciente["nome"],
                placeholder="Digite seu nome completo",
            )

            idade = st.number_input(
                "Idade *",
                min_value=0,
                max_value=120,
                value=st.session_state.dados_paciente["idade"],
                step=1,
            )

            queixa = st.text_area(
                "Motivo da consulta",
                value=st.session_state.dados_paciente["queixa"],
                placeholder="Ex.: estou com dor de cabeça desde ontem",
                height=120,
            )


        # ----------------------------------------------------------------------
        # NAVEGAÇÃO
        # ----------------------------------------------------------------------

        with st.container(key="navegacao-totem"):

            c_back, c_next = st.columns([1, 2])

            with c_back:

                if st.button(
                    "← Voltar ao início",
                    use_container_width=True,
                ):
                    st.session_state.etapa = 0
                    st.rerun()

            with c_next:

                if st.button(
                    "Continuar →",
                    use_container_width=True,
                    type="primary",
                ):

                    if not nome.strip():

                        st.error(
                            "Informe seu nome completo para continuar."
                        )

                        falar_orientacao(
                            "Por favor, informe seu nome completo antes de continuar."
                        )

                    else:

                        st.session_state.dados_paciente["nome"] = nome
                        st.session_state.dados_paciente["idade"] = idade
                        st.session_state.dados_paciente["queixa"] = queixa

                        st.session_state.etapa = 2
                        st.rerun()


    # ==========================================================================
    # ETAPA 2: AFERIÇÃO TÉRMICA
    # ==========================================================================

    elif st.session_state.etapa == 2:

        falar_orientacao(
            "Olhe para a câmera e posicione o seu rosto de forma centralizada."
        )

        # ----------------------------------------------------------------------
        # AFERIÇÃO
        # ----------------------------------------------------------------------

        with st.container(border=False):
            col_cam, col_info = st.columns([3, 2])

            with col_cam:

                st.image(
                    "http://localhost:8000/video_feed",
                    caption="Sensor de detecção térmica facial",
                    use_container_width=True,
                )

            with col_info:

                st.info(
                    "Mantenha-se posicionado em frente à câmera e "
                    "remova óculos ou chapéu."
                )

                if st.button(
                    "🔊 Repetir orientação",
                    use_container_width=True,
                ):
                    falar_orientacao(
                        "Olhe para a câmera e posicione o seu rosto de forma centralizada."
                    )

                temp_capturada = st.number_input(
                    "Temperatura registrada (°C)",
                    min_value=32.0,
                    max_value=42.0,
                    value=float(
                        st.session_state.dados_paciente["temperatura"]
                    ),
                    step=0.1,
                )


        # ----------------------------------------------------------------------
        # NAVEGAÇÃO
        # ----------------------------------------------------------------------

        with st.container(key="navegacao-totem"):

            c_back, c_next = st.columns([1, 2])

            with c_back:

                if st.button(
                    "← Identificação",
                    use_container_width=True,
                ):
                    st.session_state.etapa = 1
                    st.rerun()

            with c_next:

                if st.button(
                    "Confirmar e continuar →",
                    use_container_width=True,
                    type="primary",
                ):

                    st.session_state.dados_paciente["temperatura"] = (
                        temp_capturada
                    )

                    st.session_state.etapa = 3
                    st.rerun()


    # ==========================================================================
    # ETAPA 3: SINAIS VITAIS
    # ==========================================================================

    elif st.session_state.etapa == 3:

        falar_orientacao(
            "Apoie o seu dedo indicador no leitor de oxigenação "
            "e aguarde alguns segundos."
        )

        # --- CARREGAMENTO DO GIF LOCAL ---
        caminho_gif = os.path.join(
            "media", "finger_scan.gif"
        )  # Altere o nome do arquivo se necessário
        gif_base64 = get_image_base64(caminho_gif)

        # Injeta CSS e HTML para fixar o GIF no canto inferior direito
        if gif_base64:
            st.markdown(
                f"""
                <style>
                .gif-flutuante {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 200px;
                    background-color: #1a1c23;
                    border: 2px solid #0055ff;
                    border-radius: 12px;
                    padding: 10px;
                    box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
                    z-index: 99999;
                    text-align: center;
                }}
                .gif-flutuante img {{
                    width: 100%;
                    border-radius: 8px;
                    display: block;
                }}
                .gif-flutuante p {{
                    color: #ffffff;
                    font-size: 12px;
                    margin-top: 6px;
                    margin-bottom: 0px;
                    font-weight: bold;
                }}
                </style>

                <div class="gif-flutuante">
                    <img src="data:image/gif;base64,{gif_base64}" alt="Instrução Dedo">
                    <p>Apoie o dedo no leitor</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------------------------
        # SINAIS VITAIS
        # ----------------------------------------------------------------------

        with st.container(border=True):

            col_sinais, col_resumo = st.columns([3, 2])

            with col_sinais:

                st.markdown(
                    '<div class="form-titulo">Parâmetros dos sensores</div>',
                    unsafe_allow_html=True,
                )

                spo2 = st.slider(
                    "Saturação de oxigênio (SpO₂ %)",
                    70,
                    100,
                    int(
                        st.session_state.dados_paciente["spo2"]
                    ),
                )

                fc = st.slider(
                    "Frequência cardíaca (BPM)",
                    30,
                    200,
                    int(
                        st.session_state.dados_paciente[
                            "frequencia_cardiaca"
                        ]
                    ),
                )

                fr = st.slider(
                    "Frequência respiratória (RPM)",
                    10,
                    40,
                    int(
                        st.session_state.dados_paciente[
                            "frequencia_respiratoria"
                        ]
                    ),
                )

                dor = st.slider(
                    "Escala de dor (0 a 10)",
                    0,
                    10,
                    int(
                        st.session_state.dados_paciente["dor"]
                    ),
                )

            with col_resumo:

                st.markdown(
                    '<div class="form-titulo">Resumo do atendimento</div>',
                    unsafe_allow_html=True,
                )

                st.metric(
                    label="Paciente",
                    value=str(
                        st.session_state.dados_paciente["nome"]
                    ),
                )

                st.metric(
                    label="Temperatura corporal",
                    value=(
                        str(
                            st.session_state.dados_paciente[
                                "temperatura"
                            ]
                        )
                        + " °C"
                    ),
                )

                st.write(
                    "**Motivo da consulta:** "
                    + str(
                        st.session_state.dados_paciente["queixa"]
                    )
                )

                if "resultado_classificacao" in st.session_state:

                    st.success(
                        "Triagem registrada com sucesso!"
                    )

                    st.json(
                        st.session_state.resultado_classificacao
                    )


        # ----------------------------------------------------------------------
        # NAVEGAÇÃO
        # ----------------------------------------------------------------------

        with st.container(key="navegacao-totem"):

            c_back, c_next = st.columns([1, 2])

            with c_back:

                if "resultado_classificacao" not in st.session_state:

                    if st.button(
                        "← Temperatura",
                        use_container_width=True,
                    ):
                        st.session_state.etapa = 2
                        st.rerun()

                else:

                    if st.button(
                        "Voltar ao início",
                        use_container_width=True,
                    ):
                        st.session_state.etapa = 0
                        st.rerun()

            with c_next:

                if "resultado_classificacao" not in st.session_state:

                    if st.button(
                        "Concluir triagem →",
                        use_container_width=True,
                        type="primary",
                    ):

                        st.session_state.dados_paciente["spo2"] = spo2

                        st.session_state.dados_paciente[
                            "frequencia_cardiaca"
                        ] = fc

                        st.session_state.dados_paciente[
                            "frequencia_respiratoria"
                        ] = fr

                        st.session_state.dados_paciente["dor"] = dor

                        try:

                            res = requests.post(
                                "http://localhost:8000/triagem/classificar",
                                json=st.session_state.dados_paciente,
                            )

                            if res.status_code == 200:

                                st.session_state.resultado_classificacao = (
                                    res.json()
                                )

                                falar_orientacao(
                                    "Triagem concluída com sucesso. "
                                    "Aguarde a chamada no painel."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    "Erro na comunicação com o servidor de triagem."
                                )

                        except Exception:

                            st.warning(
                                "Servidor local indisponível. "
                                "Registro mantido em contingência."
                            )
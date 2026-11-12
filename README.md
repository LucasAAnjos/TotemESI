# Estação de Autoatendimento para Triagem Médica

Projeto de desenvolvimento de uma **estação de autoatendimento para triagem médica**, com o objetivo de auxiliar na coleta inicial de informações do paciente e na classificação de risco antes do atendimento por um profissional de saúde.

O sistema é dividido em dois componentes principais: uma **interface de atendimento**, responsável pela interação com o paciente e obtenção dos dados, e um **modelo de inteligência artificial**, responsável pela classificação do nível de risco com base nos sintomas informados.

## Pré-requisitos

* **Python 3.10.x** (Recomendado: **Python 3.10.11** ou superior da linha 3.10).

  > **Nota:** Recomenda-se evitar versões iniciais/instáveis do Python 3.10 (como 3.10.0 a 3.10.4) para evitar incompatibilidades conhecidas de compilação com pacotes como PyTorch, PyArrow/Streamlit e Uvicorn.

## Estrutura do Projeto

### `totem/`

Contém a interface web utilizada no totem de autoatendimento e os scripts de inicialização.

A aplicação é responsável por:

* Iniciar o atendimento do paciente;
* Realizar a coleta de informações;
* Apresentar perguntas e orientações ao paciente;
* Obter os sintomas relatados;
* Organizar os dados coletados para utilização pelo modelo de classificação;
* Apresentar os resultados e orientações do atendimento;
* `run.py`: Script para inicialização simultânea do backend (Uvicorn) e frontend (Streamlit).

### `modelo/`

Contém o modelo de **rede neural** desenvolvido para realizar a classificação de risco utilizando como referência a **Escala de Triagem de Emergência (ESI — Emergency Severity Index)**.

O modelo recebe como entrada os sintomas e demais informações obtenidas durante o atendimento e busca realizar a classificação correspondente ao nível de prioridade.

## Como Executar o Projeto

Siga os passos abaixo para configurar o ambiente de desenvolvimento e executar a aplicação.

### 1. Criar e Ativar o Ambiente Virtual (`env`)

Certifique-se de estar utilizando a versão correta do Python (3.10):

**No Linux/macOS:**

```bash
python3.10 -m venv env
source env/bin/activate
```

**No Windows (Command Prompt / PowerShell):**

```cmd
python -3.10 -m venv env
env\Scripts\activate
```

### 2. Instalar as Dependências

Com o ambiente virtual ativado, instale os pacotes listados no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Iniciar a Aplicação

Para subir simultaneamente o servidor backend (FastAPI/Uvicorn na porta 8000) e a interface frontend (Streamlit), utilize o script `run.py` localizado na pasta `totem/`.

A partir da raiz do projeto, execute:

```bash
python totem/run.py
```

*Ou, se preferir entrar na pasta primeiro:*

```bash
cd totem
python run.py
```

O script subirá ambos os serviços automaticamente. Para encerrar a execução de ambos os componentes ao mesmo tempo, basta pressionar `Ctrl + C` no terminal.

## Funcionamento Geral

O fluxo previsto para o sistema é:

1. O paciente inicia o atendimento no totem;
2. A interface realiza a coleta das informações necessárias;
3. Os sintomas e demais dados são organizados e enviados para o modelo;
4. A rede neural realiza a classificação de risco com base nos dados recebidos;
5. O resultado da classificação é apresentado para auxiliar no direcionamento do atendimento.

## Roadmap

* **Testes e validação do hardware:** Realizar a integração física com a Raspberry Pi 4 e os sensores MAX30102 e MLX90640, verificando a comunicação, estabilidade das leituras e confiabilidade dos sinais vitais obtidos. Também será necessário definir e testar uma solução adequada para a aquisição da pressão arterial por meio de manguito.
* **Finalização da interface e integração dos sensores:** Concluir as etapas restantes da interface de usuário, integrando a aquisição automática dos sinais vitais ao fluxo de atendimento. O objetivo é reduzir a necessidade de inserção manual de informações, centralizando a coleta, o processamento e o envio dos dados para o módulo de classificação.
* **Proposta de parceria com a UNESC para geração de um dataset nacional:** Estabelecer uma possível parceria com a Universidade do Extremo Sul Catarinense (UNESC), buscando viabilizar a construção de uma base de dados brasileira, com registros clínicos representativos da população nacional e maior coerência entre sinais vitais, queixas principais e classificações de urgência. Essa iniciativa poderá contribuir significativamente para o treinamento e a validação de modelos de classificação ESI mais consistentes e adequados à realidade dos serviços de saúde brasileiros, respeitando os requisitos éticos e de proteção dos dados dos pacientes.

## Estado Atual

O projeto encontra-se **em desenvolvimento**.

Tanto a interface do totem quanto o modelo de classificação ainda estão sendo desenvolvidos e podem sofrer alterações na estrutura, funcionalidades e integração entre os componentes.

## Objetivo

O objetivo do projeto é desenvolver uma solução integrada de autoatendimento capaz de realizar a **coleta inicial de dados e a classificação automatizada de risco**, buscando tornar o processo de triagem mais organizado e agilizar o direcionamento dos pacientes para o atendimento adequado.
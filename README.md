# Estação de Autoatendimento para Triagem Médica

Projeto de desenvolvimento de uma **estação de autoatendimento para triagem médica**, com o objetivo de auxiliar na coleta inicial de informações do paciente e na classificação de risco antes do atendimento por um profissional de saúde.

O sistema é dividido em dois componentes principais: uma **interface de atendimento**, responsável pela interação com o paciente e obtenção dos dados, e um **modelo de inteligência artificial**, responsável pela classificação do nível de risco com base nos sintomas informados.

## Estrutura do Projeto

### `totem/`

Contém a interface web utilizada no totem de autoatendimento.

A aplicação é responsável por:

* Iniciar o atendimento do paciente;
* Realizar a coleta de informações;
* Apresentar perguntas e orientações ao paciente;
* Obter os sintomas relatados;
* Organizar os dados coletados para utilização pelo modelo de classificação;
* Apresentar os resultados e orientações do atendimento.

### `modelo/`

Contém o modelo de **rede neural** desenvolvido para realizar a classificação de risco utilizando como referência a **Escala de Triagem de Emergência (ESI — Emergency Severity Index)**.

O modelo recebe como entrada os sintomas e demais informações obtidas durante o atendimento e busca realizar a classificação correspondente ao nível de prioridade.

## Funcionamento Geral

O fluxo previsto para o sistema é:

1. O paciente inicia o atendimento no totem;
2. A interface realiza a coleta das informações necessárias;
3. Os sintomas e demais dados são organizados e enviados para o modelo;
4. A rede neural realiza a classificação de risco com base nos dados recebidos;
5. O resultado da classificação é apresentado para auxiliar no direcionamento do atendimento.

## Estado Atual

O projeto encontra-se **em desenvolvimento**.

Tanto a interface do totem quanto o modelo de classificação ainda estão sendo desenvolvidos e podem sofrer alterações na estrutura, funcionalidades e integração entre os componentes.

## Objetivo

O objetivo do projeto é desenvolver uma solução integrada de autoatendimento capaz de realizar a **coleta inicial de dados e a classificação automatizada de risco**, buscando tornar o processo de triagem mais organizado e agilizar o direcionamento dos pacientes para o atendimento adequado.

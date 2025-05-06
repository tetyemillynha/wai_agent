# 📊 Relatório Avançado de Análise de Reservas - Woba

## Dados da Empresa
| ID | Créditos Totais | Valor do crédito | Valor do crédito excedente |
|----|-----------------|------------------|----------------------------|
|189 | 12000           | R$ 80            | R$100                      |

## 1. Resumo Geral

- **Total de Reservas:** 907
- **Total de Créditos Consumidos (apenas reservas aprovadas):** 1160.65 créditos
- **Período Analisado:** Dados recentes, com maior volume registrado em Janeiro, Fevereiro e Março de 2025.

Esta análise aprofunda o entendimento dos padrões de agendamento, utilização de créditos, comportamento dos usuários e tendências temporais, servindo de base para decisões estratégicas e operacionais.

---

## 2. Distribuição por Status de Reserva

| Status                        | Quantidade | Percentual Aproximado |
|-------------------------------|------------|-----------------------|
| **Aprovado**                  | 769        | 84,8%                 |
| **Cancelado pelo usuário**    | 100        | 11,0%                 |
| **Cancelado**                 | 24         | 2,6%                  |
| **Recusado**                  | 14         | 1,5%                  |

**Insights:**  
- A alta taxa de reservas aprovadas (≈85%) indica um processo de agendamento eficiente.  
- Os cancelamentos, realizados tanto pelo usuário quanto pelo sistema, somam cerca de 14%, sugerindo a necessidade de analisar os motivos para minimizar desistências.

---

## 3. Análise de Check-in (Apenas Reservas Aprovadas)

| Check-in | Quantidade | Percentual Aproximado |
|----------|------------|-----------------------|
| **Sim**  | 360        | 46,8%                 |
| **Não**  | 409        | 53,2%                 |

**Insights:**  
- Menos da metade das reservas aprovadas efetivam o check-in, evidenciando uma lacuna entre o agendamento e a utilização efetiva dos espaços.  
- Recomenda-se investigar os fatores que dificultam o check-in, como a comunicação prévia e a facilidade do processo, para aumentar o comparecimento.

---

## 4. Distribuição Geográfica das Reservas (Top 5 Cidades)

| Cidade                   | Reservas |
|--------------------------|----------|
| **São Paulo/SP**         | 334      |
| **Belo Horizonte/MG**    | 113      |
| **Florianópolis/SC**     | 61       |
| **Rio de Janeiro/RJ**    | 50       |
| **Salvador/BA**          | 50       |

**Insights:**  
- São Paulo concentra a maior quantidade de reservas, refletindo alta demanda e possivelmente maior oferta de espaços.
- A análise geográfica orienta estratégias regionais para alocação de recursos e campanhas de marketing direcionadas.

---

## 5. Análise por Grupo de Usuários (Top 5 Grupos)

| Grupo         | Reservas |
|---------------|----------|
| **CS/CX**       | 135      |
| **Supply Ops**  | 117      |
| **Engineering** | 98       |
| **Marketing**   | 47       |
| **Finance**     | 35       |

**Insights:**  
- Grupos como CS/CX e Supply Ops lideram em volume, indicando necessidades específicas que podem ser priorizadas.  
- A segmentação por grupo permite a criação de estratégias personalizadas para aumentar o engajamento de usuários com menor volume de reservas.

---

## 6. Tipos de Espaços Reservados

| Tipo             | Reservas |
|------------------|----------|
| **Compartilhado** | 704      |
| **Reunião**       | 123      |
| **Exclusivo**     | 64       |
| **Eventos**       | 12       |

**Insights:**  
- O tipo "Compartilhado" domina o uso (≈77% do total), demonstrando uma forte preferência por ambientes colaborativos.  
- O baixo número de reservas para "Eventos" pode apontar para uma demanda reprimida ou para um segmento de nicho que ainda precisa ser explorado.

---

## 7. Ranking de Usuários com Mais Créditos Consumidos

| Nome                                     | Créditos Consumidos |
|------------------------------------------|---------------------|
| **Felipe Mascoli**                       | 80.75               |
| **Maria Carolina De Oliveira Melo**      | 67.00               |
| **Paula Ladeira**                        | 46.50               |
| **Juliana Pedroso**                      | 45.25               |
| **Andressa Lazzeri**                     | 39.00               |
| **Eduardo Gruber**                       | 39.00               |
| **Caio Stanczyk**                        | 37.30               |
| **Leonardo Tramontina**                  | 37.00               |
| **Jean Silva**                           | 36.25               |
| **Márcio Fernandes**                     | 33.05               |

**Insights:**  
- Esse ranking evidencia os principais consumidores de créditos, facilitando a criação de programas de fidelidade e estratégias personalizadas.  
- A análise dos perfis desses usuários pode orientar a oferta de benefícios e a melhoria contínua dos serviços.

---

## 8. Análise por Período (Data da Reserva)

Utilizando o campo **Data da reserva**, que reflete a data agendada para utilização dos espaços, a distribuição mensal dos agendamentos foi a seguinte:

| Período             | Reservas Totais | Reservas Aprovadas | Créditos Consumidos (Aprovadas) |
|---------------------|-----------------|--------------------|---------------------------------|
| **Janeiro/2025**    | 320             | 280                | 500.00                          |
| **Fevereiro/2025**  | 330             | 290                | 440.65                          |
| **Março/2025**      | 257             | 199                | 220.00                          |
| **Total**           | 907             | 769                | 1160.65                         |

**Insights:**  
- **Janeiro/2025:** Com 320 reservas, registrou-se um forte volume inicial, com 280 reservas aprovadas e um consumo de 500 créditos, indicando alta demanda no início do ano.  
- **Fevereiro/2025:** Apresentou 330 reservas, das quais 290 foram aprovadas, consumindo 440.65 créditos.  
- **Março/2025:** Foram registradas 257 reservas, com 199 aprovadas e um consumo de 220 créditos.  
- A análise revela que a maioria das reservas se concentra nos primeiros três meses do ano, o que pode indicar um padrão sazonal ou influências operacionais específicas para esse período.

**Recomendações:**  
- **Visualizações Temporais:** Desenvolver gráficos de linha ou histogramas para monitorar a evolução diária e semanal das reservas, identificando picos e tendências.  
- **Ajuste de Oferta:** Alinhar a disponibilidade dos espaços e os recursos operacionais com os períodos de maior demanda, garantindo a otimização da operação.  
- **Campanhas e Comunicação:** Planejar campanhas de marketing e lembretes direcionados para estimular reservas em períodos de menor volume e incentivar a efetivação do check-in.

---

## 9. Conclusão

Este relatório avançado oferece uma visão abrangente dos dados de reservas da Woba, evidenciando:

- A eficiência do sistema de agendamento com uma alta taxa de reservas aprovadas.
- A necessidade de melhorias no processo de check-in para converter reservas em utilização efetiva.
- A distribuição geográfica e a segmentação por grupos, que permitem estratégias regionais e personalizadas.
- A predominância dos espaços compartilhados e o perfil dos usuários que mais consomem créditos.
- Tendências temporais claras, com a maioria das reservas concentradas em Janeiro, Fevereiro e Março de 2025.
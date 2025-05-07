const bookings = $input.first().json.bookings;

const groups = $input.first().json._embedded?.company_groups || [];

const pacotes = $input.first().json.packages || [];


const tiposProduto = {
  1: "Compartilhado",
  3: "Exclusivo",
  4: "Reunião",
  5: "Eventos",
  6: "Privativo",
};

const statusReserva = {
  0: "Aguardando revisão",
  1: "Aprovado",
  2: "Recusado",
  3: "Cancelado",
  4: "Cancelado pelo usuário",
  5: "Aguardando pagamento"
};

if (!bookings || bookings.length === 0) {
  return [{ json: { markdown: '# ❌ Nenhuma reserva encontrada.' } }];
}

// Mapas auxiliares
const porCidade = {};
const porEspaco = {};
const porGrupo = {};
const porUsuario = {};
const reservasPorTipo = {};
const reservasPorStatus = {};
let totalCreditos = 0;
let totalGasto = 0;
let checkinsFeitos = 0;
let checkinsNaoFeitos = 0;

// Map de ID de grupo → nome
const mapGrupos = {};
groups.forEach(g => {
  const ginfo = g.company_group;
  mapGrupos[ginfo.id] = {
    name: ginfo.name || 'Grupo sem nome',
    total_members: g.total_members || 0
  };
});

// Processar bookings
bookings.forEach(booking => {
  const cidade = booking.spaces?.cityname || 'Desconhecida';
  const espaco = booking.spaces?.name || 'Espaço desconhecido';
  const user = booking.users;
  const grupoId = booking.group_id;
  const grupo = mapGrupos[grupoId];

  totalCreditos += booking.credits || 0;
  totalGasto += booking.spentAmmount || 0;

  // Cidades
  porCidade[cidade] = (porCidade[cidade] || 0) + 1;

  // Espaços
  porEspaco[espaco] = porEspaco[espaco] || {
    count: 0,
    cm: booking.spaces?.cm_name,
    bairro: booking.spaces?.neighborhood,
    cidade
  };
  porEspaco[espaco].count++;

  // Grupos
  if (grupo) {
    porGrupo[grupo.name] = porGrupo[grupo.name] || { count: 0, members: grupo.total_members };
    porGrupo[grupo.name].count++;
  }

  // Usuários
  if (user?.first_name) {
    const nomeCompleto = `${user.first_name} ${user.last_name || ''}`.trim();
    porUsuario[nomeCompleto] = porUsuario[nomeCompleto] || {
      email: user.email || '',
      totalCreditos: 0
    };
    porUsuario[nomeCompleto].totalCreditos += booking.credits || 0;
  }

  if (booking.checkIn === true) checkinsFeitos++;
  else if (booking.checkIn === false) checkinsNaoFeitos++;

  // Tipo de produto
  const tipoProduto = tiposProduto[booking.type] || "Outro";
  reservasPorTipo[tipoProduto] = (reservasPorTipo[tipoProduto] || 0) + 1;

  // Status
const status = statusReserva[booking.status] || "-";
  reservasPorStatus[status] = (reservasPorStatus[status] || 0) + 1;
  
});

// Top 5 usuários
const topUsuarios = Object.entries(porUsuario)
  .sort((a, b) => b[1].totalCreditos - a[1].totalCreditos)
  .slice(0, 5);

// Montagem do markdown
let markdown = `# 📊 Relatório Analítico - Empresa ${bookings[0].companies?.id} -  ${bookings[0].companies?.name || 'Empresa Desconhecida'}\n\n`;

markdown += `## 🗓️ Período: ${bookings[0].booking_date?.split('T')[0] || 'Indefinido'} até ${bookings.at(-1).booking_date?.split('T')[0] || 'Indefinido'}\n\n`;

markdown += `### 🔢 Resumo Geral\n`;
markdown += `- Total de reservas: ${bookings.length}\n`;
markdown += `- Créditos consumidos: ${totalCreditos}\n`;
markdown += `- Valor gasto estimado: R$ ${(totalGasto / 100).toFixed(2)}\n`;
markdown += `- Cidades atendidas: ${Object.keys(porCidade).length}\n`;
markdown += `- Grupos identificados: ${Object.keys(porGrupo).length}\n\n`;

markdown += `---\n## 🏙️ Reservas por Cidade:\n`;
for (const [cidade, total] of Object.entries(porCidade)) {
  markdown += `- **${cidade}**: ${total} reservas\n`;
}

markdown += `\n## 🧑‍🤝‍🧑 Reservas por Grupo:\n`;
for (const [grupo, data] of Object.entries(porGrupo)) {
  markdown += `- **${grupo}**: ${data.count} reservas (${data.members} membros)\n`;
}

markdown += `\n## 👥 Top 5 Usuários por Créditos Consumidos:\n`;
topUsuarios.forEach(([nome, data], i) => {
  markdown += `${i + 1}. **${nome}** (${data.email}) – ${data.totalCreditos} créditos\n`;
});

markdown += `\n## 🏢 Espaços Utilizados:\n`;
for (const [espaco, data] of Object.entries(porEspaco)) {
  markdown += `- **${espaco}** (${data.cidade}, ${data.bairro}) – ${data.count} reservas`;
  if (data.cm) markdown += ` — CM: ${data.cm}`;
  markdown += '\n';
}

markdown += `\n---\n## 📌 Análise Consolidada das Reservas:\n`;

// Dias reservados
const porDia = {};
bookings.forEach(b => {
  const data = b.booking_date?.split('T')[0];
  if (data) porDia[data] = (porDia[data] || 0) + 1;
});

const porDiaSemana = {};
bookings.forEach(b => {
  const data = new Date(b.booking_date);
  const dia = data.toLocaleDateString('pt-BR', { weekday: 'long' });
  porDiaSemana[dia] = (porDiaSemana[dia] || 0) + 1;
});

markdown += `\n### 📅 Dias da Semana com Mais Reservas:\n`;
Object.entries(porDiaSemana)
  .sort((a, b) => b[1] - a[1])
  .forEach(([dia, total]) => {
    markdown += `- ${dia}: ${total} reservas\n`;
  });

markdown += `\n### ✅ Check-ins:\n`;
markdown += `- Realizados: ${checkinsFeitos}\n`;
markdown += `- Não realizados: ${checkinsNaoFeitos}\n`;

markdown += `\n### 📦 Reservas por Tipo de Produto:\n`;
for (const [tipo, total] of Object.entries(reservasPorTipo)) {
  markdown += `- ${tipo}: ${total} reservas\n`;
}

markdown += `\n### 📝 Reservas por Status:\n`;
for (const [status, total] of Object.entries(reservasPorStatus)) {
  markdown += `- ${status}: ${total} reservas\n`;
}

// Grupos (já tem em `porGrupo`)
markdown += `\n### 🧑‍🤝‍🧑 Créditos por Grupo:\n`;
for (const [grupo, data] of Object.entries(porGrupo)) {
  const totalCreditos = bookings
    .filter(b => mapGrupos[b.group_id]?.name === grupo)
    .reduce((sum, b) => sum + (b.credits || 0), 0);
  markdown += `- ${grupo}: ${data.count} reservas, ${totalCreditos} créditos\n`;
}

// Espaços (já tem `porEspaco`)
markdown += `\n### 🏢 Espaços Mais Reservados:\n`;
Object.entries(porEspaco)
  .sort((a, b) => b[1].count - a[1].count)
  .slice(0, 10)
  .forEach(([espaco, data]) => {
    const totalCreditos = bookings
      .filter(b => b.spaces?.name === espaco)
      .reduce((sum, b) => sum + (b.credits || 0), 0);
    markdown += `- ${espaco}: ${data.count} reservas, ${totalCreditos} créditos\n`;
  });

markdown += `## 🎯 Informações do Pacote Contratado\n\n`;

for (const pacote of pacotes) {
  const ciclo = pacote.activeCycle || {};
  const produtos = pacote.products?.join(', ') || '-';
  const bloqueados = pacote.blockedProducts?.length ? pacote.blockedProducts.join(', ') : '_nenhum_';
  const consumido = ciclo.creditAmountConsumed || 0;
  const total = ciclo.creditAmountTotal || 0;
  const disponivel = ciclo.availableCredits || 0;
  const excedentes = ciclo.exceededCredits || 0;

  markdown += `### Pacote #${pacote.id} (${pacote.duration})\n`;
  markdown += `- Vigência: ${new Date(pacote.startDate).toLocaleDateString('pt-BR')} até ${new Date(pacote.endDate).toLocaleDateString('pt-BR')}\n`;
  markdown += `- Produtos disponíveis: **${produtos}**\n`;
  markdown += `- Produtos bloqueados: **${bloqueados}**\n`;
  if (total > 0) {
    markdown += `- Créditos totais: ${total}\n`;
    markdown += `- Créditos consumidos: ${consumido}\n`;
    markdown += `- Créditos disponíveis: ${disponivel}\n`;
    markdown += `- Preço unitário: R$ ${(ciclo.creditUnitPrice || 0).toFixed(2)}\n`;
    markdown += `- Preço de crédito excedente: R$ ${(ciclo.creditExceededPrice || 0).toFixed(2)}\n`;
    markdown += `- Porcentagem consumida: ${(ciclo.consumeInPercentage || 0).toFixed(2)}%\n\n`;
  } else {
    markdown += `- Créditos excedentes utilizados: ${excedentes}\n`;
    markdown += `- Preço de crédito excedente: R$ ${(ciclo.creditExceededPrice || 0).toFixed(2)}\n`;
    markdown += `- Créditos disponíveis: ${disponivel}\n\n`;
  }
}

markdown += `---\n_Gerado automaticamente por WAi Facilities em ${new Date().toLocaleString('pt-BR')}_`;



return [{ json: { markdown } }];
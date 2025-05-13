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
  return [{ json: { error: "Nenhuma reserva encontrada" } }];
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
  if (!porEspaco[espaco]) {
    porEspaco[espaco] = {
      count: 0,
      cm: booking.spaces?.cm_name,
      bairro: booking.spaces?.neighborhood,
      cidade,
      creditos: 0
    };
  }
  porEspaco[espaco].count++;
  porEspaco[espaco].creditos += booking.credits || 0;

  // Grupos
  if (grupo) {
    if (!porGrupo[grupo.name]) {
      porGrupo[grupo.name] = { 
        count: 0, 
        members: grupo.total_members,
        creditos: 0
      };
    }
    porGrupo[grupo.name].count++;
    porGrupo[grupo.name].creditos += booking.credits || 0;
  }

  // Usuários
  if (user?.first_name) {
    const nomeCompleto = `${user.first_name} ${user.last_name || ''}`.trim();
    if (!porUsuario[nomeCompleto]) {
      porUsuario[nomeCompleto] = {
        email: user.email || '',
        totalCreditos: 0
      };
    }
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
  .slice(0, 5)
  .map(([nome, data]) => ({
    nome,
    email: data.email,
    creditos: data.totalCreditos
  }));

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

// Espaços mais reservados
const espacosMaisReservados = Object.entries(porEspaco)
  .sort((a, b) => b[1].count - a[1].count)
  .slice(0, 10)
  .map(([espaco, data]) => ({
    espaco,
    cidade: data.cidade,
    bairro: data.bairro,
    cm: data.cm,
    reservas: data.count,
    creditos: data.creditos
  }));

// Dias da semana ordenados
const diasSemanaOrdenados = Object.entries(porDiaSemana)
  .sort((a, b) => b[1] - a[1])
  .map(([dia, total]) => ({
    dia,
    reservas: total
  }));

// Processar pacotes
const pacotesFormatados = pacotes.map(pacote => {
  const ciclo = pacote.activeCycle || {};
  return {
    id: pacote.id,
    duracao: pacote.duration,
    vigencia: {
      inicio: pacote.startDate,
      fim: pacote.endDate
    },
    produtos: {
      disponiveis: pacote.products || [],
      bloqueados: pacote.blockedProducts || []
    },
    creditos: {
      totais: ciclo.creditAmountTotal || 0,
      consumidos: ciclo.creditAmountConsumed || 0,
      disponiveis: ciclo.availableCredits || 0,
      excedentes: ciclo.exceededCredits || 0
    },
    precos: {
      unitario: ciclo.creditUnitPrice || 0,
      excedente: ciclo.creditExceededPrice || 0
    },
    porcentagem_consumida: ciclo.consumeInPercentage || 0
  };
});

// Construir o objeto JSON final
const result = {
  empresa: {
    id: bookings[0].companies?.id,
    nome: bookings[0].companies?.name || 'Empresa Desconhecida'
  },
  periodo: {
    inicio: bookings.at(-1).booking_date?.split('T')[0] || 'Indefinido',
    fim: bookings[0].booking_date?.split('T')[0] || 'Indefinido'
  },
  resumo_geral: {
    total_reservas: bookings.length,
    creditos_consumidos: totalCreditos,
    valor_gasto: totalGasto / 100,
    cidades_atendidas: Object.keys(porCidade).length,
    grupos_identificados: Object.keys(porGrupo).length,
    checkins: {
      realizados: checkinsFeitos,
      nao_realizados: checkinsNaoFeitos
    }
  },
  por_cidade: Object.entries(porCidade).map(([cidade, total]) => ({
    cidade,
    reservas: total
  })),
  por_grupo: Object.entries(porGrupo).map(([grupo, data]) => ({
    grupo,
    reservas: data.count,
    membros: data.members,
    creditos: data.creditos
  })),
  top_usuarios: topUsuarios,
  espacos_utilizados: Object.entries(porEspaco).map(([espaco, data]) => ({
    espaco,
    cidade: data.cidade,
    bairro: data.bairro,
    cm: data.cm,
    reservas: data.count,
    creditos: data.creditos
  })),
  analise_consolidada: {
    dias_semana: diasSemanaOrdenados,
    por_tipo_produto: Object.entries(reservasPorTipo).map(([tipo, total]) => ({
      tipo,
      reservas: total
    })),
    por_status: Object.entries(reservasPorStatus).map(([status, total]) => ({
      status,
      reservas: total
    })),
    espacos_mais_reservados: espacosMaisReservados
  },
  pacotes: pacotesFormatados,
  gerado_em: new Date().toISOString()
};

return [{ json: result }];
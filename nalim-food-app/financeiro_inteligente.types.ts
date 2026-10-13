/**
 * NALIM FOOD SERVICE — MÓDULO FINANCEIRO INTELIGENTE
 * Tipagens TypeScript e Contratos de Dados do Cérebro Financeiro
 */

export type RoleUsuario = 'dono' | 'gerente' | 'operador';

export type CanalVenda = 'Salão' | 'Balcão' | 'iFood' | '99Food' | 'WhatsApp Próprio' | 'Delivery Próprio';

export type FormaPagamento = 'PIX' | 'Cartão Crédito' | 'Cartão Débito' | 'Dinheiro' | 'iFood Pay / Online';

export type MotivoPerda = 'validade' | 'erro_cozinha' | 'descarte' | 'avaria';

export type StatusBcg = 'campeoes' | 'populares' | 'oportunidades' | 'revisar_retirar';

/**
 * Registro de perda de insumos ou produtos finalizados
 */
export interface PerdaItem {
  id: number;
  tenant_id?: number;
  data: string; // YYYY-MM-DD
  item_nome: string;
  quantidade: number;
  custo_unitario: number;
  motivo: MotivoPerda;
  observacao?: string;
  custo_total?: number;
}

/**
 * Item vendido em um pedido
 */
export interface ItemPedidoVenda {
  produtoCodigo: string;
  nome: string;
  qtd: number;
  precoUnit: number;
  cmvUnit: number;
  modificacoes?: string;
}

/**
 * Pedido completo de venda
 */
export interface PedidoVenda {
  id: number;
  dataHora: string;
  dataIso: string; // YYYY-MM-DD
  identificacao: string;
  canal: CanalVenda | string;
  pagto: FormaPagamento | string;
  total: number;
  cmv: number;
  lucro: number;
  itens: string;
  itensDetalhados?: ItemPedidoVenda[];
}

/**
 * Termômetro Semanal de Rentabilidade: Métricas por dia da semana
 */
export interface TermometroDiaSemana {
  diaIndex: number; // 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
  diaNome: string; // 'Segunda-feira', 'Terça-feira', etc.
  diaSigla: string; // 'SEG', 'TER', 'QUA', etc.
  vezesAberto: number;
  faturamentoTotal: number;
  faturamentoMedio: number;
  cmvMedio: number;
  taxasMedias: number;
  custoFixoDiarioProporcional: number;
  custoOperacionalDiario: number;
  resultadoOperacionalDiario: number;
  margemOperacionalPct: number;
  status: 'lucro' | 'prejuizo' | 'fechado';
  alertaPrescritivo?: string;
}

/**
 * Desmembramento por Canal de Venda
 */
export interface DesmembramentoCanal {
  canal: string;
  pedidosCount: number;
  faturamentoBruto: number;
  taxasRetidas: number;
  taxaEfetivaPct: number;
  cmvTotal: number;
  lucroLiquido: number;
  margemLiquidaRealPct: number;
  ticketMedio: number;
}

/**
 * Previsão de Fluxo de Caixa a Curto Prazo (7 a 15 dias)
 */
export interface PrevisaoCaixaDia {
  dataIso: string;
  diaFormatado: string; // DD/MM
  diaSemana: string;
  entradasPrevistas: number;
  saidasPrevistas: number;
  saldoProjetado: number;
  alertaLiquidez: boolean;
  detalhesEntradas: string[];
  detalhesSaidas: string[];
}

/**
 * Recomendação Executiva do Cérebro Financeiro
 */
export interface DecisaoCerebro {
  id: string;
  categoria: 'meta' | 'preco' | 'dia_critico' | 'canais' | 'perdas';
  icone: string;
  titulo: string;
  diagnostico: string;
  acaoRecomendada: string;
  impactoEsperado: string;
  severidade: 'positivo' | 'alerta' | 'critico';
}

/**
 * Notificação por Exceção
 */
export interface NotificacaoExcecao {
  id: string;
  titulo: string;
  descricao: string;
  acaoRecomendada: string;
  tipo: 'alerta' | 'critico';
  regraDisparada: string;
}

/**
 * Item classificado na Matriz BCG
 */
export interface ItemBcg {
  codigo: string;
  nome: string;
  categoria: string;
  vendasQtd: number;
  faturamento: number;
  margemGerada: number;
  margemPct: number;
  quadrante: StatusBcg;
  recomendacaoAcao: string;
}
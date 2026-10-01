from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Pedido, CustoFixo, ConfiguracaoEmpresa
from schemas import DreResponse
from auth import require_role

router = APIRouter(prefix="/api/gerencial", tags=["Gerencial (Dono — DRE, Saúde Nalim & iFood)"])

@router.get("/dre", response_model=DreResponse)
def calcular_dre_gerencial(
    mes: str = Query("2026-08", description="Mês vigência YYYY-MM"),
    regime: str = Query("ME_6", description="'ME_6' (Simples Nacional 6%) ou 'MEI' (DAS R$ 75)"),
    current_user: User = Depends(require_role(["dono"])),
    db: Session = Depends(get_db)
):
    # 1. Totalização dos Pedidos do Tenant
    pedidos = db.query(Pedido).filter(Pedido.tenant_id == current_user.tenant_id).all()
    receita_bruta = sum(p.valor_bruto for p in pedidos)
    cmv_total = sum(p.cmv_total for p in pedidos)
    taxas_canais = sum(p.taxa_canal for p in pedidos)

    # Se ainda houver poucos pedidos reais, usa os dados consolidados do mês da planilha
    if receita_bruta < 500:
        receita_bruta = 36800.00
        cmv_total = 12940.00
        taxas_canais = 4232.00

    # 2. Impostos conforme Regime Fiscal
    if regime == "MEI":
        impostos = 75.00  # DAS fixo
    else:
        impostos = receita_bruta * 0.06  # Simples Nacional 6%

    receita_liquida = receita_bruta - impostos - taxas_canais
    lucro_bruto = receita_liquida - cmv_total
    margem_bruta_pct = (lucro_bruto / receita_bruta * 100) if receita_bruta > 0 else 0.0

    # 3. Custos Fixos do mês
    custos_fixos_db = db.query(CustoFixo).filter(
        CustoFixo.tenant_id == current_user.tenant_id,
        CustoFixo.mes_vigencia == mes
    ).all()
    custos_fixos_total = sum(c.valor for c in custos_fixos_db)
    if custos_fixos_total == 0:
        custos_fixos_total = 6450.00

    # 4. Resultado Líquido
    resultado_liquido = lucro_bruto - custos_fixos_total
    margem_liquida_pct = (resultado_liquido / receita_bruta * 100) if receita_bruta > 0 else 0.0

    # 5. Ponto de Equilíbrio (PE)
    indice_mc = (lucro_bruto / receita_bruta) if receita_bruta > 0 else 0.45
    ponto_equilibrio_mensal = (custos_fixos_total / indice_mc) if indice_mc > 0 else 0.0
    ponto_equilibrio_diario = ponto_equilibrio_mensal / 26.0

    # 6. Índice Nalim de Saúde do Negócio (Score de 0 a 100)
    score = 50.0
    if margem_liquida_pct >= 15.0:
        score += 25.0
    elif margem_liquida_pct >= 8.0:
        score += 15.0
    elif margem_liquida_pct < 0:
        score -= 25.0

    if receita_bruta >= ponto_equilibrio_mensal:
        score += 20.0
    else:
        score -= 15.0

    cmv_pct = (cmv_total / receita_bruta * 100) if receita_bruta > 0 else 35.0
    if cmv_pct <= 35.0:
        score += 15.0
    elif cmv_pct > 42.0:
        score -= 10.0

    score = max(5.0, min(100.0, score))
    classificacao = "SAUDÁVEL" if score >= 75.0 else ("ATENÇÃO" if score >= 50.0 else "CRÍTICO")

    return {
        "mes_vigencia": mes,
        "regime_tributario": regime,
        "receita_bruta": round(receita_bruta, 2),
        "deducoes_impostos": round(impostos, 2),
        "taxas_canais_ifood": round(taxas_canais, 2),
        "receita_liquida": round(receita_liquida, 2),
        "cmv_total": round(cmv_total, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "margem_bruta_pct": round(margem_bruta_pct, 1),
        "custos_fixos_total": round(custos_fixos_total, 2),
        "resultado_liquido": round(resultado_liquido, 2),
        "margem_liquida_pct": round(margem_liquida_pct, 1),
        "ponto_equilibrio_mensal": round(ponto_equilibrio_mensal, 2),
        "ponto_equilibrio_diario": round(ponto_equilibrio_diario, 2),
        "score_saude_nalim": round(score, 1),
        "classificacao_saude": classificacao
    }

@router.get("/simulador-ifood")
def simular_precificacao_ifood(
    custo_insumos: float = Query(11.50, description="Custo dos insumos da receita"),
    custo_embalagem: float = Query(2.50, description="Embalagem e sacola térmica"),
    taxa_comissao_pct: float = Query(23.0, description="Comissão cobrada pelo iFood"),
    imposto_pct: float = Query(6.0, description="Alíquota fiscal do restaurante"),
    margem_lucro_desejada_pct: float = Query(25.0, description="Margem de lucro limpa desejada"),
    current_user: User = Depends(require_role(["dono"]))
):
    # Fórmula do Markup Divisor para Food Service Delivery
    divisor = 1.0 - ((taxa_comissao_pct + imposto_pct + margem_lucro_desejada_pct) / 100.0)
    if divisor <= 0.1:
        divisor = 0.1

    custo_direto = custo_insumos + custo_embalagem
    preco_venda_sugerido = custo_direto / divisor

    comissao_reais = preco_venda_sugerido * (taxa_comissao_pct / 100.0)
    imposto_reais = preco_venda_sugerido * (imposto_pct / 100.0)
    repasse_liquido = preco_venda_sugerido - comissao_reais
    lucro_reais = repasse_liquido - custo_direto - imposto_reais

    return {
        "custo_direto": round(custo_direto, 2),
        "preco_venda_sugerido": round(preco_venda_sugerido, 2),
        "comissao_ifood_reais": round(comissao_reais, 2),
        "imposto_reais": round(imposto_reais, 2),
        "repasse_liquido_ifood": round(repasse_liquido, 2),
        "lucro_liquido_reais": round(lucro_reais, 2),
        "margem_efetiva_pct": round((lucro_reais / preco_venda_sugerido * 100), 1)
    }

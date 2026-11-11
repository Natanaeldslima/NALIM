# =====================================================================
# GERADOR DE APRESENTACAO POWERPOINT - NALIM FOOD SERVICE
# =====================================================================

$ppApp = New-Object -ComObject PowerPoint.Application
$ppApp.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

# Cria apresentacao
$pres = $ppApp.Presentations.Add([Microsoft.Office.Core.MsoTriState]::msoTrue)

# 16:9 Widescreen (960 x 540 pt)
$pres.PageSetup.SlideWidth = 960
$pres.PageSetup.SlideHeight = 540

function Get-RGB([int]$r, [int]$g, [int]$b) {
    return [int]($r + ($g * 256) + ($b * 65536))
}

$cDarkBg    = Get-RGB 15 23 42
$cLightBg   = Get-RGB 248 250 252
$cWhite     = Get-RGB 255 255 255
$cForest    = Get-RGB 5 150 105
$cDarkGreen = Get-RGB 6 78 59
$cAmber     = Get-RGB 217 119 6
$cRose      = Get-RGB 225 29 72
$cPurple    = Get-RGB 126 34 206
$cBorder    = Get-RGB 226 232 240
$cTextDark  = Get-RGB 15 23 42
$cTextGray  = Get-RGB 71 85 105
$cTextLight = Get-RGB 203 213 225

function Add-Header($slide, [string]$tag, [string]$titulo, [string]$subtitulo) {
    $boxTag = $slide.Shapes.AddTextbox(1, 50, 30, 860, 24)
    $boxTag.TextFrame.TextRange.Text = $tag.ToUpper()
    $boxTag.TextFrame.TextRange.Font.Name = "Segoe UI"
    $boxTag.TextFrame.TextRange.Font.Size = 10
    $boxTag.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $boxTag.TextFrame.TextRange.Font.Color.RGB = $cForest
    $boxTag.TextFrame.MarginLeft = 0; $boxTag.TextFrame.MarginTop = 0

    $boxTit = $slide.Shapes.AddTextbox(1, 50, 52, 860, 40)
    $boxTit.TextFrame.TextRange.Text = $titulo
    $boxTit.TextFrame.TextRange.Font.Name = "Segoe UI"
    $boxTit.TextFrame.TextRange.Font.Size = 22
    $boxTit.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $boxTit.TextFrame.TextRange.Font.Color.RGB = $cTextDark
    $boxTit.TextFrame.MarginLeft = 0; $boxTit.TextFrame.MarginTop = 0

    $boxSub = $slide.Shapes.AddTextbox(1, 50, 92, 860, 24)
    $boxSub.TextFrame.TextRange.Text = $subtitulo
    $boxSub.TextFrame.TextRange.Font.Name = "Segoe UI"
    $boxSub.TextFrame.TextRange.Font.Size = 12
    $boxSub.TextFrame.TextRange.Font.Color.RGB = $cTextGray
    $boxSub.TextFrame.MarginLeft = 0; $boxSub.TextFrame.MarginTop = 0
}

# =====================================================================
# SLIDE 1: CAPA EXECUTIVA
# =====================================================================
$s1 = $pres.Slides.Add(1, 12)
$bg1 = $s1.Shapes.AddShape(1, 0, 0, 960, 540)
$bg1.Fill.Solid()
$bg1.Fill.ForeColor.RGB = $cDarkBg
$bg1.Line.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse

$bTop = $s1.Shapes.AddShape(1, 50, 90, 280, 32)
$bTop.Fill.Solid(); $bTop.Fill.ForeColor.RGB = (Get-RGB 6 78 59)
$bTop.Line.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse
$bTop.TextFrame.TextRange.Text = "SISTEMA NALIM FOOD SERVICE 2026"
$bTop.TextFrame.TextRange.Font.Name = "Segoe UI"
$bTop.TextFrame.TextRange.Font.Size = 10
$bTop.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$bTop.TextFrame.TextRange.Font.Color.RGB = (Get-RGB 167 243 208)

$tit1 = $s1.Shapes.AddTextbox(1, 50, 140, 860, 130)
$tit1.TextFrame.TextRange.Text = "Gestao Operacional e Lucro Real`npara Restaurantes e Hamburguerias"
$tit1.TextFrame.TextRange.Font.Name = "Segoe UI"
$tit1.TextFrame.TextRange.Font.Size = 34
$tit1.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$tit1.TextFrame.TextRange.Font.Color.RGB = $cWhite

$slog1 = $s1.Shapes.AddTextbox(1, 50, 280, 820, 80)
$slog1.TextFrame.TextRange.Text = "Pare de apenas faturar alto e comece a ver o dinheiro sobrando no seu bolso:`ncontrole o salao, o KDS da cozinha e a previsao de caixa em uma unica plataforma integrada."
$slog1.TextFrame.TextRange.Font.Name = "Segoe UI"
$slog1.TextFrame.TextRange.Font.Size = 15
$slog1.TextFrame.TextRange.Font.Color.RGB = $cTextLight

$foot1 = $s1.Shapes.AddShape(1, 50, 420, 860, 60)
$foot1.Fill.Solid(); $foot1.Fill.ForeColor.RGB = (Get-RGB 30 41 59)
$foot1.Line.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse
$foot1.TextFrame.TextRange.Text = "[*] Garcom Mobile com Push no Bolso    [*] Cozinha KDS sem Papel    [*] CMV Automatico    [*] Previsao de Caixa 21 Dias"
$foot1.TextFrame.TextRange.Font.Name = "Segoe UI"
$foot1.TextFrame.TextRange.Font.Size = 12
$foot1.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$foot1.TextFrame.TextRange.Font.Color.RGB = (Get-RGB 52 211 153)

# =====================================================================
# SLIDE 2: AS 5 DORES DO DONO
# =====================================================================
$s2 = $pres.Slides.Add(2, 12)
Add-Header $s2 "Diagnostico de Mercado" "Onde o Dono de Restaurante Perde Dinheiro Todo Mes?" "A maioria dos empresarios do food service trabalha 14 horas por dia, mas enfrenta 5 armadilhas invisiveis:"

$dores = @(
    @("Ilusao do Faturamento", "Sabe quanto passou na maquina, mas nao sabe o Lucro Real apos descontar taxas do iFood (ate 27%) e taxas de cartao."),
    @("Surpresas nos Boletos", "Boletos de aluguel, energia e insumos vencem sem previsao clara de liquidez nos dias dos repasses semanais dos apps."),
    @("Gargalo Salao x Cozinha", "Comandas de papel perdidas, comida esfriando na chapa e garcons sem saber quando o pedido esta pronto."),
    @("Custo Alto de Hardware", "Sistemas legados exigem comprar maquininhas ou tablets caros (R$ 800+ cada) para cada garcom da equipe."),
    @("Desperdicio sem Controle", "Insumos nobres (carnes, queijos, bacon) sao descartados sem ficha tecnica e sem calculo do impacto no DRE.")
)

for ($i = 0; $i -lt 5; $i++) {
    $x = 50 + ($i * 174)
    $c = $s2.Shapes.AddShape(1, $x, 150, 164, 330)
    $c.Fill.Solid(); $c.Fill.ForeColor.RGB = $cWhite
    $c.Line.ForeColor.RGB = $cBorder; $c.Line.Weight = 1.5

    $txt = $c.TextFrame.TextRange
    $txt.Text = "$($i+1)`n`n$($dores[$i][0])`n`n$($dores[$i][1])"
    $txt.Font.Name = "Segoe UI"; $txt.Font.Size = 11; $txt.Font.Color.RGB = $cTextGray

    $c.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(1).Font.Size = 20
    $c.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cRose

    $c.TextFrame.TextRange.Paragraphs(3).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(3).Font.Size = 13
    $c.TextFrame.TextRange.Paragraphs(3).Font.Color.RGB = $cTextDark
}

# =====================================================================
# SLIDE 3: O ECOSSISTEMA NALIM (4 PILARES)
# =====================================================================
$s3 = $pres.Slides.Add(3, 12)
Add-Header $s3 "A Solucao Completa" "O Ecossistema Integrado NALIM Food Service" "Tudo o que seu restaurante precisa para operar com agilidade maxima e controle financeiro absoluto."

$pilares = @(
    @("PILAR 1", "Garcom Mobile Conectado", "Comanda digital no proprio celular do garcom. Recebe notificacao push no bolso mesmo com a tela bloqueada.", $cForest),
    @("PILAR 2", "Cozinha KDS Sem Papel", "Monitor interativo na chapa com tempos de preparo (Na Chapa -> Pronto). Dispara aviso sonoro imediato ao garcom.", $cAmber),
    @("PILAR 3", "CMV Real e Fichas Tecnicas", "Custo grama a grama de cada produto. Atualizacao automatica a cada venda realizada no balcao ou salao.", $cPurple),
    @("PILAR 4", "Previsao de Caixa 21 Dias", "Calendario financeiro que antecipa repasses do iFood (quartas) e provisiona boletos fixos nas datas de vencimento.", $cForest)
)

for ($i = 0; $i -lt 4; $i++) {
    $x = 50 + ($i * 218)
    $c = $s3.Shapes.AddShape(1, $x, 150, 206, 330)
    $c.Fill.Solid(); $c.Fill.ForeColor.RGB = $cWhite
    $c.Line.ForeColor.RGB = $cBorder; $c.Line.Weight = 2

    $txt = $c.TextFrame.TextRange
    $txt.Text = "$($pilares[$i][0])`n`n$($pilares[$i][1])`n`n$($pilares[$i][2])"
    $txt.Font.Name = "Segoe UI"; $txt.Font.Size = 12; $txt.Font.Color.RGB = $cTextGray

    $c.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(1).Font.Size = 11
    $c.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $pilares[$i][3]

    $c.TextFrame.TextRange.Paragraphs(3).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(3).Font.Size = 14
    $c.TextFrame.TextRange.Paragraphs(3).Font.Color.RGB = $cTextDark
}

# =====================================================================
# SLIDE 4: SAUDE FINANCEIRA & DRE
# =====================================================================
$s4 = $pres.Slides.Add(4, 12)
Add-Header $s4 "Visao de Lucro Real" "Saude Financeira: Saiba Exatamente Quanto Sobra no Bolso" "Enquanto os outros sistemas so mostram quanto vendeu, o NALIM calcula a sua margem liquida real a cada pedido."

$cDRE = $s4.Shapes.AddShape(1, 50, 150, 480, 330)
$cDRE.Fill.Solid(); $cDRE.Fill.ForeColor.RGB = $cWhite
$cDRE.Line.ForeColor.RGB = $cBorder; $cDRE.Line.Weight = 1.5
$tDRE = $cDRE.TextFrame.TextRange
$tDRE.Text = "Demonstrativo de Resultado (DRE) em Tempo Real`n`n" +
            "(+) Faturamento Bruto (Salao + Balcao + iFood)`n" +
            "(-) Taxas de Cartao e Comissoes dos Canais`n" +
            "(-) Custo de Mercadorias Vendidas (CMV dos Ingredientes)`n" +
            "(=) LUCRO BRUTO OPERACIONAL (Margem Real)`n`n" +
            "(-) Custos Fixos do Mes (Aluguel, Luz, Gas, Equipe, Pro-Labore)`n" +
            "(-) Perdas e Desperdicios Registrados na Cozinha`n`n" +
            "(=) LUCRO LIQUIDO REAL NO SEU BOLSO"
$tDRE.Font.Name = "Segoe UI"; $tDRE.Font.Size = 12; $tDRE.Font.Color.RGB = $cTextDark
$cDRE.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$cDRE.TextFrame.TextRange.Paragraphs(1).Font.Size = 13
$cDRE.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cForest

$cLat1 = $s4.Shapes.AddShape(1, 550, 150, 360, 155)
$cLat1.Fill.Solid(); $cLat1.Fill.ForeColor.RGB = (Get-RGB 236 253 245)
$cLat1.Line.ForeColor.RGB = (Get-RGB 167 243 208)
$tLat1 = $cLat1.TextFrame.TextRange
$tLat1.Text = "Ponto de Equilibrio (Break-Even Diario)`n`n" +
              "O sistema calcula automaticamente quantos hamburgueres ou quantos R$ por dia o restaurante precisa faturar apenas para pagar os custos fixos. Tudo o que vender acima disso e lucro puro."
$tLat1.Font.Name = "Segoe UI"; $tLat1.Font.Size = 11; $tLat1.Font.Color.RGB = $cDarkGreen
$cLat1.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue

$cLat2 = $s4.Shapes.AddShape(1, 550, 325, 360, 155)
$cLat2.Fill.Solid(); $cLat2.Fill.ForeColor.RGB = (Get-RGB 254 243 199)
$cLat2.Line.ForeColor.RGB = (Get-RGB 253 230 138)
$tLat2 = $cLat2.TextFrame.TextRange
$tLat2.Text = "Fechamento de Caixa com Conferencia Cega`n`n" +
              "O operador fecha o turno declarando os valores fisicos sem ver o total do sistema. O gerente faz o confronto cego de PIX, Cartao e Dinheiro, eliminando de vez furos e desvios de caixa."
$tLat2.Font.Name = "Segoe UI"; $tLat2.Font.Size = 11; $tLat2.Font.Color.RGB = (Get-RGB 120 53 15)
$cLat2.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue

# =====================================================================
# SLIDE 5: PREVISAO DE CAIXA DE 21 DIAS
# =====================================================================
$s5 = $pres.Slides.Add(5, 12)
Add-Header $s5 "Fluxo de Caixa Preditivo" "Previsao de Caixa de 21 Dias: Diga Adeus as Surpresas de Boletos" "Planejamento visual de liquidez: veja o saldo projetado de cada dia combinando entradas de apps e vencimentos."

$f1 = $s5.Shapes.AddShape(1, 50, 150, 270, 330)
$f1.Fill.Solid(); $f1.Fill.ForeColor.RGB = $cWhite; $f1.Line.ForeColor.RGB = $cBorder; $f1.Line.Weight = 1.5
$t1 = $f1.TextFrame.TextRange
$t1.Text = "Repasse Semanal dos Apps`n`n" +
           "O sistema sabe que toda quarta-feira entra o repasse acumulado das vendas do iFood e 99Food.`n`n" +
           "Essa entrada robusta e projetada automaticamente no calendario, mostrando exatamente quando o caixa da empresa ganha folego para honrar despesas."
$t1.Font.Name = "Segoe UI"; $t1.Font.Size = 12; $t1.Font.Color.RGB = $cTextGray
$f1.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$f1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14
$f1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cPurple

$f2 = $s5.Shapes.AddShape(1, 345, 150, 270, 330)
$f2.Fill.Solid(); $f2.Fill.ForeColor.RGB = $cWhite; $f2.Line.ForeColor.RGB = $cBorder; $f2.Line.Weight = 1.5
$t2 = $f2.TextFrame.TextRange
$t2.Text = "Boletos de Custos Fixos`n`n" +
           "Cadastre a data de vencimento de cada conta: Aluguel (dia 10), Energia (dia 12), Contabilidade (dia 15).`n`n" +
           "Os boletos entram automaticamente como saidas previstas na data exata, abatendo do saldo projetado sem precisar digitar duas vezes."
$t2.Font.Name = "Segoe UI"; $t2.Font.Size = 12; $t2.Font.Color.RGB = $cTextGray
$f2.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$f2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14
$f2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cForest

$f3 = $s5.Shapes.AddShape(1, 640, 150, 270, 330)
$f3.Fill.Solid(); $f3.Fill.ForeColor.RGB = $cWhite; $f3.Line.ForeColor.RGB = $cBorder; $f3.Line.Weight = 1.5
$t3 = $f3.TextFrame.TextRange
$t3.Text = "Alerta Previo de Liquidez`n`n" +
           "Se em algum dia das proximas 3 semanas a soma dos boletos superar as entradas, o sistema emite um Alerta de Liquidez em vermelho.`n`n" +
           "Voce descobre o deficit com dias de antecedencia para negociar prazos com fornecedores antes de pagar multas ou juros bancarios."
$t3.Font.Name = "Segoe UI"; $t3.Font.Size = 12; $t3.Font.Color.RGB = $cTextGray
$f3.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$f3.TextFrame.TextRange.Paragraphs(1).Font.Size = 14
$f3.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cRose

# =====================================================================
# SLIDE 6: AGILIDADE NO SALAO - GARCOM PUSH + KDS
# =====================================================================
$s6 = $pres.Slides.Add(6, 12)
Add-Header $s6 "Velocidade de Atendimento" "Salao e Cozinha 100% Sincronizados em Tempo Real" "Elimine pedidos esquecidos, gritaria na chapa e comida esfriando no balcao com tecnologia Web Push exclusiva."

$bGar = $s6.Shapes.AddShape(1, 50, 150, 420, 330)
$bGar.Fill.Solid(); $bGar.Fill.ForeColor.RGB = $cWhite; $bGar.Line.ForeColor.RGB = $cBorder; $bGar.Line.Weight = 1.5
$tGar = $bGar.TextFrame.TextRange
$tGar.Text = "Aplicativo do Garcom (Comanda Digital)`n`n" +
             "- Zero Gasto com Aparelhos: Funciona em qualquer smartphone Android que o garcom ja possui.`n`n" +
             "- Web Push Exclusivo: Quando a cozinha aperta Pronto, o celular do garcom toca e vibra no bolso mesmo com a tela apagada.`n`n" +
             "- Mapa de Mesas Vivo: Mostra na hora quais mesas estao livres, ocupadas ou com comida pronta esperando retirada.`n`n" +
             "- Adicionais e Observacoes: Personalize pratos (+ bacon, sem cebola) com dois toques."
$tGar.Font.Name = "Segoe UI"; $tGar.Font.Size = 12; $tGar.Font.Color.RGB = $cTextGray
$bGar.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$bGar.TextFrame.TextRange.Paragraphs(1).Font.Size = 14
$bGar.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cForest

$bKds = $s6.Shapes.AddShape(1, 490, 150, 420, 330)
$bKds.Fill.Solid(); $bKds.Fill.ForeColor.RGB = $cWhite; $bKds.Line.ForeColor.RGB = $cBorder; $bKds.Line.Weight = 1.5
$tKds = $bKds.TextFrame.TextRange
$tKds.Text = "KDS Cozinha Digital (Sem Papel)`n`n" +
             "- Adeus Comandas de Papel: Chega de papeis perdidos, molhados ou manchados de gordura na chapa.`n`n" +
             "- Fluxo Visual Rapido: Fases claras de preparo: Na Chapa -> Pronto -> Entregue.`n`n" +
             "- Controle de Tempo de Espera: Cronometro por pedido para garantir que nenhum cliente espere mais do que o combinado.`n`n" +
             "- 1 Toque Dispara o Alerta: O chapeiro clica em Pronto e o garcom responsavel ja recolhe na hora."
$tKds.Font.Name = "Segoe UI"; $tKds.Font.Size = 12; $tKds.Font.Color.RGB = $cTextGray
$bKds.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$bKds.TextFrame.TextRange.Paragraphs(1).Font.Size = 14
$bKds.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cAmber

# =====================================================================
# SLIDE 7: COMPARATIVO NALIM VS MERCADO
# =====================================================================
$s7 = $pres.Slides.Add(7, 12)
Add-Header $s7 "Diferencial Competitivo" "Por que o NALIM Supera os Sistemas Tradicionais?" "Compare os custos, a tecnologia e os recursos com softwares legados do mercado:"

$tab = $s7.Shapes.AddTable(6, 3, 50, 150, 860, 310)
$colWidths = @(340, 260, 260)
for ($col = 1; $col -le 3; $col++) { $tab.Table.Columns.Item($col).Width = $colWidths[$col-1] }

$headersTable = @("RECURSO / FUNCIONALIDADE", "SISTEMAS TRADICIONAIS", "NALIM FOOD SERVICE")
for ($c = 1; $c -le 3; $c++) {
    $cell = $tab.Table.Cell(1, $c).Shape.TextFrame.TextRange
    $cell.Text = $headersTable[$c-1]
    $cell.Font.Name = "Segoe UI"; $cell.Font.Size = 11; $cell.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $cell.Font.Color.RGB = $cWhite
    $tab.Table.Cell(1, $c).Shape.Fill.Solid()
    $tab.Table.Cell(1, $c).Shape.Fill.ForeColor.RGB = (Get-RGB 15 23 42)
}

$rows = @(
    @("Custo de Aparelhos (Hardware)", "Exige terminais/POS pagos (R$ 800+ cada)", "R$ 0 (Usa o celular comum da equipe)"),
    @("Push no Celular com Tela Apagada", "Nao possui (Apenas som com app aberto)", "Sim (Web Push VAPID com som e vibracao)"),
    @("Previsao de Caixa com Repasses Apps", "Cobrado a parte em modulos caros", "Incluso (Calendario 21 dias com iFood/99)"),
    @("CMV Real e Fichas Tecnicas", "Complexo ou inexistente na base", "Automatico e integrado a cada venda"),
    @("Comissao sobre Pedidos", "Cobram 1% a 3% do faturamento", "0% de comissao (Mensalidade 100% fixa)")
)

for ($r = 0; $r -lt 5; $r++) {
    for ($c = 1; $c -le 3; $c++) {
        $cell = $tab.Table.Cell($r+2, $c).Shape.TextFrame.TextRange
        $cell.Text = $rows[$r][$c-1]
        $cell.Font.Name = "Segoe UI"; $cell.Font.Size = 11
        if ($c -eq 3) {
            $cell.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
            $cell.Font.Color.RGB = $cForest
        } else {
            $cell.Font.Color.RGB = $cTextDark
        }
        $tab.Table.Cell($r+2, $c).Shape.Fill.Solid()
        if ($r % 2 -eq 0) {
            $tab.Table.Cell($r+2, $c).Shape.Fill.ForeColor.RGB = (Get-RGB 241 245 249)
        } else {
            $tab.Table.Cell($r+2, $c).Shape.Fill.ForeColor.RGB = $cWhite
        }
    }
}

# =====================================================================
# SLIDE 8: RETORNO SOBRE O INVESTIMENTO (ROI NA PRATICA)
# =====================================================================
$s8 = $pres.Slides.Add(8, 12)
Add-Header $s8 "Retorno Garantido" "Quanto Dinheiro o NALIM Devolve para o Restaurante?" "Exemplo pratico de uma hamburgueria que fatura R$ 45.000,00 por mes:"

$roiCards = @(
    @("Reducao de 3% no Desperdicio", "Fichas tecnicas precisas e registro de perdas evitam desperdicio de insumos nobres.", "+ R$ 1.350 /mes"),
    @("Migracao de 15% para Delivery Proprio", "Migrar clientes fieis do iFood para o cardapio proprio economiza taxas de comissao.", "+ R$ 1.080 /mes"),
    @("Economia de Hardware para 3 Garcons", "Sem necessidade de comprar maquininhas dedicadas de R$ 800 para cada operador.", "+ R$ 2.400 (imediato)"),
    @("Giro Rapido de Mesas no Salao", "Avisos instantaneos reduzem tempo ocioso das mesas e aumentam capacidade em 10%.", "+ R$ 2.200 /mes")
)

for ($i = 0; $i -lt 4; $i++) {
    $x = 50 + ($i * 218)
    $c = $s8.Shapes.AddShape(1, $x, 150, 206, 230)
    $c.Fill.Solid(); $c.Fill.ForeColor.RGB = $cWhite
    $c.Line.ForeColor.RGB = $cBorder; $c.Line.Weight = 1.5

    $txt = $c.TextFrame.TextRange
    $txt.Text = "$($roiCards[$i][0])`n`n$($roiCards[$i][1])`n`n$($roiCards[$i][2])"
    $txt.Font.Name = "Segoe UI"; $txt.Font.Size = 11; $txt.Font.Color.RGB = $cTextGray

    $c.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(1).Font.Size = 13
    $c.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cTextDark

    $c.TextFrame.TextRange.Paragraphs(5).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(5).Font.Size = 15
    $c.TextFrame.TextRange.Paragraphs(5).Font.Color.RGB = $cForest
}

$bRoi = $s8.Shapes.AddShape(1, 50, 400, 860, 80)
$bRoi.Fill.Solid(); $bRoi.Fill.ForeColor.RGB = (Get-RGB 6 78 59)
$bRoi.Line.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse
$tRoi = $bRoi.TextFrame.TextRange
$tRoi.Text = "RESULTADO LIQUIDO: O NALIM se paga nos primeiros 7 a 10 dias do mes!`nTodo o restante vira dinheiro no bolso do dono e tranquilidade na operacao."
$tRoi.Font.Name = "Segoe UI"; $tRoi.Font.Size = 14; $tRoi.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$tRoi.Font.Color.RGB = $cWhite

# =====================================================================
# SLIDE 9: PLANOS E PROPOSTA COMERCIAL
# =====================================================================
$s9 = $pres.Slides.Add(9, 12)
Add-Header $s9 "Investimento Previsivel" "Planos Flexiveis e Sem Contrato de Fidelidade Abusivo" "Escolha a modalidade que melhor atende o estagio atual da sua operacao:"

$planos = @(
    @("PLANO ESSENCIAL", "R$ 119", "/mes", "Para Dark Kitchens e Balcao`n`n- PDV Balcao e Caixa Cego`n- Cardapio Digital WhatsApp`n- Fechamento de Turnos`n- Relatorios Basicos", $cBorder, $cTextDark),
    @("PLANO PROFISSIONAL", "R$ 199", "/mes", "O Mais Vendido (Salao e Chapa)`n`n- Tudo do Essencial`n- Cozinha KDS em Tempo Real`n- App Garcom ilimitado com Push`n- Gestao de Mesas e Comandas", $cForest, $cForest),
    @("PLANO GESTAO TOTAL", "R$ 299", "/mes", "Controle Financeiro Rigoroso`n`n- Tudo do Profissional`n- CMV Real e Fichas Tecnicas`n- Previsao de Caixa 21 Dias`n- DRE e Ponto de Equilibrio", $cPurple, $cPurple)
)

for ($i = 0; $i -lt 3; $i++) {
    $x = 50 + ($i * 295)
    $c = $s9.Shapes.AddShape(1, $x, 150, 275, 330)
    $c.Fill.Solid(); $c.Fill.ForeColor.RGB = $cWhite
    $c.Line.ForeColor.RGB = $planos[$i][4]; $c.Line.Weight = 2

    $txt = $c.TextFrame.TextRange
    $txt.Text = "$($planos[$i][0])`n$($planos[$i][1])$($planos[$i][2])`n`n$($planos[$i][3])"
    $txt.Font.Name = "Segoe UI"; $txt.Font.Size = 11; $txt.Font.Color.RGB = $cTextGray

    $c.TextFrame.TextRange.Paragraphs(1).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(1).Font.Size = 12
    $c.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $planos[$i][5]

    $c.TextFrame.TextRange.Paragraphs(2).Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $c.TextFrame.TextRange.Paragraphs(2).Font.Size = 22
    $c.TextFrame.TextRange.Paragraphs(2).Font.Color.RGB = $cTextDark
}

# =====================================================================
# SLIDE 10: FECHAMENTO & PROXIMOS PASSOS (DARK)
# =====================================================================
$s10 = $pres.Slides.Add(10, 12)
$bg10 = $s10.Shapes.AddShape(1, 0, 0, 960, 540)
$bg10.Fill.Solid(); $bg10.Fill.ForeColor.RGB = $cDarkBg
$bg10.Line.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse

$tit10 = $s10.Shapes.AddTextbox(1, 50, 60, 860, 70)
$tit10.TextFrame.TextRange.Text = "Proximo Passo: Comece a Lucrar Mais Hoje"
$tit10.TextFrame.TextRange.Font.Name = "Segoe UI"
$tit10.TextFrame.TextRange.Font.Size = 28
$tit10.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$tit10.TextFrame.TextRange.Font.Color.RGB = $cWhite

$passos = @(
    @("1. Demonstracao Pratica de 10 Minutos", "Simulamos um pedido no salao e mostramos a cozinha e o celular apitando em tempo real."),
    @("2. Implantacao Assistida do seu Cardapio", "Cadastramos suas fotos, produtos e configuramos as fichas tecnicas com voce."),
    @("3. Treinamento da sua Equipe", "Em menos de 20 minutos seus garcons e chapeiros ja dominam 100% da operacao."),
    @("4. Clareza Financeira Imediata", "Acompanhe seu primeiro fechamento de caixa e veja sua previsao de liquidez de 21 dias.")
)

for ($i = 0; $i -lt 4; $i++) {
    $y = 150 + ($i * 70)
    $cardP = $s10.Shapes.AddShape(1, 50, $y, 860, 56)
    $cardP.Fill.Solid(); $cardP.Fill.ForeColor.RGB = (Get-RGB 30 41 59)
    $cardP.Line.ForeColor.RGB = (Get-RGB 51 65 85); $cardP.Line.Weight = 1
    
    $txtP = $cardP.TextFrame.TextRange
    $txtP.Text = "$($passos[$i][0])  -  $($passos[$i][1])"
    $txtP.Font.Name = "Segoe UI"; $txtP.Font.Size = 12; $txtP.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $txtP.Font.Color.RGB = (Get-RGB 241 245 249)
}

$btnFinal = $s10.Shapes.AddShape(1, 300, 450, 360, 50)
$btnFinal.Fill.Solid(); $btnFinal.Fill.ForeColor.RGB = $cForest
$btnFinal.Line.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse
$btnFinal.TextFrame.TextRange.Text = "AGENDAR DEMONSTRACAO AGORA"
$btnFinal.TextFrame.TextRange.Font.Name = "Segoe UI"
$btnFinal.TextFrame.TextRange.Font.Size = 13
$btnFinal.TextFrame.TextRange.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$btnFinal.TextFrame.TextRange.Font.Color.RGB = $cWhite

# Salva arquivo final
$caminhoPptx = "c:\Users\Natanael\.gemini\antigravity\conversations\nalim-food-app\Apresentacao_Comercial_NALIM.pptx"
$pres.SaveAs($caminhoPptx)
$pres.Close()
$ppApp.Quit()

Write-Output "PPTX_GERADO_COM_SUCESSO: $caminhoPptx"

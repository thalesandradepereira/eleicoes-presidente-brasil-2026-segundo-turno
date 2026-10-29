<div align="center">

# TAP · TSE 2026 — Auditoria Eleitoral

**Dashboard bilíngue e independente para examinar boletins de urna do segundo turno presidencial brasileiro de 2026.**

**PT-BR · EN-US** &nbsp; | &nbsp; **Made by TAP** &nbsp; | &nbsp; **Fonte: TSE**

</div>

---

## Visão geral

O projeto entrega um arquivo `index.html` autossuficiente, sem backend ou carregamento remoto de resultados eleitorais. A consulta pública permite verificar os votos por urna, município, zona e seção, além de visualizar mapas do Brasil e do exterior e a evolução por minuto de **encerramento da urna**.

> **Projeto independente, não oficial e sem vínculo institucional com o Tribunal Superior Eleitoral (TSE).** A fonte primária dos votos é o TSE; a interpretação dos dados, a visualização e o código do painel são responsabilidade deste projeto.

| Indicador auditado | Valor |
|---|---:|
| Registros de boletins agregados | **499.205** |
| Registros brasileiros | 497.897 |
| Registros do exterior (ZZ) | 1.308 |
| Países com boletins do exterior | 99 |
| Lula — votos nacionais | **64.256.232** |
| Flávio Bolsonaro — votos nacionais | **59.826.041** |
| Brancos — votos nacionais | 1.430.496 |
| Nulos — votos nacionais | 2.723.305 |

Os números acima são reproduzidos pelos testes da base embutida. O total de registros BWEB (499.205) difere em 43 do indicador de 499.248 seções do painel oficial do TSE. Esta diferença permanece documentada, **sem causa comprovada atribuída**. Os totais de votos, entretanto, coincidem com a totalização oficial.

## Experiência de consulta

| Recurso | Comportamento |
|---|---|
| Total nacional | Visualização inicial com Brasil e exterior, sem corte de horário |
| Filtros | País, UF, município, zona eleitoral, seção e identificação da urna |
| Mapa do Brasil | Resultados por UF; seleção interativa |
| Mapa-múndi | Dados do exterior associados às cidades de votação |
| Linha do tempo | Encerramentos de urnas brasileiras a partir de 17h00, em passos de 1 minuto (horário de Brasília) |
| Auditoria individual | Identificação e votos por urna, com paginação |
| Exportação | CSV integral correspondente ao filtro selecionado |
| Idiomas | Português (Brasil) e inglês (Estados Unidos) |
| Identidade | Made by TAP · Lula em vermelho · Flávio em azul |

### Precisão temporal

A linha do tempo usa o campo **`DT_ENCERRAMENTO`**, com conversão para Brasília no Brasil, e não o horário de transmissão, recebimento ou divulgação pelo TSE. O limite `17:15` corresponde a **17:15:00, inclusive**. Urnas com encerramento posterior não entram nesse recorte. Os boletins do exterior ficam fora dessa linha do tempo porque não houve conversão auditada de todos os fusos internacionais.

**Este gráfico não reconstitui o resultado que era público em cada minuto da apuração.** Mostra apenas o acumulado dos boletins cujo encerramento ocorreu até o horário selecionado.

## Fontes e proveniência

- **TSE — dados eleitorais:** [Resultados 2026 — Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna).
- **Geografia do Brasil:** [br-geojson](https://github.com/henriquemalvar/br-geojson).
- **Malha mundial:** [world.geo.json](https://github.com/johan/world.geo.json).
- **Associação auxiliar de localidades do exterior:** [consulta-boletins-urna](https://github.com/ricmazz/consulta-boletins-urna).

A análise original conferiu os **28 arquivos ZIP oficiais** por hash SHA-512 do TSE antes da consolidação. Este repositório não publica esses ZIPs: contém apenas o HTML resultante, a documentação e testes estáticos. O mapa mundial e a associação das cidades aos países são auxiliares cartográficos, não campos eleitorais certificados pelo TSE.

## Arquitetura e operação

```text
tap-tse-2026-auditoria/
├── index.html                  # Dashboard completo e offline
├── README.md                   # Metodologia, evidências e utilização
├── .nojekyll                   # Desativa transformação Jekyll
├── tests/
│   └── test_dashboard.py       # Integridade da base embutida
└── .github/workflows/
    └── pages.yml               # QA obrigatório → publicação
```

O HTML carrega registros compactados com gzip e codificados em base64, incorporados diretamente na página. Não há chamadas ao TSE durante a navegação. Alterações na base exigem regeneração controlada e nova auditoria; **não existe atualização em tempo real**.

### Testes locais

```sh
python3 -m unittest discover -s tests -v
```

Os testes verificam o arquivo completo, estrutura da base e geometrias, digest SHA-256 do payload incorporado, total por categoria, 270 conferências por UF (27 UFs × 5 indicadores × resultado integral e corte), quantidade de boletins do exterior e os quatro somatórios das urnas brasileiras encerradas até 17h15.

### Entrega e rollback

Cada alteração na branch `main` executa QA antes da implantação. O deploy ocorre somente quando a variável de repositório `ENABLE_GITHUB_PAGES=true` estiver habilitada, **e quando o plano da conta suportar Pages em repositório privado**. Como a tentativa em 29/10/2026 retornou HTTP 422 (plano sem suporte), a publicação está bloqueada, preservando a privacidade do repositório. Apenas um resultado de CI aprovado permite o deploy. O release traz a versão, a revisão e os resultados dos testes; o rollback consiste em restaurar um commit/tag anterior e executar novamente o workflow, respeitando o mesmo QA.

**Privacidade:** repositório privado, com site **público somente quando o plano GitHub permitir GitHub Pages em repositórios privados**. Os arquivos publicados pelo Pages são necessariamente acessíveis a quem visitar a página; privado não significa que o HTML implantado esteja oculto.

---

## English summary

Independent, bilingual (Portuguese BR / English US) **2026 Brazilian presidential runoff ballot audit** based on officially published TSE ballot-box records. Explore per-state maps, overseas country breakdowns, municipality/section drill-down, minute-by-minute **ballot closing** history, and filtered CSV exports.

**Important:** the timeline represents ballot closing times, **not** vote reporting/publication times. The overseas results are included in the final national totals but are excluded from Brazil’s minute-by-minute closing-time series. This project is **not affiliated with or endorsed by TSE**.

**Official electoral data:** https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna

---

<sub>Made by TAP · Auditoria reproduzível, transparência metodológica e controle de qualidade.</sub>

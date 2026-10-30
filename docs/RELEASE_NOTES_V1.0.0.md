# Made by TAP · Eleições Presidente Brasil 2026 — Segundo Turno · v1.0.0

**Publicação de produção — GitHub Pages com HTTPS**

**Abrir a página:** https://thalesandradepereira.github.io/eleicoes-presidente-brasil-2026-segundo-turno/

## Entrega
- Painel HTML único e independente de serviços externos para carregar dados.
- Mapa do Brasil (27 UFs), mapa-múndi (99 países), filtros e auditoria por seção/urna.
- Idiomas 🇧🇷 PT-BR e 🇺🇸 EN-US, branding Made by TAP, Lula vermelho e Flávio azul.
- Total nacional TSE e histórico por encerramento de urna brasileira a partir de 17h00, minuto a minuto.
- Exportação CSV e fontes no cabeçalho do painel.
- Favicon incorporado para eliminar requisições 404 na hospedagem estática.

## Evidências
- Testes `unittest`: 5 de 5 aprovados, incluindo 270 verificações estaduais.
- GitHub Actions com jobs de QA e deploy aprovados: [execução](https://github.com/thalesandradepereira/eleicoes-presidente-brasil-2026-segundo-turno/actions/runs/40978372418).
- URL HTTPS pública responde HTTP 200 e entrega HTML byte a byte idêntico ao `index.html`.
- Browser QA da página hospedada: total nacional, PT/EN, filtro França, cortes 17h15 e 17h16, mapas e mobile; sem erros JavaScript.

## Ressalvas
- Horário é `DT_ENCERRAMENTO` da urna, **não** momento de divulgação dos votos.
- Exterior incluído nos totais finais e excluído da linha do tempo por fuso não auditado.
- Diferença entre 499.205 registros BWEB e 499.248 seções totalizadas permanece declarada.
- Projeto independente, não afiliado ao TSE. Dados eleitorais extraídos do catálogo oficial.

**Fonte TSE:** https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna

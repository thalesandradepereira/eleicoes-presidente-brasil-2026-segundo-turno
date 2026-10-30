# QA da publicação — Eleições Presidente Brasil 2026, segundo turno

**Resultado: APROVADO — página pública operacional**

**URL:** https://thalesandradepereira.github.io/eleicoes-presidente-brasil-2026-segundo-turno/

**Fonte:** https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna

## Segurança e publicação

| Verificação | Evidência | Resultado |
|---|---|---|
| Visibilidade pública aprovada | Repositório público após auditoria do histórico | PASS |
| Segredos / credenciais | Dois commits originais e nove caminhos; sem chaves em texto aberto (alertas no Base64 de dados eram falsos positivos) | PASS |
| Dados oficiais | 28 ZIPs previamente validados por hash SHA-512, registros embutidos com SHA-256 | PASS |
| GitHub Actions | Execução [40978372418](https://github.com/thalesandradepereira/eleicoes-presidente-brasil-2026-segundo-turno/actions/runs/40978372418): QA e deploy concluídos com sucesso | PASS |
| Disponibilidade | Página hospedada respondeu HTTP 200, HTTPS/TLS sem erro | PASS |
| Correspondência de artefato | SHA-256 do HTML público idêntico ao arquivo `index.html` do repositório | PASS |
| Dependências | Sem scripts externos carregados em tempo de execução; um único HTML | PASS |
| Aviso institucional | Projeto independente, link oficial TSE e identidade Made by TAP | PASS |

## E2E na URL pública (navegador Chromium)

| Teste | Resultado |
|---|---|
| Total BWEB | 499.205 registros |
| Lula — total Brasil + exterior | 64.256.232 |
| Flávio Bolsonaro — total Brasil + exterior | 59.826.041 |
| Votos brancos e nulos | 1.430.496 e 2.723.305 |
| Mapa Brasil | 27 UFs |
| Mapa-múndi | 99 países com registros no exterior |
| Filtro França | 43 boletins, 11.275 votos Lula |
| Barra 17h15 | 488.813 urnas; 62.657.589 votos Lula; 58.545.934 votos Flávio |
| Barra 17h16 | 489.056 urnas |
| Idiomas | PT-BR e EN-US: alternância funcional |
| Layout móvel | viewport 390 px sem rolagem horizontal |
| JavaScript | Nenhum erro em console após favicon incorporado |

## Testes automatizados de base

`python3 -m unittest discover -s tests -v`: **5/5 aprovados**, incluindo 270 verificações de agregados estaduais em resultado integral e corte de 17h15. O histórico de implantação é rastreável no GitHub Actions.

## Limitações metodológicas

- Encerramento da urna **não** é recebimento ou divulgação da apuração.
- Exterior incluído no total, mas fora do histórico de encerramentos minuto a minuto.
- O número de registros BWEB (499.205) difere em 43 do contador de seções totalizadas do TSE (499.248); a causa não foi determinada.
- Países do exterior vêm de associação geográfica auxiliar. Os totais de votos têm como fonte exclusiva os boletins oficiais.
- A página é uma fotografia estática dos dados publicados, não uma conexão em tempo real.

## Manutenção e rollback

Para publicar mudanças: alterar código, executar testes, fazer revisão, aprovar CI e conferir URL HTTPS. Para rollback, restaurar um commit/tag previamente aprovado e reexecutar o workflow. Não publicar novas versões sem verificar tanto os cálculos quanto a resposta do site público.

**Made by TAP — painel independente, sem vínculo institucional com o TSE.**

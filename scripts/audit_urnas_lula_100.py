#!/usr/bin/env python3
"""Auditoria reprodutivel de 100% de votos validos para Lula; TSE 2026, 2T.

Fonte de microdados: dataset BWEB incorporado ao index.html publicado.
Aderencia: reconcilia contagens nacionais antes de selecionar registros.
A lista e exaustiva sobre 499.205 registros BWEB consolidados.
"""
from __future__ import annotations

import base64
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, LongTable, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
SOURCE = "https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna"
DASHBOARD = "https://thalesandradepereira.github.io/eleicoes-presidente-brasil-2026-segundo-turno/"
PDF = OUT / "Auditoria_TSE_2026_Urnas_100pct_Votos_Validos_Lula.pdf"
CSV = OUT / "Auditoria_TSE_2026_Urnas_100pct_Lula_Dados.csv"
SUMMARY = OUT / "Auditoria_TSE_2026_Urnas_100pct_Lula_Resumo.json"

def fmt(v):
    return f"{int(v):,}".replace(",", ".")

def source_records():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    match = re.search(r'<script id="dataset" type="application/octet-stream">([A-Za-z0-9+/=\s]+)</script>', html)
    if not match:
        raise RuntimeError("Dataset nao embutido em index.html")
    compressed = base64.b64decode("".join(match.group(1).split()), validate=True)
    p = html.index("const INFO=") + len("const INFO=")
    meta, _ = json.JSONDecoder().raw_decode(html[p:])
    expected_hash = meta["payload_sha256"]
    actual_hash = hashlib.sha256(compressed).hexdigest()
    if actual_hash != expected_hash:
        raise AssertionError("Falha de integridade SHA-256")
    raw = gzip.decompress(compressed).decode("ascii")
    cities = meta["cities"]
    totals = [0,0,0,0,0]
    allvalid = []
    ids = set()
    other_count = 0
    inconsistency = []
    for i,line in enumerate(raw.splitlines(), 1):
        values = [int(x) for x in line.split(",")]
        if len(values) != 11:
            raise AssertionError(f"Registro de formato invalido: {i}")
        cid, zone, sec, urna, sec_after17, lula, flavio, branco, nulo, comparecimento, offset = values
        city = cities[cid]
        uf, municipio, code = city[:3]
        for j,v in enumerate((lula,flavio,branco,nulo,1)):
            totals[j] += v
        key = (uf,code,zone,sec,urna)
        if key in ids:
            raise AssertionError(f"Chave de urna duplicada: {key}")
        ids.add(key)
        sum_cats=lula+flavio+branco+nulo
        if comparecimento != sum_cats:
            other_count += 1
        if lula>0 and flavio==0:
            strict=(branco==0 and nulo==0 and comparecimento==lula)
            row={
                "uf":uf, "municipio":municipio, "codigo_municipio":code,
                "zona":zone, "secao":sec, "numero_urna":urna,
                "lula":lula, "flavio_bolsonaro":flavio, "brancos":branco, "nulos":nulo,
                "comparecimento":comparecimento, "soma_categorias":sum_cats,
                "diferenca_comparecimento":comparecimento-sum_cats,
                "pct_validos_lula":100.0, "tambem_100pct_comparecimento":strict,
                "exterior_pais":city[3] if len(city)>3 else "",
            }
            allvalid.append(row)
            if sum_cats != comparecimento:
                inconsistency.append(row)
    if totals != meta["br_totals"]:
        raise AssertionError(f"Falha reconciliacao national: {totals} != {meta['br_totals']}")
    if len(ids)!=499205 or totals[:4] != [64256232,59826041,1430496,2723305]:
        raise AssertionError(f"Total base fora do esperado: {len(ids)} {totals}")
    allvalid.sort(key=lambda r:(r["uf"],r["municipio"],r["zona"],r["secao"],r["numero_urna"]))
    return allvalid,totals,other_count,inconsistency,actual_hash

def font_setup():
    regular=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("DVS", str(regular)))
        pdfmetrics.registerFont(TTFont("DVS-Bold", str(bold)))
        return "DVS","DVS-Bold"
    return "Helvetica","Helvetica-Bold"

def make_pdf(rows,totals,other_count,bad,sha):
    fr,fb=font_setup()
    navy=HexColor("#18354D"); muted=HexColor("#64778A"); red=HexColor("#BD3542"); blue=HexColor("#2664AA"); pale=HexColor("#EDF3F7")
    styles=getSampleStyleSheet()
    title=ParagraphStyle("t",parent=styles["Title"],fontName=fb,fontSize=19,leading=25,textColor=navy,spaceAfter=8,alignment=TA_LEFT)
    subtitle=ParagraphStyle("sub",parent=styles["Normal"],fontName=fr,fontSize=9,leading=14,textColor=muted,spaceAfter=12)
    h2=ParagraphStyle("h2",parent=styles["Heading2"],fontName=fb,fontSize=12,leading=17,textColor=navy,spaceBefore=12,spaceAfter=8)
    body=ParagraphStyle("body",parent=styles["Normal"],fontName=fr,fontSize=8,leading=12,textColor=navy,spaceAfter=6)
    small=ParagraphStyle("small",parent=body,fontSize=7,leading=10)
    cell=ParagraphStyle("cell",parent=body,fontSize=7,leading=9,spaceAfter=0)
    link=ParagraphStyle("url",parent=body,fontSize=8,leading=11,textColor=blue,wordWrap="CJK")
    page=landscape(A4)
    def footer(canvas,doc):
        canvas.saveState()
        w,h=page
        canvas.setStrokeColor(HexColor("#D8E1E8"));canvas.line(13*mm,12*mm,w-13*mm,12*mm)
        canvas.setFont(fr,7);canvas.setFillColor(muted)
        canvas.drawString(14*mm,8*mm,"TSE 2026 | 2º turno | Boletins por urna | Made by TAP")
        canvas.drawRightString(w-14*mm,8*mm,f"Página {doc.page}")
        canvas.restoreState()
    class Doc(BaseDocTemplate):
        pass
    doc=Doc(str(PDF),pagesize=page,leftMargin=13*mm,rightMargin=13*mm,topMargin=12*mm,bottomMargin=17*mm,
            title="Auditoria TSE 2026 | Urnas 100% dos votos validos Lula",author="Made by TAP")
    frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="frame",leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="normal",frames=[frame],onPage=footer))
    strict=[r for r in rows if r["tambem_100pct_comparecimento"]]
    other=[r for r in rows if not r["tambem_100pct_comparecimento"]]
    byuf=defaultdict(list)
    for r in rows:byuf[r["uf"]].append(r)
    totalv=sum(r["lula"] for r in rows)
    nonzero_blank=sum(1 for r in rows if r["brancos"]>0)
    nonzero_null=sum(1 for r in rows if r["nulos"]>0)
    unique_cities=len({(r["uf"],r["codigo_municipio"]) for r in rows})
    story=[
      Paragraph("AUDITORIA DOS BOLETINS DE URNA",title),
      Paragraph("Presidente do Brasil — 2º turno, 25/10/2026 | Casos em que Lula recebeu 100% dos <b>votos válidos</b> da urna",subtitle),
    ]
    stats=[
      ["URNA(S) EM 100% DOS VÁLIDOS", "100% DE TODOS OS VOTOS", "VOTOS PARA LULA NOS CASOS", "MUNICÍPIOS / LOCALIDADES"],
      [fmt(len(rows)),fmt(len(strict)),fmt(totalv),fmt(unique_cities)]
    ]
    stat=Table(stats,colWidths=[49*mm,49*mm,49*mm,54*mm],hAlign="LEFT",rowHeights=[12*mm,16*mm])
    stat.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),pale),("FONTNAME",(0,0),(-1,0),fb),("FONTNAME",(0,1),(-1,1),fb),
                               ("FONTSIZE",(0,0),(-1,0),7),("FONTSIZE",(0,1),(-1,1),15),
                               ("TEXTCOLOR",(0,0),(-1,0),muted),("TEXTCOLOR",(0,1),(-1,1),navy),
                               ("LEFTPADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                               ("LINEBELOW",(0,-1),(-1,-1),.5,HexColor("#B4C4D0"))]))
    story += [stat,Spacer(1,6*mm),Paragraph("CRITÉRIOS DE CLASSIFICAÇÃO",h2),
      Paragraph("<b>100% dos votos válidos:</b> Lula &gt; 0 e Flávio Bolsonaro = 0. Votos em branco e nulos podem existir e são apresentados em colunas próprias.",body),
      Paragraph("<b>100% de todos os votos registrados:</b> Lula &gt; 0, Flávio = 0, brancos = 0, nulos = 0 e o número de votos de Lula corresponde ao comparecimento informado no BWEB. É um subconjunto do critério anterior.",body),
      Paragraph(f"Dos {fmt(len(rows))} registros com 100% dos votos válidos, {fmt(len(strict))} satisfazem o critério estrito e {fmt(len(other))} não. Há {fmt(nonzero_blank)} com pelo menos um branco, {fmt(nonzero_null)} com pelo menos um nulo e {fmt(len(bad))} com divergência entre comparecimento e soma das quatro categorias.",body),
      Paragraph("<b>Atenção:</b> 100% dos votos válidos numa seção não é, por si só, indício de irregularidade. As quantidades de eleitores e o contexto local importam. Este documento é uma filtragem descritiva de boletins públicos, sem inferência de fraude ou intenção de voto.",body),
      Paragraph("ESCOPO E CONTROLE DE QUALIDADE",h2),
      Paragraph(f"Base examinada: <b>{fmt(totals[4])} registros de boletim</b> de 27 UFs + exterior (ZZ), 28 arquivos ZIP oficiais previamente validados por SHA-512 e base embutida conferida por SHA-256 (<font size='7'>{sha[:22]}...</font>). Totais nacionais de Lula, Flávio, brancos e nulos reconciliados com a fonte.",body),
      Paragraph("Fonte oficial: <link href='"+SOURCE+"' color='#2664AA'>"+SOURCE+"</link>",link),
      Paragraph("Dashboard de dados incorporados: <link href='"+DASHBOARD+"' color='#2664AA'>"+DASHBOARD+"</link>",link),
      Spacer(1,5*mm),Paragraph("DISTRIBUIÇÃO DAS URNAS POR UF",h2)]
    state_data=[[Paragraph("UF",cell),Paragraph("Urnas 100% válidos",cell),Paragraph("100% de todos os votos",cell),Paragraph("Votos Lula",cell)]]
    for uf in sorted(byuf):
      vals=byuf[uf]
      state_data.append([uf,fmt(len(vals)),fmt(sum(r["tambem_100pct_comparecimento"] for r in vals)),fmt(sum(r["lula"] for r in vals))])
    t=Table(state_data,colWidths=[27*mm,46*mm,53*mm,54*mm],repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                           ("FONTNAME",(0,0),(-1,-1),fr),("FONTSIZE",(0,0),(-1,-1),7),
                           ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,HexColor("#F1F5F8")]),
                           ("BOTTOMPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5)]))
    story.append(t)
    story.append(PageBreak())
    story.extend([Paragraph("LISTA COMPLETA — TODOS OS CASOS",title),
      Paragraph("Ordenação: UF, cidade, zona, seção e número da urna. Uma linha por boletim/urna. Flávio Bolsonaro aparece explicitamente com zero nos casos selecionados.",subtitle)])
    hdr=["UF","Cidade / localidade","Zona","Seção","Nº urna","Lula","Flávio","Brancos","Nulos","Comp.","100% total?"]
    widths=[14*mm,73*mm,17*mm,19*mm,25*mm,18*mm,18*mm,18*mm,18*mm,18*mm,21*mm]
    data=[[Paragraph(h,ParagraphStyle("head"+str(i),parent=cell,fontName=fb,textColor=colors.white,fontSize=6.5,leading=8)) for i,h in enumerate(hdr)]]
    for r in rows:
      c = r["municipio"]+((" · "+r["exterior_pais"]) if r["exterior_pais"] else "")
      data.append([r["uf"],Paragraph(c,cell),str(r["zona"]),str(r["secao"]),str(r["numero_urna"]),fmt(r["lula"]),
                   str(r["flavio_bolsonaro"]),str(r["brancos"]),str(r["nulos"]),fmt(r["comparecimento"]),
                   "SIM" if r["tambem_100pct_comparecimento"] else "NÃO"])
    tb=LongTable(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
    tb.setStyle(TableStyle([
      ("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),
      ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,HexColor("#F0F4F7")]),
      ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("FONTSIZE",(0,1),(-1,-1),6.6),
      ("FONTNAME",(0,1),(-1,-1),fr),("ALIGN",(2,1),(-1,-1),"CENTER"),
      ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
      ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
      ("LINEBELOW",(0,0),(-1,0),.4,HexColor("#C7D3DA")),
    ]))
    story.append(tb)
    story.extend([Spacer(1,6*mm),Paragraph("NOTAS DE LEITURA",h2),
      Paragraph("A designação "100% total?" significa ausência de votos adversários, brancos e nulos, e reconciliação entre voto nominal e comparecimento. A coluna "Comp." transcreve o campo de comparecimento informado pelo TSE.",body),
      Paragraph("Eventuais divergências de comparecimento devem ser investigadas no boletim original antes de qualquer conclusão. Este documento não substitui a conferência do BU original.",body)])
    doc.build(story)

def write_outputs(rows,totals,other_count,bad,sha):
    columns=["uf","municipio","codigo_municipio","zona","secao","numero_urna","lula","flavio_bolsonaro",
             "brancos","nulos","comparecimento","soma_categorias","diferenca_comparecimento",
             "pct_validos_lula","tambem_100pct_comparecimento","exterior_pais"]
    with CSV.open("w",encoding="utf-8-sig",newline="") as f:
      w=csv.DictWriter(f,fieldnames=columns,delimiter=";")
      w.writeheader();w.writerows(rows)
    uf=Counter(r["uf"] for r in rows)
    strict=[r for r in rows if r["tambem_100pct_comparecimento"]]
    summary={
      "periodo":"2026-10-25_2turno","fonte":SOURCE,"base_registros":totals[4],
      "base_totais":{"lula":totals[0],"flavio":totals[1],"brancos":totals[2],"nulos":totals[3]},
      "urna_100pct_votos_validos_lula":len(rows),
      "urna_100pct_total_comparecimento_lula":len(strict),
      "urnas_com_brancos":sum(r["brancos"]>0 for r in rows),
      "urnas_com_nulos":sum(r["nulos"]>0 for r in rows),
      "urnas_com_comparecimento_inconciliavel":len(bad),
      "lula_votos_nessas_urnas":sum(r["lula"] for r in rows),
      "unidades_federativas_com_ocorrencia":dict(sorted(uf.items())),
      "municipios_ou_localidades":len({(r["uf"],r["codigo_municipio"]) for r in rows}),
      "verificacao_sha256":sha,
      "maior_lula_urna":max((r["lula"] for r in rows),default=0),
      "arquivos":{"pdf":PDF.name,"csv":CSV.name},
    }
    SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SUMMARY_JSON="+json.dumps(summary,ensure_ascii=False,separators=(",",":")),flush=True)
    print("RESULT_PDF="+str(PDF)+" "+str(PDF.stat().st_size),flush=True)
    print("RESULT_CSV="+str(CSV)+" "+str(CSV.stat().st_size),flush=True)

if __name__=="__main__":
    rows,totals,other_count,bad,sha=source_records()
    make_pdf(rows,totals,other_count,bad,sha)
    write_outputs(rows,totals,other_count,bad,sha)

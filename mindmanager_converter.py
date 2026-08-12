"""MindManager HTML -> Mermaid & Markdown converter (v5).

Converts MindManager HTML export to:
  - Mermaid flowchart (.md)
  - Markdown outline (.md)
Uses explicit relationship edges from the mind map XML.
"""

import re, base64, zipfile, io
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


AP = "http://schemas.mindjet.com/MindManager/Application/2003"

PHASE_ORDER = [
    "Inicio",
    "1. Investigacion",
    "Decision - Entrevistas",
    "2. Descubrimiento",
    "Persona y Problem-Solution Fit",
    "3. Ideacion",
    "4. Prototipado y Validacion",
]

# Keys use text AFTER normalization (collapsed spaces, no \n)
NODE_PHASE = {
    "C\u00f3mo quieres iniciar?": "Inicio",

    "Agente Benchmark": "1. Investigacion",
    "Agente Foresight": "1. Investigacion",
    "Agente Se\u00f1ales d\u00e9biles": "1. Investigacion",
    "Agente Discussion Forums": "1. Investigacion",
    "Agente Search Trend Analysis": "1. Investigacion",

    "Agente Entrevista de empat\u00eda": "Decision - Entrevistas",
    "\u00bfEjecuci\u00f3n de entrevistas?": "Decision - Entrevistas",
    "Simular o no": "Decision - Entrevistas",
    "Selecci\u00f3n de agentes": "Decision - Entrevistas",

    "Agente A Day In The Life": "2. Descubrimiento",
    "Agente Expo Quest": "2. Descubrimiento",
    "Agente Encuesta Kano": "2. Descubrimiento",
    "Agente Discovery Survey": "2. Descubrimiento",

    "Agente Persona Profile": "Persona y Problem-Solution Fit",
    "\u00bfHay datos reales de entrevistas / encuestas?": "Persona y Problem-Solution Fit",
    "Agente Problem Solution Fit": "Persona y Problem-Solution Fit",
    "Elecci\u00f3n de protopersona": "Persona y Problem-Solution Fit",
    "Agente Journey Builder": "Persona y Problem-Solution Fit",
    "Agente HMW": "Persona y Problem-Solution Fit",
    "Ambici\u00f3n estrat\u00e9gica": "Persona y Problem-Solution Fit",
    "Apalancamiento": "Persona y Problem-Solution Fit",

    "Selecci\u00f3n de agentes de ideaci\u00f3n": "3. Ideacion",
    "Agente Ideaci\u00f3n": "3. Ideacion",
    "Agente Caressing the client": "3. Ideacion",
    "Agente Referral Builder": "3. Ideacion",
    "Agente Dimensionador Estrat\u00e9gico de Ideas de Negocio": "3. Ideacion",
    "Agente Business Model Navigator": "3. Ideacion",

    "Selecci\u00f3n de agente para validar": "4. Prototipado y Validacion",
    "Agente Simple Landing Page": "4. Prototipado y Validacion",
    "Agente Landing Page UX Analyzer": "4. Prototipado y Validacion",
    "Agente Online Ads": "4. Prototipado y Validacion",
    "Agente Email Campaign": "4. Prototipado y Validacion",
    "Agente Explainer Video": "4. Prototipado y Validacion",
    "Agente Pop-Up Store": "4. Prototipado y Validacion",
    "Agente Feature Stub": "4. Prototipado y Validacion",
}


def _normalize(text: str) -> str:
    """Normalize: replace newlines, collapse whitespace, strip."""
    text = text.replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", text).strip()


def _extract_xml(html_path: str) -> str:
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'<script\s+id="mmap"[^>]*>([^<]+)</script>', content)
    if not match:
        raise ValueError("Could not find <script id='mmap'>")
    zip_bytes = base64.b64decode(match.group(1).strip())
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        return zf.read("Document.xml").decode("utf-8")


def _parse_mindmap(xml_content: str) -> dict:
    root = ET.fromstring(xml_content)

    oid_to_topic = {}
    for t in root.iter(f"{{{AP}}}Topic"):
        oid = t.get("OId", "")
        text_el = t.find(f"{{{AP}}}Text")
        if text_el is None:
            continue
        text = text_el.get("PlainText", "")
        if not text or not text.strip():
            continue

        text = _normalize(text)
        notes_el = t.find(f"{{{AP}}}NotesGroup/{{{AP}}}NotesXhtmlData")
        has_notes = notes_el is not None
        notes = notes_el.get("PreviewPlainText", "") if has_notes else ""

        oid_to_topic[oid] = {
            "text": text,
            "has_notes": has_notes,
            "notes": notes,
        }

    edges = []
    seen_pairs = set()

    for rel in root.iter(f"{{{AP}}}Relationship"):
        cgs = rel.findall(f"{{{AP}}}ConnectionGroup")
        refs = []
        for cg in cgs:
            conn = cg.find(f"{{{AP}}}Connection")
            if conn is not None:
                ref = conn.find(f"{{{AP}}}ObjectReference")
                if ref is not None:
                    oid_ref = ref.get("OIdRef", "")
                    if oid_ref in oid_to_topic:
                        refs.append(oid_ref)
        if len(refs) >= 2:
            pair = (refs[0], refs[1])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                edges.append({
                    "src_oid": refs[0],
                    "dst_oid": refs[1],
                    "src_text": oid_to_topic[refs[0]]["text"],
                    "dst_text": oid_to_topic[refs[1]]["text"],
                })

    return {"topics": oid_to_topic, "edges": edges}


def _is_agent(text: str) -> bool:
    return text.startswith("Agente")


def _mermaid_label(text: str, is_agent: bool) -> str:
    """Build mermaid node label: agent -> [text], decision -> {text}."""
    clean = text.replace('"', "'")
    if is_agent:
        return f'["{clean}"]'
    else:
        return f'{{"{clean}"}}'


def generate_mermaid(parsed: dict) -> str:
    topics = parsed["topics"]
    edges = parsed["edges"]

    lines = ["graph TD"]

    phase_nodes = defaultdict(list)
    node_id_map = {}
    connected_texts = set()
    for e in edges:
        connected_texts.add(e["src_text"])
        connected_texts.add(e["dst_text"])

    node_counter = 0
    for text in sorted(connected_texts):
        node_id = f"N{node_counter}"
        node_counter += 1
        node_id_map[text] = node_id
        phase = NODE_PHASE.get(text, "Otros")
        phase_nodes[phase].append((node_id, text))

    for phase_name in PHASE_ORDER:
        nodes = phase_nodes.get(phase_name, [])
        if not nodes:
            continue
        safe_phase = re.sub(r"[^a-zA-Z0-9]", "_", phase_name).strip("_")
        lines.append(f"    subgraph {safe_phase}[{phase_name}]")
        for node_id, text in nodes:
            agent = _is_agent(text)
            label = _mermaid_label(text, agent)
            lines.append(f"        {node_id}{label}")
        lines.append("    end")

    lines.append("")

    seen_id_pairs = set()
    for e in edges:
        src_id = node_id_map.get(e["src_text"])
        dst_id = node_id_map.get(e["dst_text"])
        if src_id and dst_id:
            pair = (src_id, dst_id)
            if pair not in seen_id_pairs:
                seen_id_pairs.add(pair)
                lines.append(f"    {src_id} --> {dst_id}")

    # No markdown fences — output is raw Mermaid for CLI / API consumers
    return "\n".join(lines)


def generate_markdown(parsed: dict) -> str:
    topics = parsed["topics"]
    edges = parsed["edges"]

    lines = ["# Flujo de Agentes de Innovaci\u00f3n IRIS", ""]

    phase_agents = defaultdict(list)
    phase_decisions = defaultdict(list)

    connected_texts = set()
    for e in edges:
        connected_texts.add(e["src_text"])
        connected_texts.add(e["dst_text"])

    for oid, info in topics.items():
        text = info["text"]
        if text not in connected_texts:
            continue
        phase = NODE_PHASE.get(text, "Otros")
        if _is_agent(text):
            phase_agents[phase].append(info)
        else:
            phase_decisions[phase].append(info)

    for phase_name in PHASE_ORDER:
        agents = phase_agents.get(phase_name, [])
        decisions = phase_decisions.get(phase_name, [])
        if not agents and not decisions:
            continue

        lines.append(f"## {phase_name}")
        lines.append("")

        if decisions:
            lines.append("### Puntos de decisi\u00f3n")
            lines.append("")
            seen_dec = set()
            for d in decisions:
                if d["text"] not in seen_dec:
                    seen_dec.add(d["text"])
                    lines.append(f"- **{d['text']}**")
            lines.append("")

        if agents:
            lines.append("### Agentes")
            lines.append("")
            for ag in agents:
                lines.append(f"#### {ag['text']}")
                if ag["notes"]:
                    lines.append("")
                    notes = ag["notes"].replace("<br>", "\n").replace("&lt;br&gt;", "\n")
                    lines.append(f"> {notes}")
                lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## Nodos de referencia (sin conexiones expl\u00edcitas)")
    lines.append("")
    for oid, info in topics.items():
        if info["text"] not in connected_texts:
            lines.append(f"- {info['text']}")
    lines.append("")

    return "\n".join(lines)


def convert(html_path: str, mermaid_path: str, md_path: str) -> None:
    print(f"Reading {html_path}...")
    xml = _extract_xml(html_path)

    print("Parsing mind map...")
    parsed = _parse_mindmap(xml)
    print(f"  Topics: {len(parsed['topics'])}")
    print(f"  Edges: {len(parsed['edges'])}")

    # Phase verification
    phase_counts = defaultdict(lambda: {"agents": 0, "decisions": 0})
    connected = set()
    for e in parsed["edges"]:
        connected.add(e["src_text"])
        connected.add(e["dst_text"])
    for text in connected:
        phase = NODE_PHASE.get(text, "Otros")
        if _is_agent(text):
            phase_counts[phase]["agents"] += 1
        else:
            phase_counts[phase]["decisions"] += 1

    print("  Phase assignments:")
    for p in PHASE_ORDER + ["Otros"]:
        if p in phase_counts:
            c = phase_counts[p]
            print(f"    {p}: {c['agents']} agents, {c['decisions']} decisions")

    # Show any Otros nodes
    otros = [t for t in connected if NODE_PHASE.get(t, "Otros") == "Otros"]
    if otros:
        print(f"  WARNING: {len(otros)} nodes in 'Otros':")
        for t in otros:
            print(f"    - [{t}]")

    print("Generating Mermaid...")
    mermaid = generate_mermaid(parsed)
    Path(mermaid_path).write_text(mermaid, encoding="utf-8")
    print(f"  -> {mermaid_path} ({len(mermaid)} chars)")

    print("Generating Markdown...")
    markdown = generate_markdown(parsed)
    Path(md_path).write_text(markdown, encoding="utf-8")
    print(f"  -> {md_path} ({len(markdown)} chars)")

    print("Done!")


if __name__ == "__main__":
    base = Path.cwd()
    convert(
        str(base / "Flujo Agentes mapa 2.html"),
        str(base / "flujo_mermaid.md"),
        str(base / "flujo_agentes.md"),
    )

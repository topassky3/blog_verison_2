import re
from django import template

register = template.Library()

@register.simple_tag
def build_toc(tutorial):
    """
    Recorre todos los bloques del tutorial y extrae los encabezados <h2> y <h3>.
    Retorna una lista de diccionarios con el nivel, id y texto del encabezado.
    Se buscan en bloques de tipo: text, html, code y latex.
    Sin embargo, si un bloque de tipo 'code' contiene una declaración de documento
    (por ejemplo, DOCTYPE o la etiqueta <html>), se ignora para no dañar la TOC.
    """
    headings = []
    heading_regex = re.compile(r'<h([23])\s+id="([^"]+)"\s*>(.*?)</h\1>', re.IGNORECASE)
    for block in tutorial.blocks.all():
        if block.block_type in ['text', 'html', 'code', 'latex']:
            # Si es un bloque de código y contiene una declaración de documento, lo ignoramos
            if block.block_type == 'code' and ('&lt;!DOCTYPE' in block.content or '&lt;html' in block.content):
                continue
            for match in heading_regex.finditer(block.content):
                level = int(match.group(1))
                id_attr = match.group(2)
                text = match.group(3)
                headings.append({'level': level, 'id': id_attr, 'text': text})
    return headings

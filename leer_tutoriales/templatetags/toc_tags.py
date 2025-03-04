import re
from django import template

register = template.Library()

@register.simple_tag
def build_toc(tutorial):
    """
    Recorre todos los bloques del tutorial y extrae los encabezados <h2> y <h3>.
    Retorna una lista de diccionarios con el nivel, id y texto del encabezado.
    Ahora se buscan encabezados en bloques de tipo: text, html, code y latex.
    """
    headings = []
    # Expresión regular para encontrar h2 y h3 que tengan un atributo id
    heading_regex = re.compile(r'<h([23])\s+id="([^"]+)"\s*>(.*?)</h\1>', re.IGNORECASE)
    for block in tutorial.blocks.all():
        # Se incluye la búsqueda en bloques de tipo 'text', 'html', 'code' y 'latex'
        if block.block_type in ['text', 'html', 'code', 'latex']:
            matches = heading_regex.finditer(block.content)
            for match in matches:
                level = int(match.group(1))
                id_attr = match.group(2)
                text = match.group(3)
                headings.append({'level': level, 'id': id_attr, 'text': text})
    return headings

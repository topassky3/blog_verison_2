import re
from django import template

register = template.Library()


@register.simple_tag
def build_toc(tutorial):
    """
    Recorre todos los bloques del tutorial y extrae los encabezados <h2> y <h3>.
    Retorna una lista de diccionarios con el nivel, id y texto del encabezado.
    Si el bloque es de tipo 'code', se ignora para la generación de la TOC.
    """
    headings = []
    heading_regex = re.compile(r'<h([23])\s+id="([^"]+)"\s*>(.*?)</h\1>', re.IGNORECASE)

    for block in tutorial.blocks.all().order_by('order'):  # Asegúrate de que los bloques estén ordenados

        # --- CAMBIO IMPORTANTE AQUÍ ---
        # Si el bloque es de tipo 'code', lo saltamos completamente para la TOC
        if block.block_type == 'code':
            continue
            # --- FIN DEL CAMBIO ---

        # Solo procesamos los tipos de bloque donde esperamos encontrar encabezados válidos para la TOC
        if block.block_type in ['text', 'html', 'latex']:
            # La siguiente condición original para ignorar DOCTYPE/html en bloques
            # que NO son 'code' (ej. un bloque tipo 'html') puede seguir siendo útil.
            if block.block_type == 'html' and ('<!DOCTYPE' in block.content or '<html' in block.content):
                continue

            for match in heading_regex.finditer(block.content):
                level = int(match.group(1))
                id_attr = match.group(2)
                text = match.group(3)
                headings.append({'level': level, 'id': id_attr, 'text': text})

    return headings
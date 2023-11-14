"""
 def generic_borme(texto_del_pdf):
    extracted_info = []
    
    # Buscar fecha del Borme 
    borme_date_pattern = r'(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+(\d+)\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})'
    borme_date_match = re.search(borme_date_pattern, texto_del_pdf)
    borme_date = borme_date_match.group(0) if borme_date_match else "No encontrado"

    # Buscar la provincia del Acto
    commercial_registry_pattern = r'^Actos inscritos\n([A-Z\/ÁÉÍÓÚÜ\s]+)\n'
    commercial_registry_match = re.search(commercial_registry_pattern, texto_del_pdf, re.MULTILINE)
    commercial_registry = commercial_registry_match.group(1) if commercial_registry_match else "No encontrado"

    # Buscar Sección del Acto
    inscription_section_pattern = r'Pág\.\s+\d+\s+SECCIÓN\s+(PRIMERA|SEGUNDA)'
    inscription_section_match = re.search(inscription_section_pattern, texto_del_pdf)
    inscription_section = inscription_section_match.group(1) if inscription_section_match else "No encontrado"

    # Buscar Categoria del Acto
    inscription_category_pattern = r'Empresarios\s+(.*)\s+'
    inscription_category_match = re.search(inscription_category_pattern, texto_del_pdf)
    inscription_category = inscription_category_match.group(1) if inscription_category_match else "No encontrado"

    # Buscar todos los actos inscritos y extraer informacion
    inscription_pattern = r'^(\d+ - .+?)\n(?=\d+ - |\Z)'
    inscriptions = re.findall(inscription_pattern, texto_del_pdf, re.MULTILINE | re.DOTALL)
"""
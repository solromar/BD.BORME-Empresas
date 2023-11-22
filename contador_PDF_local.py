import os

def contar_pdfs_por_tipo(raiz):
    total_contador = 0
    borme_a_contador = 0
    borme_b_contador = 0
    borme_c_contador = 0
    borme_s_contador = 0
    for directorio, subdirectorios, archivos in os.walk(raiz):
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                total_contador += 1
                if archivo.startswith('BORME-A'):
                    borme_a_contador += 1
                elif archivo.startswith('BORME-B'):
                    borme_b_contador += 1
                elif archivo.startswith('BORME-C'):
                    borme_c_contador += 1
                elif archivo.startswith('BORME-S'):
                    borme_s_contador += 1
    return total_contador, borme_a_contador, borme_b_contador, borme_c_contador, borme_s_contador

# Reemplaza 'ruta/a/tu/carpeta' con la ruta de tu carpeta
ruta_carpeta = '/home/soledad/BD.BORME-Empresas/files/prueba'
total_pdfs, total_pdfs_borme_a, total_pdfs_borme_b, total_pdfs_borme_c, total_pdfs_borme_s = contar_pdfs_por_tipo(ruta_carpeta)
print(f"Total de archivos PDF en '{ruta_carpeta}': {total_pdfs}")
print(f"Total de archivos PDF 'BORME-A' en '{ruta_carpeta}': {total_pdfs_borme_a}")
print(f"Total de archivos PDF 'BORME-B' en '{ruta_carpeta}': {total_pdfs_borme_b}")
print(f"Total de archivos PDF 'BORME-C' en '{ruta_carpeta}': {total_pdfs_borme_c}")
print(f"Total de archivos PDF 'BORME-S' en '{ruta_carpeta}': {total_pdfs_borme_s}")

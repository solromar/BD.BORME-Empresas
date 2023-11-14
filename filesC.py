"""
public function handleFileTypeC($textoDelPdf, $fileName)
    {
        $inscription = '';

        // Busca la categoria (Actos inscritos u Otros actos inscritos, etc)
        if (preg_match("/SECCIÓN SEGUNDA - Anuncios y avisos legales\s+(.*)\s+/", $textoDelPdf, $matches)) {
            $inscriptionCategory = $matches[1];
        }

        //Almacena cada acto en un texto plano
        if (preg_match("/^[0-9].*?\d{1,2}\s+de\s+\w+\s+de\s+\d{4}.*?(?=\ncve:)/ms", $textoDelPdf, $matches)) {
            $inscription = $matches[0];
        }

        // Busca la fecha del Borme que estoy procesando
        $this->findGenericBormeSectionAndDate($textoDelPdf, $inscriptionSection ,$bormeDate);

        //TODO: ver que hacer en caso que haya mas de una sociedad, por ej en las fusiones
        // Buscar el nombre de la sociedad
        if (preg_match("/^\d+\s-\s(.*)(?:\n|\r\n)/m", $inscription, $matches)) {
            $companyName = $matches[1];
        }

        //Busca el numero de acto
        if (preg_match("/^\d+/m", $textoDelPdf, $matches)) {
            $inscriptionNumber = $matches[0];
        }

        //Busca el tipo de acto, que luego usaremos para $companyState
        $lineas = explode("\n", $textoDelPdf);

        $inscriptionName = "";

        foreach ($lineas ?? [] as $linea) {
            if (strpos($linea, "Declaración de insolvencia") !== false) {
                $inscriptionName .= $linea . "\n";
            }
            if (strpos($linea, "Disolución de empresas") !== false) {
                $inscriptionName .= $linea . "\n";
            }
            if (strpos($linea, "Pérdida de certificación") !== false) {
                $inscriptionName .= $linea . "\n";
            }
        }

        $this->persistCompanyInscription(
            $inscriptionName ?? null,
            $companyName ?? null,
            $comercialRegistryConstitucion ?? null,
            $inscriptionNumber ?? null,
            $inscriptionSection ?? null,
            $inscriptionCategory ?? null,
            $inscription ?? null,
            $fileName ?? null,
            $bormeDate ?? null,
        );
    }
    """
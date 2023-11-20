"""
public function handleFileTypeB($textoDelPdf, $fileName)
    {
        $inscription = '';

        if (preg_match('/^Otros actos publicados en el Registro Mercantil\n([A-Z\/ÁÉÍÓÚÜ]+)\n/m', $textoDelPdf, $matches)) {
            $comercialRegistryConstitucion = $matches[1];
        }
        
        $this->findBormeVars_A_B($textoDelPdf, $inscriptionCategory, $inscriptions);
        $this->findGenericBormeSectionAndDate($textoDelPdf, $inscriptionSection ,$bormeDate);

        foreach ($inscriptions ?? [] as $key => $inscription) {
            $pattern = "/^\d+\s-\s(.*)(\R|$)/m";
            if (preg_match($pattern, $inscription, $matches)) {
                $companyName = $matches[1];
            } else {
                $companyName = 'Nombre no encontrado';
            }

            if (preg_match("/^\d+/m", $inscription, $matches)) {
                $inscriptionNumber = $matches[0];
            }            
            
            $pattern = "/^(Depósito|Cierre|Reapertura|Cancelación).*/m";
            if (preg_match($pattern, $inscription, $matches)) {
                $inscriptionName = $matches[0] ?? 'ERROR';
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
    }
    """
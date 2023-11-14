
"""
public function handleFileTypeA($textoDelPdf, $fileName)
    {
        $inscription = '';

        if (preg_match('/^Actos inscritos\n([A-Z\/ÁÉÍÓÚÜ]+)\n/m', $textoDelPdf, $matches)) {
            $comercialRegistryConstitucion = $matches[1];
        }

        $this->findBormeVars_A_B($textoDelPdf, $inscriptionCategory, $inscriptions);
        $this->findGenericBormeSectionAndDate($textoDelPdf, $inscriptionSection ,$bormeDate);
        
        foreach ($inscriptions ?? [] as $key => $inscription) {
            if (preg_match('/^\d+\s-\s(.*)(\R|$)/m', $inscription, $matches)) {
                $companyName = $matches[1];
            } else {
                $companyName = 'Nombre no encontrado';
            }
            
            if (preg_match("/^\d+/m", $inscription, $matches)) {
                $inscriptionNumber = $matches[0];
            }

            $lines = explode("\n", $inscription);
            $secondLine = isset($lines[1]) ? $lines[1] : '';
            $inscriptionName = '';

            if (!empty($secondLine)) {
                $pattern = '/^[^\.|:]+/';
                if (preg_match($pattern, $secondLine, $matches)) {
                    $inscriptionName = isset($matches[0]) ? $matches[0] : 'ERROR';
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
    }
    
"""
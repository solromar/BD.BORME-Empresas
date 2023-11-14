class Company_inscription:
    def __init__(self, id, createdAt, updatedAt, companyId, inscriptionCommercialRegistry, inscriptionNumber, inscriptionSection, inscriptionCategory, inscriptionName, inscriptionDate, inscriptionRegistryData, inscription, bormeDate, inscriptionFile):
        self.id = id
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.companyId = companyId # ES LA RELACION CON COMPANY
        self.inscriptionCommercialRegistry = inscriptionCommercialRegistry
        self.inscriptionNumber = inscriptionNumber
        self.inscriptionSection = inscriptionSection
        self.inscriptionCategory = inscriptionCategory
        self.inscriptionName = inscriptionName
        self.inscriptionDate = inscriptionDate
        self.inscriptionRegistryData = inscriptionRegistryData
        self.inscription = inscription
        self.bormeDate = bormeDate
        self.inscriptionFile = inscriptionFile
        
    
    def toDBCollection(self):
         return{
             "id" : self.id,
             "createdAt" : self.createdAt,
             "updatedAt" : self.updatedAt,
             "companyId": self.companyId,
             "inscriptionCommercialRegistry": self.inscriptionCommercialRegistry,
             "inscriptionNumber": self.inscriptionNumber,
             "inscriptionSection": self.inscriptionSection,
             "inscriptionCategory": self.inscriptionCategory,
             "inscriptionName": self.inscriptionName,
             "inscriptionDate": self.inscriptionDate,
             "inscriptionRegistryData": self.inscriptionRegistryData,
             "inscription": self.inscription,
             "bormeDate": self.bormeDate,
             "inscriptionFile": self.inscriptionFile              
         }
            
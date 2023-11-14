class Company:
    def __init__(self, id, createdAt, updatedAt, companyInscription, companySocialDenomination, companyName, companyNif, companyCurrentAddress, companyCurrentSocialObject, companyCurrentSocialCapital, companyPhoneNumber, companyEmail,companyWeb, companyEmployeesNumber, companyParent, constitutionCommercialRegistry, constitutionDate, operationsStartDate, companyDuration, constitutionAddress, constitutionSocialObject, constitutionSocialCapital, constitutionRegistryData, constitutionInscription, constitutionFile, companyState, administrationType, administratorsList, administrationAppointmentDate, administrationAppointmentInscription, administrationAppointmentFile):
        self.id = id
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.companyInscription = companyInscription # ESTA ES LA RELACION ENTRE COMPANY y COMPANY_INSCRIPTION
        self.companySocialDenomination = companySocialDenomination
        self.companyName = companyName
        self.companyNif = companyNif
        self.companyCurrentAddress = companyCurrentAddress
        self.companyCurrentSocialObject = companyCurrentSocialObject
        self.companyCurrentSocialCapital = companyCurrentSocialCapital
        self.companyPhoneNumber = companyPhoneNumber
        self.companyEmail = companyEmail
        self.companyWeb = companyWeb
        self.companyEmployeesNumber = companyEmployeesNumber
        self.companyParent = companyParent
        self.constitutionCommercialRegistry = constitutionCommercialRegistry
        self.constitutionDate = constitutionDate
        self.operationsStartDate = operationsStartDate
        self.companyDuration = companyDuration
        self.constitutionAddress = constitutionAddress
        self.constitutionSocialObject = constitutionSocialObject
        self.constitutionSocialCapital = constitutionSocialCapital
        self.constitutionRegistryData = constitutionRegistryData
        self.constitutionInscription = constitutionInscription
        self.constitutionFile = constitutionFile
        self.companyState = companyState
        self.administrationType = administrationType
        self.administratorsList = administratorsList
        self.administrationAppointmentDate = administrationAppointmentDate
        self.administrationAppointmentInscription = administrationAppointmentInscription
        self.administrationAppointmentFile = administrationAppointmentFile     
        
        
    def toDBCollection (self):
         return{
             "id" : self.id,
             "createdAt" : self.createdAt,
             "updatedAt" : self.updatedAt,
             "companyInscription" : self.companyInscription, # ESTA ES LA RELACION ENTRE COMPANY y COMPANY_INSCRIPTION
             "companySocialDenomination" : self.companySocialDenomination,
             "companyName" : self.companyName,
             "companyNif" : self.companyNif,
             "companyCurrentAddress" : self.companyCurrentAddress,
             "companyCurrentSocialObject" : self.companyCurrentSocialObject,
             "companyCurrentSocialCapital" : self.companyCurrentSocialCapital,
             "companyPhoneNumber" : self.companyPhoneNumber,
             "companyEmail" : self.companyEmail,
             "companyWeb" : self.companyWeb,
             "companyEmployeesNumber" : self.companyEmployeesNumber,
             "companyParent" : self.companyParent,
             "constitutionCommercialRegistry" : self.constitutionCommercialRegistry,
             "constitutionDate" : self.constitutionDate,
             "operationsStartDate" : self.operationsStartDate,
             "companyDuration" : self.companyDuration,
             "constitutionAddress" : self.constitutionAddress,
             "constitutionSocialObject" : self.constitutionSocialObject,
             "constitutionSocialCapital" : self.constitutionSocialCapital,
             "constitutionRegistryData" : self.constitutionRegistryData,
             "constitutionInscription" : self.constitutionInscription,
             "constitutionFile" : self.constitutionFile,
             "companyState" : self.companyState,
             "administrationType" : self.administrationType,
             "administratorsList" : self.administratorsList,
             "administrationAppointmentDate" : self.administrationAppointmentDate,
             "administrationAppointmentInscription" : self.administrationAppointmentInscription,
             "administrationAppointmentFile" : self.administrationAppointmentFile
         }   
from typing import Tuple, Set, Iterable, List


class DesignToFabricationConverter:
    def __init__(self, document: Document): ...
    @property
    def IsValidObject(self) -> bool: ...
    def Convert(self, selection: ISet, serviceId: int) -> DesignToFabricationConverterResult: ...
    def SetMapForFamilySymbolToFabricationPartType(self, typeMappings: IDictionary) -> DesignToFabricationMappingResult: ...
    def GetPartialConvertFailureResults(self) -> List[PartialFailureResults]: ...
    def GetConvertedFabricationParts(self) -> ISet: ...
    def GetElementsWithOpenConnector(self) -> ISet: ...
    def GetConvertedFabricationPartsWithInvalidConnections(self) -> IDictionary: ...
    def GetDesignElementAndFabricationPartsWithOpenConnectors(self) -> IDictionary: ...
    def GetDesignElementAndFabricationPartsWithDifferentOffsets(self) -> IDictionary: ...
    def Dispose(self) -> None: ...


class DesignToFabricationConverterResult:
    Success = 0
    PartialFailure = 1


class PartialFailureResults:
    NotAllPartsConverted = 0
    InvalidConnections = 1
    HaveOpenConnectors = 2
    HaveDifferentOffsets = 3
    NoMatchingSize = 4


class DesignToFabricationMappingResult:
    Success = 0
    Undefined = 1
    InvalidFamilySymbol = 2
    InvalidFabricationPartType = 3
    UnsupportedFamilySymbol = 4
    UnsupportedFabricationPartType = 5


class FabricationPartPlacementUtils:


class FabricationPartRouteEnd:
    @property
    def IsValidObject(self) -> bool: ...
    def CreateFromConnector(connnector: Connector) -> FabricationPartRouteEnd: ...
    def CreateFromCenterline(element: Element, ptAt: XYZ) -> FabricationPartRouteEnd: ...
    def Dispose(self) -> None: ...


class FabricationSaveJobOptions:
    @overload
    def __init__(self, addHolesForTaps: bool): ...
    @overload
    def __init__(self): ...
    @property
    def AddHolesForTaps(self) -> bool: ...
    @AddHolesForTaps.setter
    def AddHolesForTaps(self, addHolesForTaps: bool) -> None: ...
    @property
    def IsValidObject(self) -> bool: ...
    def Dispose(self) -> None: ...


class FabricationNetworkChangeService:
    def __init__(self, document: Document): ...
    @property
    def IsValidObject(self) -> bool: ...
    @overload
    def ChangeService(self, selection: ISet, serviceId: int, paletteId: int, restrictPalette: bool) -> FabricationNetworkChangeServiceResult: ...
    @overload
    def ChangeService(self, selection: ISet, serviceId: int, paletteId: int) -> FabricationNetworkChangeServiceResult: ...
    def ChangeSize(self, selection: ISet, fabricationPartSizeMaps: ISet) -> FabricationNetworkChangeServiceResult: ...
    def ApplyChange(self) -> FabricationNetworkChangeServiceResult: ...
    def GetStraightsThatWereNotChanged(self) -> ISet: ...
    def GetElementsThatFailed(self) -> ISet: ...
    def SetSelection(self, selection: ISet) -> FabricationNetworkChangeServiceResult: ...
    def SetServiceId(self, serviceId: int) -> None: ...
    def SetPaletteId(self, paletteId: int) -> None: ...
    def SetRestrictPalette(self, restrictPalette: bool) -> None: ...
    def SetMapOfInLinePartTypes(self, fabricationPartTypes: IDictionary) -> None: ...
    def GetInLinePartTypes(self) -> ISet: ...
    def SetMapOfSizesForStraights(self, fabricationPartSizeMaps: ISet) -> None: ...
    def GetMapOfAllSizesForStraights(self) -> ISet: ...
    def Dispose(self) -> None: ...


class FabricationPartSizeMap:
    @overload
    def __init__(self, size: str, widthDiameter: float, depth: float, isProductList: bool, profileType: ConnectorProfileType, serviceId: int, paletteId: int): ...
    @overload
    def __init__(self, size: str, widthDiameter: float, depth: float, isProductList: bool): ...
    @property
    def SizeString(self) -> str: ...
    @SizeString.setter
    def SizeString(self, sizeString: str) -> None: ...
    @property
    def WidthDiameter(self) -> float: ...
    @WidthDiameter.setter
    def WidthDiameter(self, widthDiameter: float) -> None: ...
    @property
    def Depth(self) -> float: ...
    @Depth.setter
    def Depth(self, depth: float) -> None: ...
    @property
    def IsProductList(self) -> bool: ...
    @IsProductList.setter
    def IsProductList(self, isProductList: bool) -> None: ...
    @property
    def ProfileType(self) -> ConnectorProfileType: ...
    @ProfileType.setter
    def ProfileType(self, profileType: ConnectorProfileType) -> None: ...
    @property
    def ServiceId(self) -> int: ...
    @ServiceId.setter
    def ServiceId(self, serviceId: int) -> None: ...
    @property
    def PaletteId(self) -> int: ...
    @PaletteId.setter
    def PaletteId(self, paletteId: int) -> None: ...
    @property
    def MappedWidthDiameter(self) -> float: ...
    @MappedWidthDiameter.setter
    def MappedWidthDiameter(self, mappedWidthDiameter: float) -> None: ...
    @property
    def MappedDepth(self) -> float: ...
    @MappedDepth.setter
    def MappedDepth(self, mappedDepth: float) -> None: ...
    @property
    def IsMappedProductList(self) -> bool: ...
    @IsMappedProductList.setter
    def IsMappedProductList(self, isMappedProductList: bool) -> None: ...
    @property
    def MappedProfileType(self) -> ConnectorProfileType: ...
    @MappedProfileType.setter
    def MappedProfileType(self, mappedProfileType: ConnectorProfileType) -> None: ...
    @property
    def MappedServiceId(self) -> int: ...
    @MappedServiceId.setter
    def MappedServiceId(self, mappedServiceId: int) -> None: ...
    @property
    def AllowMultipleServiceSizes(self) -> bool: ...
    @AllowMultipleServiceSizes.setter
    def AllowMultipleServiceSizes(self, allowMultipleServiceSizes: bool) -> None: ...
    @property
    def IsValidObject(self) -> bool: ...
    def Dispose(self) -> None: ...


class FabricationUtils:
    def ValidateConnectivity(document: Document, connector1: Connector, connector2: Connector) -> bool: ...
    def ExportToPCF(document: Document, ids: List[ElementId], filename: str) -> None: ...


class FabricationAncillaryType:
    Unknown = 0
    Fixing = 1
    Corner = 2
    Clip = 3
    TieRod = 4
    Gasket = 5
    Sealant = 6
    SupportRod = 7
    AncillaryMaterial = 8
    AirturnTrack = 9
    AirturnVane = 10
    Isolator = 11
    SeamMaterial = 12


class FabricationAncillaryUsageType:
    Undefined = 0
    Loose = 1
    Connector = 2
    Seam = 3
    Splitter = 4
    Airturn = 5
    Hanger = 6
    Stiffener = 7


class FabricationCustomDataType:
    Text = 1
    Integer = 2
    Real = 3


class FabricationPartJustification:
    Middle = 0
    Bottom = 1
    Top = 2


class FabricationPartFitResult:
    Success = 0
    IncompatibleGeometry = 1
    MisalignedEnds = 2
    DimensionLocked = 3
    BadDimensions = 4
    ShapeMismatch = 5
    SizeMismatch = 6
    IncompatibleConnection = 7
    OffsetRequired = 8
    Unsupported = 255


class ValidationStatus:
    Valid = 0
    InvalidDimensions = 1
    NoMaterial = 2


class FabricationPartCompareType:
    CutType = 1
    Material = 2
    Specification = 3
    InsulationSpecification = 4
    MaterialGauge = 5
    DuctFacing = 6
    Insulation = 7
    Notes = 8
    Filename = 9
    Description = 10
    CID = 11
    SkinMaterial = 12
    SkinGauge = 13
    Section = 14
    Status = 15
    Service = 16
    Pallet = 17
    BoxNo = 18
    OrderNo = 19
    Drawing = 20
    Zone = 21
    ETag = 22
    Alt = 23
    Spool = 24
    Alias = 25
    PCFKey = 26
    CustomData = 27
    ButtonAlias = 28


class FabricationNetworkChangeServiceResult:
    Success = 0
    PartialFailure = 1
    UserAborted = 2
    InvalidSelection = 3

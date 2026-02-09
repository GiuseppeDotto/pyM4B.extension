from typing import Tuple, Set, Iterable, List


class RevitAPIEventArgs:
    @property
    def Cancellable(self) -> bool: ...
    @property
    def IsValidObject(self) -> bool: ...
    def IsCancelled(self) -> bool: ...
    def Dispose(self) -> None: ...


class RevitAPIPreEventArgs(RevitAPIEventArgs):
    def Cancel(self) -> None: ...


class RevitAPIPostEventArgs(RevitAPIEventArgs):
    @property
    def Status(self) -> RevitAPIEventStatus: ...


class RevitAPISingleEventArgs(RevitAPIEventArgs):


class RevitAPIPreDocEventArgs(RevitAPIPreEventArgs):
    @property
    def Document(self) -> Document: ...


class RevitAPIPostDocEventArgs(RevitAPIPostEventArgs):
    @property
    def Document(self) -> Document: ...


class ApplicationInitializedEventArgs(RevitAPISingleEventArgs):


class DocumentClosingEventArgs(RevitAPIPreDocEventArgs):
    @property
    def DocumentId(self) -> int: ...


class DocumentClosedEventArgs(RevitAPIPostEventArgs):
    @property
    def DocumentId(self) -> int: ...


class DocumentPrintingEventArgs(RevitAPIPreDocEventArgs):
    def GetViewElementIds(self) -> List[ElementId]: ...
    def GetSettings(self) -> IPrintSetting: ...


class DocumentPrintedEventArgs(RevitAPIPostDocEventArgs):
    def GetPrintedViewElementIds(self) -> List[ElementId]: ...
    def GetFailedViewElementIds(self) -> List[ElementId]: ...


class ViewPrintingEventArgs(RevitAPIPreDocEventArgs):
    @property
    def Index(self) -> int: ...
    @property
    def TotalViews(self) -> int: ...
    @property
    def View(self) -> View: ...
    def GetSettings(self) -> IPrintSetting: ...


class ViewPrintedEventArgs(RevitAPIPostDocEventArgs):
    @property
    def Index(self) -> int: ...
    @property
    def TotalViews(self) -> int: ...
    @property
    def View(self) -> View: ...


class DocumentSavingEventArgs(RevitAPIPreDocEventArgs):


class DocumentSavedEventArgs(RevitAPIPostDocEventArgs):


class DocumentSavingAsEventArgs(RevitAPIPreDocEventArgs):
    @property
    def PathName(self) -> str: ...
    @property
    def IsSavingAsCentralFile(self) -> bool: ...


class DocumentSavedAsEventArgs(RevitAPIPostDocEventArgs):
    @property
    def OriginalPath(self) -> str: ...
    @property
    def IsSavingAsCentralFile(self) -> bool: ...


class DocumentSynchronizingWithCentralEventArgs(RevitAPIPreDocEventArgs):
    @property
    def Location(self) -> str: ...
    @property
    def Comments(self) -> str: ...
    @property
    def Options(self) -> SynchronizeWithCentralOptions: ...


class DocumentSynchronizedWithCentralEventArgs(RevitAPIPostDocEventArgs):


class RevitEventArgs:
    @property
    def Cancel(self) -> bool: ...
    @Cancel.setter
    def Cancel(self, value: bool) -> None: ...
    @property
    def Cancellable(self) -> bool: ...


class PreEventArgs(RevitEventArgs):


class PreDocEventArgs(PreEventArgs):
    @property
    def Document(self) -> Document: ...


class PostEventArgs(RevitEventArgs):
    @property
    def Status(self) -> EventStatus: ...


class PostDocEventArgs(PostEventArgs):
    @property
    def Document(self) -> Document: ...


class RevitAPIEventStatus:
    Succeeded = 0
    Cancelled = 1
    Failed = -1


class EventStatus:
    Succeeded = 0
    Cancelled = 1
    Failed = -1


class DocumentChangedEventArgs(RevitAPISingleEventArgs):
    @property
    def Operation(self) -> UndoOperation: ...
    @overload
    def GetAddedElementIds(self, filter: ElementFilter) -> ICollection: ...
    @overload
    def GetAddedElementIds(self) -> ICollection: ...
    def GetDeletedElementIds(self) -> ICollection: ...
    @overload
    def GetModifiedElementIds(self, filter: ElementFilter) -> ICollection: ...
    @overload
    def GetModifiedElementIds(self) -> ICollection: ...
    def GetDocument(self) -> Document: ...
    def GetTransactionNames(self) -> List[str]: ...


class DocumentCreatingEventArgs(RevitAPIPreEventArgs):
    @property
    def Template(self) -> str: ...
    @property
    def DocumentType(self) -> DocumentType: ...


class DocumentCreatedEventArgs(RevitAPIPostDocEventArgs):


class DocumentOpeningEventArgs(RevitAPIPreEventArgs):
    @property
    def PathName(self) -> str: ...
    @property
    def DocumentType(self) -> DocumentType: ...


class DocumentOpenedEventArgs(RevitAPIPostDocEventArgs):


class DocumentWorksharingEnabledEventArgs(RevitAPISingleEventArgs):
    def GetDocument(self) -> Document: ...


class ElementTypeDuplicatingEventArgs(RevitAPIPreDocEventArgs):
    @property
    def ElementTypeId(self) -> ElementId: ...


class ElementTypeDuplicatedEventArgs(RevitAPIPostDocEventArgs):
    @property
    def OriginalElementTypeId(self) -> ElementId: ...
    @property
    def NewName(self) -> str: ...
    @property
    def NewElementTypeId(self) -> ElementId: ...


class ExternalDataInstanceAddingIntoDocumentEventArgs(RevitAPIPreDocEventArgs):
    @property
    def TypeId(self) -> ElementId: ...


class ExternalDataInstanceAddedIntoDocumentEventArgs(RevitAPIPostDocEventArgs):
    @property
    def TypeId(self) -> ElementId: ...
    @property
    def ProjectId(self) -> str: ...
    @property
    def ItemId(self) -> str: ...
    @property
    def NewInstanceId(self) -> ElementId: ...


class ExternalDataInstanceRemovingFromDocumentEventArgs(RevitAPIPreDocEventArgs):
    @property
    def TypeId(self) -> ElementId: ...
    @property
    def InstanceId(self) -> ElementId: ...


class ExternalDataInstanceRemovedFromDocumentEventArgs(RevitAPIPostDocEventArgs):
    @property
    def TypeId(self) -> ElementId: ...


class ExternalDataTypeServerFailureResolutionExecutingEventArgs(RevitAPIPreDocEventArgs):


class FailuresProcessingEventArgs(RevitAPISingleEventArgs):
    def SetProcessingResult(self, result: FailureProcessingResult) -> None: ...
    def GetProcessingResult(self) -> FailureProcessingResult: ...
    def GetFailuresAccessor(self) -> FailuresAccessor: ...


class FamilyLoadingIntoDocumentEventArgs(RevitAPIPreDocEventArgs):
    @property
    def FamilyName(self) -> str: ...
    @property
    def FamilyPath(self) -> str: ...


class FamilyLoadedIntoDocumentEventArgs(RevitAPIPostDocEventArgs):
    @property
    def FamilyName(self) -> str: ...
    @property
    def FamilyPath(self) -> str: ...
    @property
    def OriginalFamilyId(self) -> ElementId: ...
    @property
    def NewFamilyId(self) -> ElementId: ...


class FileImportingEventArgs(RevitAPIPreDocEventArgs):
    @property
    def Path(self) -> str: ...
    @property
    def Format(self) -> ImportExportFileFormat: ...


class FileImportedEventArgs(RevitAPIPostDocEventArgs):
    @property
    def Path(self) -> str: ...
    @property
    def Format(self) -> ImportExportFileFormat: ...
    @property
    def ImportedInstanceId(self) -> ElementId: ...


class FileExportingEventArgs(RevitAPIPreDocEventArgs):
    @property
    def Path(self) -> str: ...
    @property
    def Format(self) -> ImportExportFileFormat: ...


class FileExportedEventArgs(RevitAPIPostDocEventArgs):
    @property
    def Path(self) -> str: ...
    @property
    def Format(self) -> ImportExportFileFormat: ...


class ViewExportingEventArgs(RevitAPIPreDocEventArgs):
    @property
    def ViewId(self) -> ElementId: ...


class ViewExportedEventArgs(RevitAPIPostDocEventArgs):
    @property
    def ViewId(self) -> ElementId: ...


class ViewsExportingByContextEventArgs(RevitAPIPreDocEventArgs):
    def GetViewIds(self) -> List[ElementId]: ...


class ViewsExportedByContextEventArgs(RevitAPIPostDocEventArgs):
    def GetViewIds(self) -> List[ElementId]: ...


class LinkedResourceOpeningEventArgs(RevitAPIPreEventArgs):
    @property
    def ResourceType(self) -> ExternalResourceType: ...
    @property
    def LinkedResourcePathName(self) -> str: ...


class LinkedResourceOpenedEventArgs(RevitAPIPostDocEventArgs):
    @property
    def ResourceType(self) -> ExternalResourceType: ...
    @property
    def ResourceTypeId(self) -> ElementId: ...
    @property
    def LinkedResourcePathName(self) -> str: ...


class ProgressChangedEventArgs(RevitAPISingleEventArgs):
    @property
    def Stage(self) -> ProgressStage: ...
    @property
    def Position(self) -> int: ...
    @property
    def LowerRange(self) -> int: ...
    @property
    def UpperRange(self) -> int: ...
    @property
    def Caption(self) -> str: ...
    def Cancel(self) -> None: ...


class DocumentReloadingLatestEventArgs(RevitAPIPreDocEventArgs):


class DocumentReloadedLatestEventArgs(RevitAPIPostDocEventArgs):
    @property
    def Location(self) -> str: ...
    @Location.setter
    def Location(self, location: str) -> None: ...


class WorksharedOperationProgressChangedEventArgs(RevitAPISingleEventArgs):
    @property
    def Location(self) -> str: ...
    @property
    def Status(self) -> RevitAPIEventStatus: ...


class DocumentSaveToLocalProgressChangedEventArgs(WorksharedOperationProgressChangedEventArgs):
    @property
    def BeforeSaveToCentral(self) -> bool: ...
    @property
    def FinishedStreams(self) -> int: ...
    @property
    def TotalStreams(self) -> int: ...
    @property
    def SaveToLocalFinished(self) -> bool: ...


class DataTransferProgressChangedEventArgs(WorksharedOperationProgressChangedEventArgs):
    @property
    def TransferMode(self) -> DataTransferMode: ...
    @property
    def Speed(self) -> float: ...
    @property
    def FinishedSize(self) -> float: ...
    @property
    def TotalSize(self) -> float: ...


class DocumentReloadLatestProgressChangedEventArgs(DataTransferProgressChangedEventArgs):
    @property
    def RetryTimes(self) -> int: ...
    @property
    def IsMerging(self) -> bool: ...
    @property
    def ReloadLatestFinished(self) -> bool: ...


class DocumentSaveToCentralProgressChangedEventArgs(DataTransferProgressChangedEventArgs):
    @property
    def RetryTimes(self) -> int: ...
    @property
    def SaveToCentralFinished(self) -> bool: ...
    @property
    def FailureDueToConflicts(self) -> bool: ...


class CreateRelatedFileProgressChangedEventArgs(DataTransferProgressChangedEventArgs):
    @property
    def CreatingCloudSharedLocal(self) -> bool: ...
    @property
    def FullDownload(self) -> bool: ...
    @property
    def DownloadFinished(self) -> bool: ...


class UndoOperation:
    TransactionCommitted = 0
    TransactionRolledBack = 1
    TransactionGroupRolledBack = 2
    TransactionUndone = 3
    TransactionRedone = 4


class ProgressStage:
    Started = 0
    RangeChanged = 1
    PositionChanged = 2
    CaptionChanged = 3
    Unchanged = 4
    Finished = 5


class DataTransferMode:
    Download = 0
    Upload = 1
    Undefined = -1

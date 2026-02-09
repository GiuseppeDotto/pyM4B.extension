from typing import Tuple, Set, Iterable, List


class FunctionId:
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...
    @property
    def File(self) -> str: ...
    @property
    def Line(self) -> int: ...
    @property
    def Function(self) -> str: ...


class ApplicationException:
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...
    @property
    def FunctionId(self) -> FunctionId: ...


class ArgumentException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...
    @property
    def Message(self) -> str: ...
    @property
    def ParamName(self) -> str: ...


class ArgumentOutOfRangeException(ArgumentException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ArgumentNullException(ArgumentException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InvalidPathArgumentException(ArgumentException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class FileArgumentNotFoundException(ArgumentException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class FileArgumentAlreadyExistsException(ArgumentException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ArgumentsInconsistentException(ArgumentException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InvalidOperationException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InvalidObjectException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ModificationOutsideTransactionException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ModificationForbiddenException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ObjectAccessException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InapplicableDataException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class FamilyContextException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class DisabledDisciplineException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InsufficientResourcesException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class IOException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class FileNotFoundException(IOException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class DirectoryNotFoundException(IOException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class FileAccessException(IOException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InvalidDataStreamException(IOException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class InternalException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ExternalApplicationException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RegenerationFailedException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class AutoJoinFailedException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class ForbiddenForDynamicUpdateException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class OptionalFunctionalityNotAvailableException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class OperationCanceledException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CorruptModelException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerCommunicationException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerInternalException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerUnauthorizedException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerUnauthenticatedUserException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerCollaborationNotAvailableException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerModelAlreadyExistsException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class RevitServerModelNameBreaksConventionException(RevitServerException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CentralModelException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CentralFileCommunicationException(CentralModelException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CentralModelAccessDeniedException(CentralModelException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CentralModelContentionException(CentralModelException):
    @property
    def CurrentUser(self) -> str: ...
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class OutdatedDirectlyOpenedCentralException(CentralModelException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CentralModelAlreadyExistsException(CentralModelException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CentralModelVersionArchivedException(CentralModelException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CheckoutElementsRequestTooLargeException(CentralModelException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class WrongUserException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class TransmittedModelException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class NotTransmittedModelException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class CannotOpenBothCentralAndLocalException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class TransientElementCreationException(InvalidOperationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...


class BackgroundTaskCancelledException(ApplicationException):
    def GetObjectData(self, info: SerializationInfo, context: StreamingContext) -> None: ...

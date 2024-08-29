# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import json
from json import JSONDecodeError
from typing import Callable, List, Optional, Dict, Union, Any, Type, cast, TypeVar, Tuple
import logging

from PyQt6.QtCore import QUrl, pyqtSlot
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from UM.Logger import Logger
from cura.CuraApplication import CuraApplication

from Pragostroj.src.EndpointModel.PGBaseModel import PGBaseModel
from Pragostroj.src.EndpointModel.PGRecentFile import PGRecentFile
from Pragostroj.src.EndpointModel.PGFile import PGFile
from Pragostroj.src.EndpointModel.PGProductInfo import PGProductInfo
from Pragostroj.src.EndpointModel.PGPrinterStatus import PGPrinterStatus
from Pragostroj.src.EndpointModel.PGExtruder import PGExtruder
from Pragostroj.src.EndpointModel.PGPrintOperationResult import PGPrintOperationResult
from Pragostroj.src.EndpointModel.PGMemoryFiles import PGMemoryFiles
from Pragostroj.src.EndpointModel.PGPrintInfo import PGPrintInfo
from Pragostroj.src.EndpointModel.PGPrintResult import PGPrintResult
from Pragostroj.src.EndpointModel.PGPlate import PGPlate
from Pragostroj.src.EndpointModel.PGPrinterState import PGPrinterState
from Pragostroj.src.EndpointModel.PGCheckFile import PGCheckFile
from Pragostroj.src.EndpointModel.PGEndInfo import PGEndInfo


PGApiClientModel = TypeVar("PGApiClientModel", bound=PGBaseModel)
"""The generic type variable used to document the methods below."""


logger = logging.getLogger(__name__)


class PGApiClient:
    """The ClusterApiClient is responsible for all network calls to local network clusters."""

    PRINTER_API_PREFIX = ":8080/api/v1"

    # TODO: Is the list emptied properly?
    # In order to avoid garbage collection we keep the callbacks in this list.
    _anti_gc_callbacks = []  # type: List[Callable[[], None]]

    def __init__(self, address: str, on_error: Callable) -> None:
        """Initializes a new cluster API client.

        :param address: The network address of the cluster to call.
        :param on_error: The callback to be called whenever we receive errors from the server.
        """
        self._manager = QNetworkAccessManager()

        self._address = address
        # TODO: move next to on_finished. So OutputDevice will pass it to every request-function
        self._on_error = on_error

        # print('------------PROXY SETUP---------------')
        # # from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        # # print("Qt: v", QT_VERSION_STR, "\tPyQt: v", PYQT_VERSION_STR)
        # from PyQt6.QtNetwork import QNetworkProxy
        # try:
        #     proxy = QNetworkProxy()
        #     # proxy.setType(QNetworkProxy.DefaultProxy)
        #     proxy.setType(QNetworkProxy.ProxyType.HttpProxy)
        #     # proxy.setType(QNetworkProxy.Socks5Proxy)
        #     proxy.setHostName("localhost")
        #     proxy.setPort(8888)
        #     QNetworkProxy.setApplicationProxy(proxy)
        #     self._manager.setProxy(proxy)
        #     print('------------PROXY SET---------------')
        # except Exception as e:
        #     print('--Exception--')
        #     print(e)

    def _createEmptyRequest(self, path: str, content_type: Optional[str] = "application/json") -> QNetworkRequest:
        """We override _createEmptyRequest in order to add the user credentials.

        :param url: The URL to request
        :param content_type: The type of the body contents.
        """
        url = QUrl("http://" + self._address + path)
        language = CuraApplication.getInstance().getPreferences().getValue("general/language").replace('_', '-')
        # logger.debug(f'----LANGUAGE: {language}')
        # print()
        # print('................................................')
        # print('CreateEmptyRequest')
        request = QNetworkRequest(url)
        request.setRawHeader(b'Accept-Language', language.encode('utf-8'))
        # request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        if content_type:
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, content_type)
            # TODO: Add Header for Accept-Language
        return request

    # NOTE: disabled-function-logging because of "spam"
    # @staticmethod
    # def _parseReply(reply: QNetworkReply) -> Tuple[int, Dict[str, Any]]:
    #     """Parses the given JSON network reply into a status code and a dictionary, handling unexpected errors as well.

    #     :param reply: The reply from the server.
    #     :return: A tuple with a status code and a dictionary.
    #     """
    #     # status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) \
    #     #     if hasattr(QNetworkRequest, 'HttpStatusCodeAttribute') \
    #     #     else None

    #     if hasattr(QNetworkRequest, 'HttpStatusCodeAttribute'):
    #         status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
    #     else:
    #         status_code = None

    #     try:
    #         response = bytes(reply.readAll()).decode()
    #         return status_code, json.loads(response) if response else None
    #     except (UnicodeDecodeError, JSONDecodeError, ValueError) as err:
    #         breakpoint()
    #         Logger.logException("e", "Could not parse response: %s", err)
    #         Logger.logException("e", response)
    #         return status_code, {"errors": [err]}

    # NOTE: disabled-function-logging because of "spam"
    def _parseModels(self,
                     response: Dict[str, Any],
                     on_finished: Union[Callable[[PGApiClientModel], Any], Callable[[List[PGApiClientModel]], Any]],
                     model_class: Type[PGApiClientModel]) -> None:
        """Parses the given models and calls the correct callback depending on the result.

        :param response: The response from the server, after being converted to a dict.
        :param on_finished: The callback in case the response is successful.
        :param model_class: The type of the model to convert the response to. It may either be a single record or a list.
        """
        if not response:
            return response

        try:
            if isinstance(response, list):
                results = [model_class(**c) for c in response]  # type: List[PGApiClientModel]
                on_finished_list = cast(Callable[[List[PGApiClientModel]], Any], on_finished)
                on_finished_list(results)
            else:
                result = model_class(**response)
                on_finished_item = cast(Callable[[PGApiClientModel], Any], on_finished)
                on_finished_item(result)
        except (JSONDecodeError, TypeError, ValueError) as e:
            Logger.log("e", "Could not parse response from network: %s", str(response))
            logger.exception(e)
            # TODO: It's a quickfix for a problem when there is some error-message but _addCallback doesn't recogize it.
            #         So it tries to call _parseModels but with data which which the model can't be created
            #         (e.g. TypeError: PGPrinterState.__init__() missing 2 required positional arguments: 'printerEmpty' and 'ready')
            # raise

    def _addCallback(self,
                     reply: QNetworkReply,
                     on_finished: Union[Callable[[PGApiClientModel], Any], Callable[[List[PGApiClientModel]], Any]],
                     model: Type[PGApiClientModel] = None,
                     on_error: Union[Callable[[PGApiClientModel], Any], Callable[[List[PGApiClientModel]], Any]] = None,
                     ) -> None:
        """Creates a callback function so that it includes the parsing of the response into the correct model.

        The callback is added to the 'finished' signal of the reply.
        :param reply: The reply that should be listened to.
        :param on_finished: The callback in case the response is successful.
        :param on_error custom error handler for cases where http error code is regular part of response
        """

        @pyqtSlot()
        def parse_func() -> None:
            # TODO: Find other way, then using such list
            self._anti_gc_callbacks.remove(parse_func)
            err = reply.error()

            status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

            if status_code != 200:
                read_all_result = reply.readAll()
                try:
                    response = json.loads(read_all_result.data()) if read_all_result else None
                    logger.error(response)
                    self._parseModels(response, on_error, model)
                    return
                except JSONDecodeError:
                    logger.error(
                        "Could not JsonDecode ErrorResponse from server. Response: {} - Error string: {}".format(
                            read_all_result,
                            reply.errorString()
                        )
                    )

            # This needs to be after status_code check. There are replies, with both, status_code error and NetworkError
            if err != QNetworkReply.NetworkError.NoError:
                # TODO: Show info in UI about network error
                logger.error(str(err))
                self._on_error(reply.errorString())
                return

            response = json.loads(r.data()) if (r := reply.readAll()) else None

            # If no parse model is given, simply return the raw data in the callback.
            if not model:
                on_finished(response)
                return

            # Otherwise parse the result and return the formatted data in the callback.
            # status_code, response = self._parseReply(reply)
            self._parseModels(response, on_finished, model)

        self._anti_gc_callbacks.append(parse_func)
        reply.finished.connect(parse_func)

    def getProductInfo(self, on_finished: Callable) -> None:
        """Get printer system information.

        :param on_finished: The callback in case the response is successful.
        """
        url = "{}/config/getProductInfo".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGProductInfo)

    # NOTE: disabled-function-logging because of "spam"
    def getStatus(self, on_finished: Callable) -> None:
        url = "{}/printer/printerstatus".format(self.PRINTER_API_PREFIX)
        # print()
        # print('----------------------------------------------------')
        # print('getStatus')
        reply = self._manager.get(self._createEmptyRequest(url))
        # reply = self._manager.get(QNetworkRequest(QUrl('http://localhost:8000/')))
        self._addCallback(reply, on_finished, PGPrinterStatus)

    def getFilePrintInfo(self, filename, on_finished: Callable):
        url = "{}/file/printinfo/{}".format(self.PRINTER_API_PREFIX, filename)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintInfo)

    def getRecentFiles(self, on_finished: Callable) -> None:
        """Get printer recent files.

        :param on_finished: The callback in case the response is successful.
        """
        url = "{}/file/recentFiles".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGRecentFile)

    def getMachineFiles(self, on_finished: Callable) -> None:
        """Get machine memmory files.

        :param on_finished: The callback in case the response is successful.
        """
        url = "{}/file/getprintfiles".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGMemoryFiles)

    def delete(self, on_finished: Callable, fileName: str, on_error: Callable):
        url = "{}/file/deleteFileFromGcode/{}".format(self.PRINTER_API_PREFIX, fileName)
        reply = self._manager.deleteResource(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintResult, on_error)

    def printFile(self, fileName: str, on_finished: Callable, on_error: Callable):
        url = "{}/file/printFile/{}".format(self.PRINTER_API_PREFIX, fileName)
        logger.debug(f'Requesting: {url}')
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintResult, on_error)

    def printFileForce(self, fileName: str, on_finished: Callable, on_error: Callable):
        url = "{}/file/printFileForce/{}".format(self.PRINTER_API_PREFIX, fileName)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintResult, on_error)

    def checkFile(self, fileName: str, on_finished: Callable):
        url = "{}/file/checkFile/{}".format(self.PRINTER_API_PREFIX, fileName)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGCheckFile, on_finished)

    # NOTE: disabled-function-logging because of "spam"
    def getEndInfo(self, on_finished: Callable):
        url = "{}/file/endInfo".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGEndInfo, on_finished)

    # NOTE: disabled-function-logging because of "spam"
    def getExtruders(self, on_finished: Callable):
        url = "{}/config/getExtruders/".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGExtruder)

    def pausePrint(self, on_finished: Callable, on_error: Callable):
        url = "{}/machine/pausePrint".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintOperationResult, on_error)

    def resumePrint(self, on_finished: Callable, on_error: Callable):
        url = "{}/machine/resumePrint".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintOperationResult, on_error)

    def cancelPrint(self, on_finished: Callable, on_error: Callable):
        url = "{}/machine/cancelPrint/force".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrintOperationResult, on_error)

    # NOTE: disabled-function-logging because of "spam"
    def getPlate(self, on_finished: Callable, on_error: Callable):
        url = "{}/config/getUsedPlate".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPlate, on_error)

    # NOTE: disabled-function-logging because of "spam"
    def getPrinterState(self, on_finished: Callable, on_error: Callable):
        url = "{}/config/printerState".format(self.PRINTER_API_PREFIX)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, PGPrinterState, on_error)

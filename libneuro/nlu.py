from abc import ABCMeta, abstractmethod
from typing import Any, List, Dict, Optional, Type, Union

NoneStrList = Union[None, str, List[str]]


class NeuroNluRecognitionRequest:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, entities=None, intents=None):
        self._entities = entities
        self._intents = intents

    @abstractmethod
    def check_entity(self, entity_name):
        pass

    @abstractmethod
    def has_entities(self):
        pass

    @abstractmethod
    def set_entities(self, entities: (str, list)):
        pass

    @abstractmethod
    def check_intent(self, intent_name):
        pass

    @abstractmethod
    def has_intents(self):
        pass

    @abstractmethod
    def set_intents(self, intents: (str, list)):
        pass


class NeuroNluRecognitionResult:

    @abstractmethod
    def __init__(self):
        self._utterance = None
        self._entities = {}
        self._intents = {}

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __bool__(self):
        pass

    @abstractmethod
    def utterance(self) -> Union[None, str]:
        """ Возвращает подготовленный и исправленный текст (после обработки exceptions) """
        pass

    @abstractmethod
    def entity(self, entity_name: str) -> Union[None, str]:
        """ Возвращает значение распознанной сущности или None """
        pass

    @abstractmethod
    def intent(self, intent_name: str) -> Union[None, str]:
        """ Возвращает значение распознанного интента или None """
        pass

    @abstractmethod
    def has_entity(self, entity_name) -> bool:
        """ Проверяет существование указанной сущности """
        pass

    @abstractmethod
    def has_entities(self) -> bool:
        """ Проверяет существование хотя бы одной любой сущности """
        pass

    @abstractmethod
    def has_intent(self, intent_name) -> bool:
        """ Проверяет существование указанного интента """
        pass

    @abstractmethod
    def has_intents(self) -> bool:
        """ Проверяет существование хотя бы одного интента """
        pass

    @abstractmethod
    def set_utterance(self, utterance: str):
        """ внутренний метод """
        pass

    @abstractmethod
    def update_entities(self, entities: dict):
        """ внутренний метод """
        pass

    @abstractmethod
    def update_intents(self, intents: dict):
        """ внутренний метод """
        pass

    @abstractmethod
    def dump(self) -> dict:
        """ возвращает словарь с распознанными сущностями """
        pass

    @abstractmethod
    def dump_json(self) -> str:
        """ возвращает строку в JSON формате с распознанными сущностями """
        pass


class NeuroNluLibrary:

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def extract(self, recognition_result: str,
                entities: NoneStrList = None, entities_exclude: NoneStrList = None,
                intents: NoneStrList = None, intents_exclude: NoneStrList = None,
                context=None, use_neuro_api=False
                ) -> NeuroNluRecognitionResult:
        """ Получение сущностей и интентов из строки

        Описание аргументов:
        :param str recognition_result: строка для распознавания сущностей
        :param entities: список сущностей, в которых нужно делать поиск.
                                           Строка, через запятую (entity1, entity2) или list ['entity1', 'entity2']
        :param entities_exclude: если указан, то поиск будет по всем сущностям, кроме этого списка,
                           Перекрывает параметр entities
        :param intents: список интентов, в которых нужно делать поиск
        :param intents_exclude: если указан, то поиск будет по всем интентам, кроме этого списка,
                           Перекрывает параметр intents
        :param context: Строка контекста для Nlu API (используется совместно с use_neuro_api=True)
        :param use_neuro_api: если True, то для определения сущностей будет задействован Nlu Api.
                              Сущности найденные через Nlu Api не будут определяться по паттернам.

        :return NeuroNluRecognitionResult: Объект класса NeuroNluRecognitionResult
        """
        pass

    @abstractmethod
    def extract_address(self, address: str) -> Dict[str, List[Optional[str]]]:
        """ Получение структуры адреса из строки

        Описание аргументов:
        :param address: строка для распознавания
        :return dict: Словарь с ключами {'city': [...], 'street': [...], 'building': [...], 'appartment': '...'}
        """
        pass

    @abstractmethod
    def extract_person(self, person: str) -> Dict[str, Optional[str]]:
        """ Получение структуры имени из строки

        Описание аргументов:
        :param person: строка для распознавания
        :return dict: Словарь с ключами {'first': '...', 'last': '...', 'middle': '...'}
        """
        pass

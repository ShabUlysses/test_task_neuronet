from abc import ABCMeta, abstractmethod
from datetime import datetime
from uuid import UUID
from typing import Any, List, Dict, Optional, Type, Union


class DialogEnumResult:
    CREATED = None
    QUEUED = 'queued'
    PENDING = 'pending'
    DONE = 'done'


class DialogAttributes:
    __metaclass__ = ABCMeta

    def __init__(self, nlu_dialog):
        self.__nlu_dialog = nlu_dialog

    @property
    @abstractmethod
    def entry_point(self) -> str:
        if 'params' in self.__nlu_dialog and isinstance(self.__nlu_dialog['params'], dict) and 'entry_point' in self.__nlu_dialog['params']:
            return self.__nlu_dialog['params']['entry_point']
        return ''

    @entry_point.setter
    @abstractmethod
    def entry_point(self, value):
        if not isinstance(self.__nlu_dialog['params'], dict):
            self.__nlu_dialog['params'] = {}
        self.__nlu_dialog['params']['entry_point'] = value

    @property
    @abstractmethod
    def result(self) -> str:
        if 'result' in self.__nlu_dialog:
            return self.__nlu_dialog['result']
        return ''

    @result.setter
    @abstractmethod
    def result(self, value):
        self.__nlu_dialog['result'] = value

    @property
    @abstractmethod
    def msisdn(self) -> str:
        if 'msisdn' in self.__nlu_dialog:
            return self.__nlu_dialog['msisdn']
        return ''

    @msisdn.setter
    @abstractmethod
    def msisdn(self, *args):
        raise ValueError('Can not change dialog property msisdn')

    def __iter__(self):
        for key in 'msisdn', 'entry_point', 'result':
            yield key, getattr(self, key)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

    def __str__(self):
        return str(dict(self))


class NeuroNetLibrary:
    __metaclass__ = ABCMeta
    RESULT_CREATED = DialogEnumResult.CREATED
    RESULT_PENDING = DialogEnumResult.PENDING
    RESULT_QUEUED = DialogEnumResult.QUEUED
    RESULT_DONE = DialogEnumResult.DONE

    @property
    @abstractmethod
    def dialog(self) -> dict:
        """ Получение данных о диалоге, сам диалог доступен в виде атрибута nn.dialog
        Пример:
        GET:
        nn.dialog -> {'msisdn': '...', 'entry_point': '...', 'result'}

        SET:
        nn.dialog['entry_point'] = 'main_failed'
        nn.dialog['result'] = 'done'
        """

        dialog_attributes = DialogAttributes({'msisdn': 'msisdn',
                                              'params': {'entry_point': 'entry_point'},
                                              'result': 'result'})
        return {'msisdn': dialog_attributes.msisdn,
                'entry_point': dialog_attributes.entry_point,
                'result': dialog_attributes.result}

    @dialog.setter
    @abstractmethod
    def dialog(self, *args):
        raise ValueError('Can not change dialog property')

    @abstractmethod
    def env(self, *args: Union[None, str, Dict[str, Union[None, str]]], **kwargs)\
            -> Union[None, str, Dict[str, Union[None, str, datetime, bool, int, float]]]:
        """ Установка / удаление / получение значений переменных окружения
        :param args: установка / получение ключей
        :param args: установка заданных ключей

        Примеры
        val = nn.env('key') # получение значения val у ключа key
        vals = nn.env() # получение всех переменных окружений в виде словаря
        nn.env('key', 'val') # установка значения val для ключа key
        nn.env('key', None) # удаление переменной key
        nn.env({'key1': 'val1', 'key2': 'val2'}) # установка нескольких значений используя словарь
        nn.env(key1='val1', key2='val2') # тоже самое, но ввиде передачи именованных аргументов

        """
        pass

    @abstractmethod
    def storage(self, *keys: str) -> Union[None, str, Dict[str, str]]:
        """ Получение значений пользовательских данных

        Аргументы:
        :param keys: один или несколько ключей, для получения значений
        :return: возвращает значение или словарь значений у выбранных ключей keys

        Пример:
        voice = nn.storage('voice') # получение одного ключа
        params = nn.storage('voice', 'lang') # получение нескольких значений, результат словарь

        Если ключа не существует, для него вернется None
        """
        pass

    @abstractmethod
    def counter(self, name, op=None):
        """ Получение / изменение счетчика

        Аргументы:
        :param name: название счетчика
        :param op: операция (+ или -)
        :return int: возвращает текущеее значения счетчика, потом производит операцию op

        Пример:
        counter_hello1 = nn.counter('hello') # получение значения счетчика hello, 0
        counter_hello2 = nn.counter('hello', '+') # возврат текущего значения 0, затем изменение счетчика на 1
                                                  # в данном случае counter_hello2 == counter_hello1 == 0

        counter_hello3 = nn.counter('hello', '-') # возврат текущего значения 1, затем изменение счетчика на -1
        counter_hello3 = nn.counter('hello') # 0

        # вариант использования с if
        if nn.counter('hello_null', '+') >= 1:
            return hello_default()
        return hello_null()

        """
        pass

    @abstractmethod
    def has_record(self, name: str, value: Union[str, None] = None) -> bool:
        """ Проверяет наличие записей фраз и сущностей в базе агента

        Аргументы:
        :param name: наименование промпта или сущности
        :param value: значение (если передано, будет проверяться сущность)

        Пример:
        if nv.has_record('hello_rights'):
            nv.say('hello_rights')

        if nv.has_record('entity_name', nn.env('name')):
            nv.say('entity_name', nn.env('name'))

        """
        pass

    @abstractmethod
    def has_records(self, *args: (str, list, dict), **kwargs: (str, list)):
        """ Проверка нескольких записей (фраз и сущностей) в базе агента
            Для проверки используется flag = nn.env('flag') и lang = dialog.params.lang

            Для проверки обычной фразы, нужно передать list или args из названий
            Для проверки сущностей, нужно передать Dict(name: value) в list или args или использовать kwargs
                если нужно проверить несколько значений у одной и той же сущности,
                то нужно передать в качестве значения list из значений, пример: entity_name=['val1', 'val2']

        Аргументы:
        :param *args: список из названий фраз (str) или сущностей со значениями (dict)
        :param **kwargs: сущности (название=значение)
        """
        pass

    @abstractmethod
    def call(self, msisdn: str, date: (datetime, str) = None, channel: str = None, script: (str, UUID) = None,
             entry_point: str = None,
             transport: str = 'sip', on_success_call: Union[None, str] = None, on_failed_call=None,
             use_default_prefix=False,
             proto_additional: dict=None, priority: int=None):
        """ Запланировать звонок в очередь

        Аргументы:
        :param msisdn: номер куда позвонить
        :param date: дата когда позвонить, если дата <= текущего времени, звонок будет запущен сразу.
               Такое же поведение, если не передать совсем (default None)
        :param channel: название канала, через который совершается звонок,
                  канал должен быть указан в CMS и доступен текущему агенту.
                  Если не указать, будет использоваться текущий канал или канал по-умолчанию (default None)
        :param script: название или UUID скрипта логики, если не указан, используется текущий (default None)
        :param entry_point: названии функции (точки входа), с которой будет запущен скрипт script, (default main)
        :param transport: голосовй транспорт, для звонков пока что используется только sip (default 'sip')
        :param on_success_call: смена точки входа после успешного звонка (default None)
        :param on_failed_call: смена точки входа после неудачного звонка или недозвона (default None)
        :param use_default_prefix: подставлять префикс транка в начало номера (default False)
        :param proto_additional: дополнительные хедеры, которые будут переданы в INVITE, где
                ключ, значение - имя и содержимое хедера соответственно
        :param priority: приоритет звонка

        Пример:
        nn.call(msisdn,
               '2020-05-20 14:20:00',
                entry_point='main_online',
                on_success_call='main_success',
                on_failed_call='main_failed')

        nn.call('89290507046', '01:00:00')  # перезвонить через час
        nn.call('89290507046', '02:00')  # через 2 часа

        nn.call('89290507046', '01:00:00')  # перезвонить через час
        nn.call('89290507046', '2020-05-20 14:20:00')  # через 2 часа
        nn.call('89290507046',
                proto_additional={"P-Asserted-Identity":"<tel:88005553535>"})  # добавить PAI в INVITE

        # Добавить префикс транка перед номером
        nn.call('9290507046', use_default_prefix=True)  # если у транка префикс 8,
                                                        # то звонок будет на 89290507046
        """
        pass

    @abstractmethod
    def send_sms(self, dest_number: str, text: str, channel: str):
        """ Отправка SMS

        Аргументы:
        :param str dest_number: номер, кому отправляем сообщение
        :param str text: текст сообщения
        :param str channel: канал (транспорт)

        Пример:
        nn.send_sms(msisdn, 'Hello World', 'ispirin_test_client')
        """
        pass

    @abstractmethod
    def log(self, *args):
        """ Логирование данных в лог теущего диалога или звонка

        Если передан 1 аргумент, то
            :name = None
            :data = args[0]
        Если передано 2 аргумента, то
            :name = args[0]
            :data = args[1]

        Параметр :data будет преобразован в строку автоматически

        Примеры:
        запись длительности звонка
        nn.log('duration', nv.get_call_duration())
        -> dialog_stats.action='nn.log', dialog_stats.name='duration', dialog_stats.data='...'

        запись транскрипции звонка
        nn.log('transcription', nv.get_call_transcription(return_format=nv.TRANSCRIPTION_FORMAT_TXT))
        -> dialog_stats.action='nn.log', dialog_stats.name='transcription', dialog_stats.data='...'

        запись результата распознавания
        nn.log('---- recognition result, utterance: %s, entity hello_confirm: %s, intent callback: %s  ----' % (
               r.utterance(), r.entity('hello_confirm'), r.intent('callback')
           ))
        -> ---- recognition result, utterance: None, entity hello_confirm: true, intent callback: false  ----
        """
        pass

    @abstractmethod
    def dump(self):
        """ Дамп сущностей в dialog_stats из nn.env, указанных в output_entities
        Пример:
        <- output_entities = ['name', 'call_result'] # берутся из CMS агента

        nn.env('name', 'Антон')
        nn.env('call_result', 'Сброс на приветствие')

        nn.dump()
        -> dialog_stats.action='nn.dump',
           dialog_stats.name='output_data',
           dialog_stats.data='{"name": "Антон", "call_result": "Сброс на приветствие"}'
        """
        pass

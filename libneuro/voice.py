from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import Any, List, Dict, Tuple, Optional, Type, Union
from uuid import UUID
NoneStrList = Union[None, str, List[str]]


@abstractmethod
def check_call_state():
    """ Декоратор для проверки статуса звонка в пользовательских функциях.

    Бросает исключение InvalidCallStateError в случае, если звонок завершается.
    Пропускает экшены, если звонок не в статусе RUNNING.
    :throws InvalidCallStateError
    """
    pass


class NeuroVoiceLibrary:
    __metaclass__ = ABCMeta

    TRANSCRIPTION_FORMAT_RAW = 'raw'
    TRANSCRIPTION_FORMAT_TXT = 'txt'

    @abstractmethod
    def get_call_duration(self) -> int:
        """ Получает текущую длительность звонка """
        pass

    @abstractmethod
    def get_call_transcription(self, return_format: str = TRANSCRIPTION_FORMAT_RAW) -> Union[List[Dict[str, str]], str]:
        """ Возвращает текущую транскрипцию звонка в виде текста или словаря

        :param return_format: формат для вывода (nv.TRANSCRIPTION_FORMAT_RAW или nv.TRANSCRIPTION_FORMAT_TXT)

        Пример:
        transcription = nv.get_call_transcription()
        print(transcription)
        -> [{"type": "bot", "message": "hello_main"},
            {"type": "human", "message": "да привет"},
            {"type": "bot", "message": "подключить нашу услугу ?"},
            {"type": "human", "message": "я согласен"}]

        transcription = nv.get_call_transcription(nv.TRANSCRIPTION_FORMAT_TXT)
        nn.log('transcription', transcription)
        -> nn.log	transcription   bot: hello_main; human: да привет; bot: подключить нашу услугу ?; human: я согласен

        """
        pass

    @abstractmethod
    def media_params(self, *args: Union[Dict[str, str], str]) -> None:
        """ Получает / обновляет параметры медиа сервера
        (flag, asr движок, tts движок, креды asr / tts)

        Пример:
        lang = nv.media_params('lang')  # ru-RU

        nv.media_params('lang', 'en-US')  # changed to en-US
        nv.media_params('flag', 'test')  # changed to test

        nv.media_params({'lang': 'en-US', 'flag': 'test'})  # changed lang and flag

        """

        pass

    @abstractmethod
    def set_default(self, section, *args: Union[Dict[str, Union[str, int]], str, int], **kwargs) -> None:
        """ Устанавливает настройки по умолчанию для функций.

        :param section: название команды, для которой применяются настройки по-умолчанию
        :param args: параметры с настройками словарь или 2 строки (ключ, значение)
        :param kwargs: параметры с настройками (сработает, если не указан args)

        Пока работает только для nv.listen и nv.random_sound

        Пример:
        nv.set_default('listen', no_input_timeout=4000, recognition_timeout=30000,
        speech_complete_timeout=1500, asr_complete_timeout=2500)

        nv.set_default('random_sound', min_delay=2000, max_delay=10000)

        nv.set_default('listen', {'no_input_timeout': 4000, 'recognition_timeout': 30000,
           'speech_complete_timeout': 1500, 'asr_complete_timeout': 2500})
        """
        pass

    @abstractmethod
    def get_default(self, section) -> Dict[str, Union[int, str]]:
        """ Получает настройки по-умолчанию для функций
        :param section: секция с настройками

        Пример:
        listen_options = nv.get_default('listen')
        print(listen_options)
        -> {'no_input_timeout': 4000, 'recognition_timeout': 30000,
           'speech_complete_timeout': 1500, 'asr_complete_timeout': 2500}
        """
        pass

    @abstractmethod
    def say(self, name: str, value: Union[str, None] = None) -> None:
        """ Проигрывает промпты (обычные и с сущностями)
        :param name: наименование промпта или сущности
        :param value: значение для проигрывания сущности

        Если не указано value, то проигрывается обычный промпт, если указано – промпт с сущностью.
        Для проигрывания промпта учитывается текущий параметр nn.env('flag')

        Пример:
        nv.say('hello_rights')  # playback prompt hello_rights

        org = nn.env('org')
        nv.say('org', org)  # playback entity org with value env['org']
        nv.say('what_doing', org)  # playback entity what_doing with value env['org']

        """
        pass

    @abstractmethod
    def background(self, name: Union[str, None]):
        """ Включить / выключить проигрывание фоновой музыки
        :param name: название фоновго файла из CMS.
                     Если None, проигрывание остановится

        Файл будет зациклен и проигрываться по кругу.

        Пример:
        nv.background('office_noise')  # включить офисный шум
        nv.background(None)  # выключить
        """
        pass

    @abstractmethod
    def template_synthesize(self, template_audio_file, template_text, replacement_text_list):
        """Кастомный синтез речи
        :param template_audio_file: имя файла шаблона для передачи в Яндекс
        :param template_text: транскрипция файла шаблона
        :param replacement_text_list: элементы для замены в шаблоне

        Пример:
        nv.template_synthesize('template_audio.s16le-ac1-ar8000.raw',
                               'Добрый день {name}. Адрес доставки: {address}. Все верно?',
                               {
                                   'address': 'г. Нижний Новгород, ул. Комарова, д.13, кв.182',
                                   'name': 'Анатолий'}
        """
        pass

    @abstractmethod
    def synthesize(self, text: str, ssml: bool = False):
        """ Проиграть речь из текста (TTS)
        :param text: текст для синтеза
        :param ssml: Если True будет использован язык разметки SSML

        Настройки для проигрывания (движок, голос), берутся из:
        - текущих параметров nv.media_params('tts'), nv.media_params('lang')
        - текущих параметров диалога dialog.params ('tts', 'language')
        - у агента по-умолчанию (agent.tts, agent.language)
        Аутентификация (креды) из настройки CMS.

        Пример:
        nn.env('name', 'Антон Палыч')
        nv.synthesize(f'Приветствую вас {nn.env["name"]}. Я ваш виртуальный помощник')
        -> Приветствую вас Антон Палыч. Я ваш виртуальный помощник
        """
        pass

    @abstractmethod
    def random_sound(self, min_delay: Union[None, int], max_delay: Union[None,int]):
        """ Включение проигрывания случайных звуков из раздела CMS Звуки
        :param min_delay - минимальное кол-во миллисекунд, после которых начнется запуск команды
        :param max_delay - максимальное кол-во миллисекунд, до которых будет запуск команды

        Проигрывает рандомный звук в рандомное время от min_delay до max_delay.
        По-умолчанию берутся настройки из nv.get_default('random_sound')
        Если отсутствует одна из настроек в nv.get_default или аргументах, будет ошибка
        """
        pass

    @abstractmethod
    def bridge(self, uri: str, channel: str = None, **kwargs):
        """ Соединить абонента с другим номером или sip_uri

        :param str uri: кому позвонить (msisdn или sip_uri)
        :param channel: канал, через который звонить, None – текущий (по-умолчанию)
        :param \**kwargs: дополнительные аргументы функции bridge, см. ниже

        :Keyword Arguments:
            * proto_additional (dict) -- дополнительные хедеры, которые будут переданы в INVITE, где
              ключ, значение - имя и содержимое хедера соответственно

        Пример:
        nv.bridge('1234567890', 'mtt')  # соединить с номером 1234567890 через канал mtt
        nv.bridge('1234567890@sip.mtt.ru')  # соединить с sip
        nv.bridge('1234567890@sip.mtt.ru', proto_additional={"P-Asserted-Identity": "<tel:88005553535>"})

        """
        pass

    @abstractmethod
    def hangup(self):
        """ Положить трубку и сбросить звонок.

        Пример:
        nv.hangup()
        """
        pass

    @abstractmethod
    def exec_after(self, sec: int, func, *args, **kwargs):
        """ Запуск команды, через определенное время
        :param sec: кол-во микросекунд, через которое будет запуск команды
        :param func: функция, которая будет запущена
        :param args: аргументы, будут проброшены в функцию
        :param kwargs: key value аргументы, будут проброшены в функцию

        nv.exec_after(60, nv.hangup)  # сброс звонка через 60 сек
        nv.exec_after(60, nv.say, 'goodbye')  # сказать "пока" через 60 сек
        """
        pass

    @abstractmethod
    def detect_speech_start(self, detect_policy=None,
                            entities=None, entities_exclude=None,
                            intents=None, intents_exclude=None,
                            context=None, use_neuro_api=False,
                            **kwargs):
        """ see nv.listen  """
        pass


    @abstractmethod
    def hold_and_call(self, msisdn: str,  channel: str = None,
                      script: (str, int, UUID) = None, entry_point: str = None,
                      transport: str = 'sip',
                      use_default_prefix=False):
        """ Создание второго звонка из родительского звонка
        Аргументы:
        :param msisdn: номер куда позвонить

        :param channel: название канала, через который совершается звонок,
                  канал должен быть указан в CMS и доступен текущему агенту.
                  Если не указать, будет использоваться текущий канал или канал по-умолчанию (default None)
        :param script: название или UUID скрипта логики, если не указан, используется текущий (default None)
        :param entry_point: названии функции (точки входа), с которой будет запущен данный звонок, (default main)
        :param transport: голосовй транспорт, для звонков пока что используется только sip (default 'sip')
        :param use_default_prefix: подставлять префикс транка в начало номера (default False)

        Изначально родительский и дочерний звонок имеют разную логику.
        Для безусловного соединения дочернего звонка с родителем в enty_point дочернего звонка должен быть вызван метод bridge_to_caller
        """
        pass

    @abstractmethod
    def bridge_to_caller(self):
        """ Метод выполняет непосредственное соединение двух звонков.
          Используется совместо с методом hold_and_call
          Метод должен быть вызван из звонка, который создается с помощью метода hold_and_call,
          потому что звонок, созданный с помощью Hold_and_call знает uuid родительского звонка"""
        pass


    @abstractmethod
    def detect_speech_stop(self):
        """ see nv.listen  """
        pass

    @contextmanager
    @abstractmethod
    def listen(self, detect_policy: Union[Tuple[NoneStrList, NoneStrList], str, int, list, None] = None,
               entities: NoneStrList = None, entities_exclude: NoneStrList = None,
               intents: NoneStrList = None, intents_exclude: NoneStrList = None,
               context=None, use_neuro_api=False,
               **kwargs):
        """ Запускает контекст для распознавания сущностей и интентов
        :param detect_policy: правила для остановки проигрывания любого аудио потока
               Tuple(search_entities:(None, str,list),  # срабатывание при поиске одной из сущностей
                    search_intents:(None, str, list),  # срабатывание при поиске одного из интентов
                    characters_count: (None,int),  # срабатывание по кол-ву распознанных символов
                    operator:str = 'OR|AND  # правила для оператор И / ИЛИ
                    )
               # укороченный синтаксис для поиска по сущностям
               search_entities:(str,list) – Tuple(search_entities, None, None, 'AND')
               # укороченный синтаксис для поиска по кол-ву символов
               characters_count:int - Tuple(None, None, characters_count, 'AND')

               По-умолчанию None – не останавливать аудио.
               Эти аргументы распаковываются и пробрасываются в функцию nv.speech_input_detector
        :param entities: список сущностей, среди которых будет поиск для распознавания
        :param entities_exclude: наоборот, поиск среди всех сущностей, кроме указанных
                                 (перекрывает настройку entities)
        :param intents: список интентов, среди которых будет поиск для распознавания
        :param intents_exclude: наоборот, поиск среди всех интентов, кроме указанных
                                 (перекрывает настройку intents)
        :param context: Строка контекста для Nlu API (используется совместно с use_neuro_api=True)
        :param use_neuro_api: если True, то для определения сущностей будет задействован Nlu Api.
                              Сущности найденные через Nlu Api не будут определяться по паттернам.

        :param kwargs: настройки распознавания, по-умолчанию берутся из nv.get_default('listen')

        :return nlu.NeuroNluRecognitionResult: сразу возвращает объект с результатом распознавания,
                                                который будет заполнятся в процессе

        Внутри контекста параллельно можно выполнять другие экшены, например nv.say(...)
        Запрещается запускать nv.listen внутри nv.listen, будет ошибка

        Пример:
        with(nv.listen(60, entities='hello,bye,busy', intents='confirm')) as r:
            nv.say('hello')

        if r.has_entity('busy'):
           nv.say('goodbye_sorry')
           nv.hangup()
           return
        """
        pass

    @staticmethod
    @abstractmethod
    def speech_input_detector(recognition_result: str,
                              found_entities: list,
                              found_intents: list,
                              *args) -> bool:
        """ Переопределить функцию для остановки проигрывания

        :param recognition_result: распознанная строка
        :param found_entities: найденные сущности
        :param found_intents: найденные интенты
        :param args: проброшенные аргументы из detect_policy

        Пример

        def my_speech_input_detector(utterance: str,
                              found_entities: list,
                              found_intents: list,
                              *args) -> bool:
            if ...:
               return True
            return False
        nv.speech_input_detector = my_speech_input_detector
        """
        pass


class InvalidCallStateError(BaseException):
    pass


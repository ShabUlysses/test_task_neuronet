from libneuro import NeuroNetLibrary as nn
from libneuro import NeuroNluLibrary as nlu
from libneuro import NeuroVoiceLibrary as nv
from libneuro import check_call_state


# hello unit

@check_call_state()
def hello_main():
    nv.set_default('listen', no_input_timeout=4000, recognition_timeout=30000,
                   speech_complete_timeout=1500, asr_complete_timeout=2500)
    nn.log('unit', 'start_call')
    with nv.listen((None, None, 500, 'AND'), entities=['yes', 'no', 'wrong_time', 'repeat']) as r:
        pass
    return hello_logic(r)


@check_call_state()
def hello():
    nn.log('unit', 'recommend_main')
    nv.say('recommend_main')
    return hello_main()


@check_call_state()
def hello_repeat():
    nn.log('unit', 'hello_repeat')
    nv.say('hello_repeat')
    return hello_main()


@check_call_state()
def hello_null():
    hello_null_counter = nn.counter('hello_null', '+')
    if hello_null_counter >= 1:
        return hangup_null()
    nn.log('unit', 'hello_null')
    nv.say('hello_null')
    return hello_main()


# main unit
def play_main():
    nv.set_default('listen', no_input_timeout=4000, recognition_timeout=30000,
                   speech_complete_timeout=1500, asr_complete_timeout=2500)
    nn.log('unit', 'play_main')
    with nv.listen((None, None, 500, 'AND'),
                   entities=['yes', 'no', 'neutral', 'repeat', 'dont_know', 'wrong_time', 'question', 'positive_score',
                             'negative_score']) as r:
        pass
    return main_logic(r)


@check_call_state()
def recommend_main():
    nn.log('unit', 'recommend_main')
    nv.say('recommend_main')
    return play_main()


@check_call_state()
def recommend_repeat():
    nn.log('unit', 'recommend_repeat')
    nv.say('recommend_repeat')
    return play_main()


@check_call_state()
def recommend_repeat_2():
    nn.log('unit', 'recommend_repeat_2')
    nv.say('recommend_repeat_2')
    return play_main()


@check_call_state()
def recommend_score_negative():
    nn.log('unit', 'recommend_score_negative')
    nv.say('recommend_score_negative')
    return play_main()


@check_call_state()
def recommend_score_neutral():
    nn.log('unit', 'recommend_score_neutral')
    nv.say('recommend_score_neutral')
    return play_main()


@check_call_state()
def recommend_score_positive():
    nn.log('unit', 'recommend_score_positive')
    nv.say('recommend_score_positive')
    return play_main()


@check_call_state()
def recommend_null():
    recommend_null_counter = nn.counter('recommend_null', '+')
    if recommend_null_counter >= 1:
        return hangup_null()
    nn.log('unit', 'hello_null')
    nv.say('hello_null')
    return hello_main()


@check_call_state()
def recommend_default():
    recommend_default_counter = nn.counter('recommend_default', '+')
    if recommend_default_counter >= 1:
        return hangup_null()
    nv.say('recommend_default')
    return play_main()


# hangup unit

@check_call_state()
def hangup_positive():
    nn.log('unit', 'hangup_positive')
    nv.say('hangup_positive')
    nv.hangup()
    return


@check_call_state()
def hangup_negative():
    nn.log('unit', 'hangup_negative')
    nv.say('hangup_negative')
    nv.hangup()
    return


@check_call_state()
def hangup_wrong_time():
    nn.log('unit', 'hangup_wrong_time')
    nv.say('hangup_wrong_time')
    nv.hangup()
    return


@check_call_state()
def hangup_null():
    nn.log('unit', 'hangup_null')
    nv.say('hangup_null')
    nv.hangup()
    return


# forward unit
@check_call_state()
def forward():
    nv.say('forward')
    nv.bridge('operator')
    return


# logic unit

@check_call_state()
def hello_logic(r):
    hello_logic_count = nn.counter('hello_logic', '+')
    if hello_logic_count >= 10:
        nn.log('Recursive callback detected')
        nv.say('hangup_wrong_time')
        nv.hangup()
        return

    nn.log('unit', 'hello_logic')
    if not r:
        nn.log('condition', 'NULL')
        return hello_null()

    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        return recommend_main()

    if r.has_entity('repeat'):
        nn.log('condition', 'repeat=True')
        return hello_repeat()

    if r.has_entity('yes'):
        nn.log('condition', 'confirm=True')
        return recommend_main()

    if r.has_entity('no'):
        nn.log('condition', 'confirm=False')
        return hangup_wrong_time()

    if r.has_entity('wrong_time'):
        nn.log('condition', 'wrong_time=True')
        return hangup_wrong_time()


@check_call_state()
def main_logic(r):
    main_logic_count = nn.counter('main_logic', '+')
    if main_logic_count >= 10:
        nn.log('Recursive callback detected')
        nv.say('hangup_wrong_time')
        nv.hangup()
        return

    nn.log('unit', 'main_logic')
    if not r:
        nn.log('condition', 'NULL')
        return recommend_null()

    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        return recommend_default()

    if r.has_entity('positive_score'):
        nn.log('condition', 'recommendation_score=positive_score')
        return hangup_positive()

    if r.has_entity('negative_score'):
        nn.log('condition', 'recommendation_score=negative_score')
        return hangup_negative()

    if r.has_entity('yes'):
        nn.log('condition', 'recommendation=positive')
        return recommend_score_positive()

    if r.has_entity('neutral'):
        nn.log('condition', 'recommendation=neutral')
        return recommend_score_neutral()

    if r.has_entity('no'):
        nn.log('condition', 'recommendation=negative')
        return recommend_score_negative()

    if r.has_entity('repeat'):
        nn.log('condition', 'repeat=True')
        return recommend_repeat()

    if r.has_entity('dont_know'):
        nn.log('condition', 'recommendation=dont_know')
        return recommend_repeat_2()

    if r.has_entity('wrong_time'):
        nn.log('condition', 'wrong_time=True')
        return hangup_wrong_time()

    if r.has_entity('question'):
        nn.log('condition', 'question=True')
        return forward()


if __name__ == '__main__':
    nn.call('+7XXXXXXXXXX', '2022-02-23 12:00:00', entry_point='hello')

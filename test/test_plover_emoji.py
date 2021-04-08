import sys
sys.path.append('..')
from plover_emoji import (
    unicode_output_to_characters,
    get_emoji,
    find_emoji_by_phrase,
    get_emoji_phrase,
    normalize,
)

def test_normalize():
    assert normalize('Clock430') == '430 clock'
    assert normalize('kissing heart') == 'heart kissing'
    assert normalize('clock 4:30') == '430 clock'

def test_unicode_output_to_characters():
    assert unicode_output_to_characters('1f605') == '😅'
    assert unicode_output_to_characters('270a-1f3fe') == '✊🏾'
    assert unicode_output_to_characters('1f468-200d-1f469-200d-1f466-200d-1f466') == '👨‍👩‍👦‍👦'

def test_get_emoji():
    assert get_emoji(normalize('grinning face with sweat')) == '1f605'

    assert get_emoji(normalize('sweat smile')) == '1f605'
    assert get_emoji(normalize('family man woman boy boy')) == '1f468-200d-1f469-200d-1f466-200d-1f466'
    assert get_emoji(normalize('family mwbb')) == '1f468-200d-1f469-200d-1f466-200d-1f466'

def test_unicode_13():
    assert get_emoji(normalize('ninja')) == '1f977'

def test_find_emoji_by_phrase_success():
    assert find_emoji_by_phrase('I had a sweat smile') == ('😅', 'sweat smile')
    assert find_emoji_by_phrase('she was a woman police officer') == ('👮‍♀️', 'woman police officer')
    assert find_emoji_by_phrase('she was a woman police officer tone 1') == ('👮🏻‍♀️', 'woman police officer tone 1')
    assert find_emoji_by_phrase('haha ok hand tone 3') == ('👌🏽', 'ok hand tone 3')
    assert find_emoji_by_phrase('I need to poop') == ('💩', 'poop')
    assert find_emoji_by_phrase('Don\'t drop your wine glass') == ('🍷', 'wine glass')
    assert find_emoji_by_phrase('lol that was so funny joy') == ('😂', 'joy')
    assert find_emoji_by_phrase('omg I am crying laughing') == ('😆', 'laughing')
    assert find_emoji_by_phrase('time for coffee') == ('☕', 'coffee')
    assert find_emoji_by_phrase('some cool kissing heart') == ('😘', 'kissing heart')
    assert find_emoji_by_phrase('pop some ta-da') == ('🎉', 'ta-da')
    assert find_emoji_by_phrase('pop some confetti') == ('🎊', 'confetti')
    assert find_emoji_by_phrase('I have a family woman woman boy') == ('👩‍👩‍👦', 'family woman woman boy')
    assert find_emoji_by_phrase('grin') == ('😁', 'grin')
    assert find_emoji_by_phrase('dog') == ('🐶', 'dog')
    assert find_emoji_by_phrase('dog 2') == ('🐕', 'dog 2')
    assert find_emoji_by_phrase('dog face') == ('🐶', 'dog face')
    assert find_emoji_by_phrase('stuck out tongue') == ('😛', 'stuck out tongue')
    assert find_emoji_by_phrase('canada') == ('🇨🇦', 'canada')
    assert find_emoji_by_phrase('metal') == ('🤘', 'metal')
    assert find_emoji_by_phrase('v') == ('✌️', 'v')
    assert find_emoji_by_phrase('victory hand') == ('✌️', 'victory hand')
    assert find_emoji_by_phrase('okay hand') == ('👌', 'okay hand')
    assert find_emoji_by_phrase('what time is clock 4') == ('🕓', 'clock 4')
    assert find_emoji_by_phrase('guess what time it is clock 4:30') == ('🕟', 'clock 4:30')
    assert find_emoji_by_phrase('one-two punch punch') == ('👊', 'punch')
    assert find_emoji_by_phrase('he made a hand signal sign of the horns') == ('🤘', 'sign of the horns')
    assert find_emoji_by_phrase('I must not see no evil') == ('🙈', 'see no evil')
    assert find_emoji_by_phrase('in our house we have boy girl man man family') == ('👨‍👨‍👧‍👦', 'boy girl man man family')

    # Too far from the name:
    assert find_emoji_by_phrase('some cool heart eyes kissing') == ('😗', 'kissing')

def test_shortnames_have_priority():
    """
    We want shortnames (like :sunglasses:) to take priority over names (like :dark_sunglasses:, a.k.a. sunglasses).
    """
    assert find_emoji_by_phrase('sunglasses') == ('😎', 'sunglasses')
    assert find_emoji_by_phrase('sunglasses dark') == ('🕶️', 'sunglasses dark')

def test_overrides():
    """
    Sometimes the behavior is a little unexpected. E.g. noodle turns into poodle.

    There are some custom overrides that we've placed.
    """
    assert find_emoji_by_phrase('winking') == ('😉', 'winking')
    assert find_emoji_by_phrase('turkey') == ('🦃', 'turkey')
    assert find_emoji_by_phrase('noodle') == ('🍜', 'noodle')

def test_find_emoji_by_phrase_order():
    assert find_emoji_by_phrase('heart kissing')[0] == find_emoji_by_phrase('kissing heart')[0]

def test_find_emoji_by_phrase_avoid_transposition():
    # Used to return "lock with pen" 🔏
    assert find_emoji_by_phrase('okay with me') == None

def test_find_emoji_by_phrase_failure():
    # Nope used to return "Nose"
    assert find_emoji_by_phrase('nope') == None
    # Too far off
    assert find_emoji_by_phrase('garbage') == None
    assert find_emoji_by_phrase('enchilada') == None

def test_find_emoji_by_phrase_words():
    assert find_emoji_by_phrase(['?']) == ('❓', '?')
    assert find_emoji_by_phrase(['!']) == ('❗', '!')
    assert find_emoji_by_phrase([' you', ' are', ' a', ' dog']) == ('🐶', ' dog')

def test_get_emoji_phrase():
    # Don't process other emoji
    assert get_emoji_phrase(['dog', '😁']) == ['dog']
    # Don't process newlines
    assert get_emoji_phrase([' cat', 'this\n' ]) == [' cat']
    # Allow numbers
    assert get_emoji_phrase(['30', ':', '4', 'clock ']) == ['clock ', '4', ':', '30']

    # Colon is okay
    family = [' family', ':', ' man', ' woman', ' boy']
    assert get_emoji_phrase(family) == list(reversed(family))

    # Only process the last ten words (note that generator is from last word, so result is reversed)
    assert get_emoji_phrase([ 'a' ] * 50) == [ 'a' ] * 10
    assert get_emoji_phrase([ 'a' ] * 10 + [ 'b' ] * 10) == [ 'a' ] * 10

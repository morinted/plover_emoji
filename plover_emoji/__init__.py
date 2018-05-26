import json
import re
from fuzzyset import FuzzySet
import pkg_resources

# Which words that a user stenos should we consider for emoji...
# "clock 4:30" requires numbers and colon.
# !, ? are also valid.
EMOJI_WORD_WHITELIST = re.compile('[:A-Za-z\\d\\-!? ]+\\Z')
NORMALIZE_RX = re.compile('[^A-Za-z\\d\\ \\-!?]')
NUMBER = re.compile('(\\D+)(\\d+)')

def normalize(phrase):
    phrase = NORMALIZE_RX.sub('', phrase) # Remove symbols.
    phrase = NUMBER.sub('\\1 \\2', phrase) # Separate numbers from words.
    phrase = re.sub('  +', ' ', phrase) # Remove repeated spaces.
    return ' '.join(sorted(phrase.split(' ')))

def make_tokens(emoji_strategy: dict):
    name_to_unicode_output = {}
    for _, emoji in emoji_strategy.items():
        name = emoji['name']
        unicode_output = emoji['unicode_output']
        # :sweat_smile: --> sweat smile
        shortname = ' '.join(emoji['shortname'][1:-1].split('_'))

        name_to_unicode_output[normalize(name)] = unicode_output
        name_to_unicode_output[normalize(shortname)] = unicode_output

    # Manual aliases
    name_to_unicode_output['!'] = name_to_unicode_output['exclamation mark']
    name_to_unicode_output['?'] = name_to_unicode_output[normalize('question mark')]
    name_to_unicode_output['!!'] = name_to_unicode_output['double exclamation mark']
    name_to_unicode_output['!?'] = name_to_unicode_output['interrobang']
    name_to_unicode_output['?!'] = name_to_unicode_output['interrobang']
    return name_to_unicode_output

emoji_file = pkg_resources.resource_filename('plover_emoji', 'emoji_strategy.json')

with open(emoji_file) as f:
    data = json.load(f)
    name_to_unicode_output = make_tokens(data)
    fuzzy_emoji_set = FuzzySet(name_to_unicode_output.keys(), use_levenshtein=False)

def get_emoji(name):
    return name_to_unicode_output[name]

def unicode_output_to_characters(unicode_output):
    return ''.join([ chr(int(code, 16)) for code in unicode_output.split('-') ])

def find_emoji_by_phrase(phrase):
    if isinstance(phrase, str): # Convert from string to list for unit tests.
        phrase = [word + ' ' for word in phrase.split(' ') if word]
        phrase[-1] = phrase[-1][:-1] # Remove final trailing space.
    matches = []
    search = []
    for word in reversed(phrase):
        search = [word] + search
        query = ''.join(search)
        best_match = fuzzy_emoji_set.get(normalize(query.strip()))
        if best_match:
            matches.append(
                best_match[0] + (query,)
            )
    highscore = 0
    emoji = None
    words = None
    for match in matches:
        percentage, name, query = match
        percentage *= 100
        classifier = percentage + len(name)
        if classifier > highscore:
            highscore = classifier
            emoji = name
            words = query
    if highscore > 70:
        return (unicode_output_to_characters(get_emoji(emoji)), words)
    return None

def get_emoji_phrase(words):
    emoji_phrase = []
    counter = 0
    for word in words:
        # We don't really want emoji to span across line breaks or sentences
        if not EMOJI_WORD_WHITELIST.match(word):
            break
        emoji_phrase.append(word)
        counter += 1
        # 10 words should be enough for all of the emoji.
        if counter >= 10:
            break
    return list(reversed(emoji_phrase))

def emoji(ctx, cmdline):
    # Placeholder
    action = ctx.copy_last_action()
    result = find_emoji_by_phrase(get_emoji_phrase(ctx.iter_last_words()))
    if result:
        emoji, phrase = result
        action.text = emoji
        action.prev_replace = ''.join(phrase)
        action.prev_attach = True
        action.word = None
    return action

if __name__ == '__main__':
    find_emoji_by_phrase('poop')
    find_emoji_by_phrase('she was a woman police officer')
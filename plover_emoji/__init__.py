import json
import re
from fuzzywuzzy import process, fuzz
from fuzzyset import FuzzySet
from pprint import pprint

def make_tokens(emoji_strategy: dict):
    name_to_unicode_output = {}
    longest_name = ''
    for _, emoji in emoji_strategy.items():
        name = re.sub("[^A-Za-z ]", "", emoji['name'])  
        unicode_output = emoji['unicode_output']
        # :sweat_smile: --> sweat smile
        shortname = ' '.join(emoji['shortname'][1:-1].split('_'))

        name_to_unicode_output[name] = unicode_output
        name_to_unicode_output[shortname] = unicode_output
    print(longest_name)
    return name_to_unicode_output

with open('./emoji_strategy.json') as f:
    data = json.load(f)
    name_to_unicode_output = make_tokens(data)
    fuzzy_emoji_set = FuzzySet(name_to_unicode_output.keys())

def get_emoji(name):
    return name_to_unicode_output[name]

def unicode_output_to_characters(unicode_output):
    return ''.join([ chr(int(code, 16)) for code in unicode_output.split('-') ])

def find_emoji_by_phrase(phrase):
    matches = []
    search = []
    for word in reversed(phrase.split(' ')):
        search = [word] + search
        query = ' '.join(search)
        # matches.append(
        #    process.extract(query, name_to_unicode_output.keys(), limit=1, scorer=fuzz.token_sort_ratio)[0] + (query,)
        # )
        best_match = fuzzy_emoji_set.get(query)
        if best_match:
            print('matches')
            pprint(best_match)
            matches.append(
                best_match[0] + (query,)
            )
    highscore = 0
    emoji = None
    words = None
    pprint(matches)
    for match in matches:
        percentage, name, query = match
        percentage *= 100
        classifier = percentage + len(name)
        if classifier > highscore:
            highscore = classifier
            emoji = name
            words = query
    if highscore > 50:
        print('winner is', (unicode_output_to_characters(get_emoji(emoji)), words))
        return (unicode_output_to_characters(get_emoji(emoji)), words)
    return None

def emoji(ctx, cmdline):
    # Placeholder
    action = ctx.new_action()
    for word in ctx.iter_last_words():
        print('dorp: ', word)
        return action
    return action

if __name__ == '__main__':
    find_emoji_by_phrase('poop')
    find_emoji_by_phrase('she was a woman police officer')
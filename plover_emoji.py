'''
Functionality to repeat output in Plover.
'''

def emoji(ctx, cmdline):
    # Placeholder
    action = ctx.new_action()
    for word in ctx.iter_last_words():
        print('dorp: ', word)
        return action
    return action

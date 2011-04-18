
def fail(inp):
    return None, inp

def success(inp):
    return [], inp

def end_of_inp(inp):
    return [] if inp else None, inp

lastline = 0
def end_of_line(inp):
    global lastline
    lastline += 1
    try:
        if inp[0] == '\n':
            return [], inp[1:]
    except IndexError:
        return [], inp
    lastline -= 1
    return None, inp

def anychar(inp):
    if not inp:
        return None, ''
    return [inp[0]], inp[1:]


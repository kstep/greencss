from lexer.parsers.parsers import inf
from lexer.parsers.helpers import clear_lines
from lexer.tokens.statements import vardef, cmacro, crule
import lexer.parsers.basic as basic

parser = (vardef/0 | cmacro/0 | crule) * inf

def test_01():
    '''
    Simple definitions + macros & variables
    '''
    test = '''
variable = 12px
variable1 = 15px

@define macro:
    margin-left: 5px

@define macro2(a, b,c):
    margin: 1px $c

sub:
    font-face:  sans-serif, sans-serif
    %macro2(1px,2px,3px)
    margin-right: $variable
    margin-bottom: -10px
    margin-top: $variable1

alt:
    color: #123456
    '''
    test = clear_lines(test)
    print parser(test)

def test_02():
    '''
    Complex attributes definition
    '''
    test = '''
sub:
    margin->
        left: 10px
        right: 5px
        bottom: -10px
        top: 8px
    '''
    test = clear_lines(test)
    print test
    print parser(test)

def test_03():
    '''
    Nested definitions
    '''
    test = '''
body:
    margin->
        left: 20px
    #wrapper:
        margin->
            right: 10px
        b:
            color: #aaaaaa
    '''
    test = clear_lines(test)
    print test
    print parser(test)

def test_04():
    '''
    Real stylesheet transformation
    '''
    f = open('/home/kstep/projects/self/serpent/serpent/ui/styles/style.ccss','rb')
    test = clear_lines(f.read())
    print parser(test), basic.lastline

def test_05():
    test = '''
var1 = 10px
body:
    width: 90%
    margin: 5em auto
    font-family: "DejaVu Sans", Verdana, Arial, Helvetica, sans-serif
    background: url(/images/base_bg.jpg) no-repeat

    #wrapper:
        padding: 0.5em
        border: 1px solid gray
        border-radius: 1em
        background: url(/images/wooden_bg.jpg)
        margin-left: $var1 * 0.1
.wrapper:
    padding: 0.5em
    border: 1px solid gray
    border-radius: 1em
    background: url(/images/wooden_bg.jpg)
    margin-left: $var1 * 0.1
    '''
    print parser(clear_lines(test))

#test_01()
#test_02()
#test_03()
test_04()
#test_05()

#print ((((A^EOL)*inf) / join - EOL) >> indent_block)('''    dsafvfd
    #sdfvsfvd
    #sdfvsdfvsdf
#sdfdvdfv
#''')

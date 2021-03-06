from greencss import convert
#from nose.tools import eq_
def eq_(value, expected):
    if value != expected:
        raise AssertionError("Expected: %s\nGot:\n%s" % (expected, value))

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
    margin: 1px $c + 2
    i:
        margin->
            top: $b * 2 / $a

sub:
    font-face:  sans-serif, sans-serif
    %macro2(1px,2px,3px)
    margin-right: $variable
    margin-bottom: -10px
    margin-top: $variable1
    %macro()

alt:
    color: green
    '''
    eq_(convert(test),
            '''
sub {
  font-face: sans-serif sans-serif;
  margin: 1px 5.0px;
  margin-right: 12px;
  margin-bottom: -10px;
  margin-top: 15px;
  margin-left: 5px;
}
sub i {
  margin-top: 4.0px;
}
alt {
  color: #008000;
}
'''.lstrip())

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
    eq_(convert(test), '''
sub {
  margin-left: 10px;
  margin-right: 5px;
  margin-bottom: -10px;
  margin-top: 8px;
}
'''.lstrip())

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
    eq_(convert(test), '''
body {
  margin-left: 20px;
}
body #wrapper {
  margin-right: 10px;
}
body #wrapper b {
  color: #aaaaaa;
}
'''.lstrip())

def test_04():
    '''
    Complex selectors example
    '''
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

        &.selected:
            border: 1px solid red

.wrapper:
    padding: 0.5em
    border: 1px solid gray
    border-radius: 1em
    background: url(/images/wooden_bg.jpg)
    margin-left: $var1 * 0.1

    & + ul > ul:
        background->
            color: red
            image: url(/images/mybg.png)
            repeat: repeat-x
    '''
    eq_(convert(test), '''
body {
  width: 90%;
  margin: 5em auto;
  font-family: "DejaVu Sans" Verdana Arial Helvetica sans-serif;
  background: url(/images/base_bg.jpg) no-repeat;
}
body #wrapper {
  padding: 0.5em;
  border: 1px solid #808080;
  border-radius: 1em;
  background: url(/images/wooden_bg.jpg);
  margin-left: 1.0px;
}
body #wrapper.selected {
  border: 1px solid #ff0000;
}
.wrapper {
  padding: 0.5em;
  border: 1px solid #808080;
  border-radius: 1em;
  background: url(/images/wooden_bg.jpg);
  margin-left: 1.0px;
}
.wrapper + ul > ul {
  background-color: #ff0000;
  background-image: url(/images/mybg.png);
  background-repeat: repeat-x;
}
'''.lstrip())

def test_05():
    '''
    Method calls test
    '''
    test = '''
variable = "defg"

@define macro(var):
    bottom: $var.length() * 2px

body:
    margin: "abc".length() * 1px
    top: $variable.length() * 1px
    %macro("xx")
    '''
    eq_(convert(test), '''
body {
  margin: 3.0px;
  top: 4.0px;
  bottom: 4.0px;
}
'''.lstrip())

def test_06():
    '''
    Include file directive
    '''
    test = '''
@include "./tests/test.gcss"
body:
    margin-top: 10px
    '''
    eq_(convert(test), '''
body {
  background: #ff0000;
}
body {
  margin-top: 10px;
}
'''.lstrip())

def test_07():
    '''
    Metablocks
    '''
    test = '''
@-moz-document url-prefix("http://example.com"), domain(example.org):
    body:
        background: red
    '''
    eq_(convert(test), '''
@-moz-document url-prefix("http://example.com"), domain(example.org) {
body {
  background: #ff0000;
}
}
'''.lstrip())

def test_08():
    '''
    Color literals
    '''
    test = '''
body:
    color: red
    color: #ff0000
    color: rgb(255, 0, 0)
    color: rgb(100%, 0%, 0%)
    '''
    eq_(convert(test), '''
body {
  color: #ff0000;
  color: #ff0000;
  color: #ff0000;
  color: #ff0000;
}
'''.lstrip())

def test_09():
    '''
    Color operations
    '''
    test = '''
body:
    color: #00ee00.darken(100)
    color: #00ee00.brighten(100)
    color: #0000ee + #00ee00
    color: #0000ee - #0000ee
    color: #ee00ee / 10
    '''
    eq_(convert(test), '''
body {
  color: #00eb00;
  color: #00f000;
  color: #00eeee;
  color: #000000;
  color: #170017;
}
'''.lstrip())

def test_10():
    '''
    Important flag
    '''
    test = '''
body:
    background: url(/image.png) repeat !important
    margin->
        left: 10px !important
        right: 10px !important
        top: 5px
.class: !important
    color: red
    background: white
    .subclass:
        color: blue
        background: blue !not-important
        .subsubclass:
            color: white
        .subsubclass: !not-important
            background: green
    '''
    eq_(convert(test), '''
body {
  background: url(/image.png) repeat !important;
  margin-left: 10px !important;
  margin-right: 10px !important;
  margin-top: 5px;
}
.class {
  color: #ff0000 !important;
  background: #ffffff !important;
}
.class .subclass {
  color: #0000ff !important;
  background: #0000ff;
}
.class .subclass .subsubclass {
  color: #ffffff !important;
}

.class .subclass .subsubclass {
  background: #008000;
}
'''.lstrip())

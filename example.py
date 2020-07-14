import Crystal;

template = """
~y = x * x
The value of x is {{x}} so the value of y is {{y}}!
""";

# evaluate the template directly
print( Crystal.evaluateTemplate(template, {"x":1}) )

# compile it for later use
code = Crystal.compileTemplate(template)
print( Crystal.evaluateCompiledTemplate(code, {"x":2}) )

# or convert it into a function for later use
f = Crystal.functionFromTemplate(template)
print( f({"x":3}) )


# What

Crystal is a templating system, or equivalently language pre-processor, that leverages the full power of python inserted throughout.

# Key features

* **Powerful** - templates that expose the full power of Python
* **Efficient** - compile into pure python for high performance 
* **Scalable** - line-by-line error reporting to find issues in complex templates
* **Applicable** - use as a stand alone meta language/template engine/preprocessor
* **Flexible** - customize the syntax to suit your preference or constraints

# Use cases

To use it as a template processor / preprocessor do something like this:

```
bash-3.2$ ./crystal myfile.html.crystal > myfile.html
```

where myfile.html.crystal could be:

```
<html>
~title = "hello world"
    <head>
        <title>{{ title }}</title>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <ol>
~for n in range(0,3):
            <li>Item {{n}}</li>
~/for
        </ol>
    </body>
</html>
```

or use it as a better preprocessor:
```
bash-3.2$ ./crystal myfile.c.crystal > myfile.c
```

```
~COUNT = 5
#include <stdio.h>
main(){
	for (int n = 0; n < {{COUNT}}; n++){
		printf("item %d\n", n);
	}
}
```

Or to use it as a Python library, by doing something like one of these:

```
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
```


# Examples to show the power of Crystal

In the examples below, templates are shown like this:

```
this is the
~# the template, not
~^
 output
```

and the output is shown like this:

> this is the output      




```
You can set variables like this:
~x = 4

and you can use them like this {{x}} or like this {{x+5}}
```
> You can set variables like this:  
>   
> and you can use them like this 4 or like this 9  

```
Structures work too: 
~a = {"a" : "javascript", "c": "python"}

and you can access them just like in {{a["c"]}}.
```

> Structures work too:   
>   
> and you can access them just like in python.  


```
As do comments.
~#like this one which you'll never see
```

> As do comments.  


```
You can interjet and
~# any amount of complext stuff
~y = 7
~#so long as you preceed the next line with a ~^
~^
 you wont break lines. Just be careful about adding spaces as needed.
```

> You can interjet and you wont break lines. Just be careful about adding spaces as needed.  



```
Functions can be defined using text inside.
~#as in this example
~def myfunc(u):
~    x = 3
   I like my local value of {{x}} as much as the input {{u}}
~/def
~^
 And then just call them:
~myfunc(7)

as many times as you like:
~myfunc(9)
```

> Functions can be defined using text inside. And then just call them:  
>    I like my local value of 3 as much as the input 7  
>   
> as many times as you like:  
>    I like my local value of 3 as much as the input 9  

```
scopes and closures are honored. If we set x to 5
~^
~x = 5
 then x = {{x}}, and yet our function which uses x:
~myfunc("happy")
still leaves x = {{x}}
```

> scopes and closures are honored. If we set x to 5 then x = 5, and yet our function which uses x:  
>    I like my local value of 3 as much as the input happy  
> still leaves x = 5  


```
~def myfunc2():
~    global a
Using global we can reach outside to see that a == {{a}}
and we can change its value
~    a["d"] = "C++"
~/def
~myfunc2()
so now a is {{a}}
```

> Using global we can reach outside to see that a == {'a': 'javascript', 'c': 'python'}  
> and we can change its value  
> so now a is {'a': 'javascript', 'c': 'python', 'd': 'C++'}  


```
Functions that return strings 
~#like this:
~def bar(x):
~    return f"in the {x} middle of"
~/def
~^ 
can be called {{bar("very")}} lines
```

> Functions that return strings can be called in the very middle of lines  



```
Loops work too:
~for n in range(1,3):
         * item {{n}}
~/for
```

> Loops work too:  
>          * item 1  
>          * item 2  


```
Loops of functions? Why not!
~def myfunc2(m):
         * item {{m+10}}
~/def
~for n in range(1,3):
~    myfunc2(n)       
~/for
```

> Loops of functions? Why not!  
>          * item 11  
>          * item 12  


```
Loops in functions. Yup. Got that too:
~def myfunc3():
~    for n in range(1,3):
         * item {{n+100}}
~/def
~myfunc3()
```

> Loops in functions. Yup. Got that too:  
>          * item 101  
>          * item 102  


```
Single line loops work too:
~for n in range(1,5):
~^
  * item {{n}}
~/for
```

> Single line loops work too:  * item 1  * item 2  * item 3  * item 4  


```
~# You may have noticed the use of "code enders" in the examples above.
~# Because your output text is likely not going to be indented
~# according to python so they're needed to differentiate between cases
~# like this:

~for n in range(0,3):
repeat this 3 times
and repeat this too
```

> repeat this 3 times  
> and repeat this too  
> repeat this 3 times  
> and repeat this too  
> repeat this 3 times  
> and repeat this too  


```
~for n in range(0,3):
repeat this 3 times
~/for
but dont repeat this
```

> repeat this 3 times  
> repeat this 3 times  
> but dont repeat this  

```
~# Notice that the first ~for was not closed. It could be written as:
~for n in range(1,3):
repeat this 3 times
and repeat this too
~/for
```

> repeat this 3 times  
> and repeat this too  
> repeat this 3 times  
> and repeat this too  


```
~# By default code enders are any line that begins with . or / 
~# 
~# Generally you might write:

~def foo():
~    for n in range(1,3):
This line is in the loop.
And so is this one.
~    /for
This line is not, but is still in the function
~.def
This line is outside the function
~foo()
```

> This line is outside the function  
> This line is in the loop.  
> And so is this one.  
> This line is in the loop.  
> And so is this one.  
> This line is not, but is still in the function  


```
~# Though you might prefer something else, e.g. empy enders, or
~# some other ending word (e.g. 'endif','enddef', 'endfor', etc)

~def foo():
~    for n in range(1,3):
This line is in the loop.
And so is this one.
~    /
This line is not, but is still in the function.
~.enddef
This line is outside the function
~foo()
```

> This line is outside the function  
> This line is in the loop.  
> And so is this one.  
> This line is in the loop.  
> And so is this one.  
> This line is not, but is still in the function.  

```
~# if something gets complicated you can annotate it
~= annotate True
~for n in range(1,3):
this line
~    for n2 in range(4,6):
that line
~    /for
~/for
~= annotate False
```

> this line&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* info.crystal:350 \*/  
> that line&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* info.crystal:352 \*/  
> that line&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* info.crystal:352 \*/  
> this line&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* info.crystal:350 \*/  
> that line&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* info.crystal:352 \*/  
> that line&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* info.crystal:352 \*/  


```
~# you can also change the indicators to personalize things,
~# either as a configuration parameter to the evaluate function
~# or direclty within the template

~= code ^---> (.*)$  
~= ender ^--->(.*)<  
~= nobreak ^[ \t]*<nobreak>[ \t]*$  
~= open \$\(
~= close \)

---> kind = "different"  
now its like a
<nobreak>  
 totally $(kind) language!
```
> now its like a totally different language!  


```
or go wild and invent your own crazy syntax

~= indicator ^!!(.*)!!$
~= ender ^!!( *)@.*!!$
~= nobreak ^!!\+\+KEEP\+\+!!$
~= reassign ^:set(.*)$
:set open (<<)
:set close (>>)  

!!kind = "different"!!
now its like a
!!++KEEP++!!
 totally <<kind>> language!  
```

> now its like a totally different language!  


```
~#and you can even have emacs highlight the meta lines
~#Hi-lock: (("^~.*$" (0 (quote hi-blue) append)))
~#Hi-lock: (("{{[^}]*}}" (0 (quote hi-blue) append)))
```




# More usage examples


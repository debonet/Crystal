import os
import re

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
class CrystalException(BaseException): pass


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fsCodeCompileTemplate(sTemplate, configIn={}, sflWorking="TEMPLATE"):
    """ compile a template """

    # -----------------------------------------------------
    # -----------------------------------------------------
    def fsRegularize(s):
        return s.replace('{','{{').replace('}','}}')

    def fxNormalizeConfig(sConfig, sVal):
        if sConfig in ["debug", "annotate"]:
            return eval(sVal,{},{})

        if sConfig in ["open", "close"]:
            sVal = fsRegularize(sVal)

        return re.compile(sVal)

    reWordSplit = re.compile("[ \t()\"']+")
    def fvsWords(s,c=0):
        return list(filter(None, reWordSplit.split(s,maxsplit=c)))

    reSpaceSplit = re.compile("[\t ]+")
    def fvsSpacedWords(s,c=0):
        return list(filter(None, reSpaceSplit.split(s,maxsplit=c)))


    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    def fsCodeCompileInternal(
            sTemplate, config, sflWorking, bJoinLines=False, sInQuote=None

    ):
        """
        handle the regular/non-code portions of templates
        """

        # -----------------------------------------------------
        # -----------------------------------------------------
        def fHandleReassign(s):
            """
            handle reassignment of configuration expressions
            """
            
            s = config["reassign"].sub("",s,1)
            vsArgs = fvsSpacedWords(s,2)
            config[vsArgs[0]] = fxNormalizeConfig(vsArgs[0], vsArgs[1])

        # -----------------------------------------------------
        # -----------------------------------------------------
        def fHandleNobreak(s):
            """
            skip the next newline
            """
            nonlocal bJoinLines
            bJoinLines = True

        # -----------------------------------------------------
        # -----------------------------------------------------
        def fHandleInclude(s):
            """
            include sub templates. 

            file list can optionaly be delimited with parens, 
            quotes and commas
            """
            
            nonlocal sCode
            nonlocal sInQuote
            nonlocal bJoinLines
            vsfl = fvsWords(s)

            sdirWorking = os.path.dirname(os.path.abspath(sflWorking)) + "/"
            
            for sfl in vsfl:
                sfl = os.path.abspath(sdirWorking + sfl)
                try:
                    with open(sfl, "rt") as fl:
                        sCode += fsCodeCompileInternal(
                            fl.read(), config.copy(), sfl, bJoinLines, sInQuote
                        )
                except:
                    raise CrystalException(f"failed to open file {sfl}\n\n{sflWorking}:{nLine}:{s}\n")

                if config["debug"]:
                    sCode += "\n"
                    sCode += "#-------------------------------------------\n"
                    sCode += f"# RETURNING TO FILE {sflWorking}\n"
                    sCode += "#-------------------------------------------\n"

        # -----------------------------------------------------
        # -----------------------------------------------------
        def fHandleCode(s):
            """
            handle python code lines within a template
            """

            # handle multiline quotes
            nonlocal vsQuoteCurrent
            n = 0
            nEnd = None
            if vsQuoteCurrent:
                s = vsQuoteCurrent[0] + s
                n += len(vsQuoteCurrent[0])
                
            while n<len(s):
                if vsQuoteCurrent:
                    if s[n:].startswith(vsQuoteCurrent[1]):
                        n += len(vsQuoteCurrent[1])
                        s = s[0:n] + ")" + s[n:]
                        vsQuoteCurrent = None
                elif s[n] == '#':
                    nEnd = n
                    break
                
                else:
                    for vsQuote in vvsQuote:                    
                        if s[n:].startswith(vsQuote[0]):
                            vsQuoteCurrent = vsQuote
                            s = s[0:n] + "(" + s[n:]
                            n+=len(vsQuote[0])
                            break
                n += 1
                
            if vsQuoteCurrent:
                s = f"{s}\\n{vsQuoteCurrent[1]}"

            # check if we're on an group expression opener line
            if nEnd == None:
                nEnd = len(s)

            bPythonOpener = not sInQuote and rePythonOpener.search(s[:nEnd])

            # handle indents
            nonlocal cIndent
            cIndent = 0
            while cIndent<len(s) and s[cIndent] == " ":
                cIndent += 1

            if bPythonOpener:
                cIndent += 4

            # output modified code
            nonlocal sCode
            if config["debug"]:
                nonlocal nLine
                sCode += s
                sCode += f" # {sflWorking}:{nLine}\n"
            else:
                sCode += f"{s}\n"

        # -----------------------------------------------------
        # -----------------------------------------------------
        def fHandleCodeEnder(s):
            """
            handle indent correction for pseudo line enders (e.g. "/for")
            """
            # if we're in a quote, handle it as code
            nonlocal vsQuoteCurrent
            if vsQuoteCurrent:
                return fHandleCode(s)

            # fix the indent
            nonlocal cIndent
            nonlocal sCode
            cIndent = len(s)

            # only log debug, otherwise no code is issued
            if config["debug"]:
                nonlocal nLine
                sCode += " " * cIndent + f"# {sflWorking}:{nLine}\n"
            else:
                sCode += "\n"

        # -----------------------------------------------------
        # -----------------------------------------------------
        def fHandleNonCode(s):
            """
            handle the regular/non-code portions of templates
            """

            # if we're in a quote, handle it as code
            nonlocal vsQuoteCurrent
            if vsQuoteCurrent:
                return fHandleCode(s)
                
            s = fsRegularize(s)
            s = config["open"].sub('{',s)
            s = config["close"].sub('}',s)
            
            #optionally annotate the output
            nonlocal nLine
            if config["annotate"]:
                s = s.replace("\t","\\t")
                if len(s) > 0 and s[-1] == "\\":
                    s =  f"%-80s \t/* {sflWorking}:{nLine} */ \\" % s[-1]
                else:
                    s =  f"%-80s \t/* {sflWorking}:{nLine} */" % s

            # handle line joining
            nonlocal bJoinLines
            if not bJoinLines:
                s = "\n" + s
            bJoinLines = False

            # output the code
            nonlocal sCode
            s = s.replace("\n","\\n")

            sCode += " " * cIndent

            if len(s) > 0:
                if s[-1] == '\\':
                    sCode += f'write(f"""{s}\\""")'
                elif  s[-1] == '"':
                    sCode += f"write(f'''{s}''')"
                else:
                    sCode += f'write(f"""{s}""")'

            if config["debug"]:
                sCode += f" # {sflWorking}:{nLine}\n"
                
        # -----------------------------------------------------
        # -----------------------------------------------------
        vtrefHandler = [
            ("reassign",    fHandleReassign),
            ("nobreak",     fHandleNobreak),
            ("include",     fHandleInclude),
            ("end",         fHandleCodeEnder),
            ("code",        fHandleCode),
            ("text",        fHandleNonCode),
        ]
             
        cIndent  = 0
        vsQuoteCurrent = None
        sCode = ""
        if config["debug"]:
            sCode += "\n"
            sCode += "#-------------------------------------------\n"
            sCode += f"# ENTERING FILE {sflWorking}\n"
            sCode += "#-------------------------------------------\n"

        vs = sTemplate.split('\n')

        nLine = 1
        for s in vs:
            for t in vtrefHandler:
                m = config[t[0]].search(s) 
                if m:
                    t[1](m.group(1) if len(m.groups()) > 0 else "")
                    break
            nLine += 1

        return sCode

    # -----------------------------------------------------
    # -----------------------------------------------------
    rePythonOpener = re.compile(":[ \t]*(#.*)?$")
    vvsQuote = [
        ['f"""','"""'],
        ['"""','"""'],
        ["f'''","'''"],
        ["'''","'''"],
        ['f"','"'],
        ['"','"'],
        ["f'","'"],
        ["'","'"]
    ]

    config = {
        "code"          : "^~(.*)$",
        "include"       : "^~include(.*)$",
        "nobreak"       : "^~\\^(.*)$",
        "reassign"      : "^~=(.*)",
        "end"           : "^~( *)[./][a-z]*[ \t]*$",
        "text"          : "^(.*)$",
        "open"          : "{{",
        "close"         : "}}",
        "debug"         : "True",
        "annotate"      : "False"
    }

    config.update(configIn)

    for sOption in config:
        config[sOption] = fxNormalizeConfig(sOption, config[sOption])

    # drop any initial shebangs
    if sTemplate[0:2] == "#!":
        sTemplate = sTemplate[sTemplate.find("\n")+1:]
        
    sCode = fsCodeCompileInternal(sTemplate, config, sflWorking)

    return sCode

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
import traceback
import sys
def fsTraceError(e, sCode):
    vs = sCode.split('\n')

    if hasattr(e,"lineno"):
        nLineCompiled = e.lineno
            
        if nLineCompiled == 1:
            sErr = "{" + e.text[1:-1] + "}"
            sLocs = ""
            for n,s in enumerate(vs):
                if s.find(sErr) >= 0:
                    nLineCompiled = n + 1
    else:
        cl, exc, tb = sys.exc_info()
        nLineCompiled = traceback.extract_tb(tb)[-1][1]

    reLoc = re.compile(" # ([^#:]+):([^#:]+)$")
    reCleanException = re.compile("\\(.*", re.DOTALL)
    mLoc  = reLoc.search(vs[nLineCompiled-1])
    sEx   = reCleanException.sub("",str(repr(e)))

    if mLoc:
        sfl   = mLoc.group(1)
        nLineSource = int(mLoc.group(2))
        sLineSource = reLoc.sub("", vs[nLineCompiled-1])
        sErr = f"{sfl}:{nLineSource}:{sEx}\n\n{sLineSource}\n\n"
    else:
        sLine = vs[nLineCompiled-1]

        sErr = f"unknown error {sEx} in template on line {nLineCompiled}:\n\n\t{sLine}"

    return sErr

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def ftcodescodeCompile(sTemplate, config={}, sflWorking = "TEMPLATE"):
    sCode = fsCodeCompileTemplate(sTemplate, config, sflWorking)
    sErr = None
    try:
        return (compile(sCode, sflWorking, "exec"), sCode)
    except SyntaxError as e:
        sErr = fsTraceError(e, sCode)
            
    if sErr:
        raise CrystalException(sErr)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fcodeCompile(sTemplate, config={}, sflWorking = "TEMPLATE"):
    return ftcodescodeCompile(sTemplate, config, sflWorking)[0]
    
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fsEvaluateTemplate(
        sTemplate, envGlobal={}, envLocal={},
        config={}, sflWorking = "TEMPLATE"
):
    """ evaluate template """

    code,sCode = ftcodescodeCompile(sTemplate, config, sflWorking)

    return fsEvaluateCompiledTemplate(code, envGlobal, envLocal, config, sCode)


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fsEvaluateFile(sfl, envGlobal={}, envLocal={}, config={}):
    """ evaluate file containing a template """

    with open(sfl, "rt") as fl:
        return fsEvaluateTemplate(
            fl.read(), envGlobal, envLocal, config, sfl
        )


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fsEvaluateCompiledTemplate(
        _code, _envGlobal={},_envLocal={}, _config={}, sCode = None
):
    """ evaluate a compled template """

    _sFinal = ""
    def _fWrite(*vs,**aArg):
        nonlocal _sFinal
        for s in vs:
            _sFinal += str(s)
        
        if "end" in aArg:
            _sFinal += str(aArg["end"])

    if not "__builtins__" in _envGlobal:
        _envGlobal["__builtins__"] = __builtins__

    _envGlobal["__builtins__"]["write"] = _fWrite;
    _envGlobal["__builtins__"]["print"] = print;

    sErr = None
    try:
        exec(_code, _envGlobal, _envLocal)
    except Exception as e:
        sErr = ' '.join(e.args) + "\n" + fsTraceError(e, sCode) 
    
    if (sErr):
        raise CrystalException(sErr)

    # eliminate the first newline, but add one at the end
    return _sFinal[1:]

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
import textwrap

def fsftsaCodeCompileTemplate(
        sTemplate, sfName, sArgs = "aArgs",
        config={}, sflWorking = "TEMPLATE"
):
    sCode = fsCodeCompileTemplate(sTemplate, config, sflWorking)
    sCode = " " * 12   + sCode.replace("\n","\n" + " " * 12)

    return textwrap.dedent(f"""
        def {sfName} ({sArgs}):
            # -----------------------------------------------
            # import args into local()
            # -----------------------------------------------
            for __{sfName}_s__, __{sfName}_x__  in {sArgs}.items():
                 globals()[__{sfName}_s__] = __{sfName}_x__

            # -----------------------------------------------
            # define the write function
            # -----------------------------------------------
            __{sfName}_sFinal__ = ""
            def write(*vs,**aArg):
                nonlocal __{sfName}_sFinal__
                for s in vs:
                    __{sfName}_sFinal__ += str(s)

                if "end" in aArg:
                    __{sfName}_sFinal__ += str(aArg["end"])

            {sCode}

            # -----------------------------------------------
            # push locals back into the args
            # -----------------------------------------------
            for __{sfName}_s__, __{sfName}_x__  in dict(locals()).items():
                 if (
                            __{sfName}_s__.find("__{sfName}_") != 0 
                            and __{sfName}_s__!="write"
                            and __{sfName}_s__!="{sArgs}"
                 ):
                     {sArgs}[__{sfName}_s__] = __{sfName}_x__

            return __{sfName}_sFinal__,{sArgs}
        """)


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fftsaCodeCompileTemplate(
        sTemplate, sArgs = "aArgs", config={}, sflWorking = "TEMPLATE"
):
    sftsaCode = fsftsaCodeCompileTemplate(sTemplate, "__fTemplate__", "__aArgs__")
    
    env = {}
    env["__builtins__"] = __builtins__

    # compile it, and catch any compile time exceptions
    sErr = ""
    try:
        exec(sftsaCode,env,env)
    except Exception as e:
        sErr = fsTraceError(e, sftsaCode)
    
    if (sErr):
        raise CrystalException(sErr)

    
    # return a function wich intelligently handles runtime exceptions
    def ftsaOut(aArgs):
        sErr = ""
        try:
            s,aArgsOut = env['__fTemplate__'](aArgs)
        except Exception as e:
            sErr = fsTraceError(e, sftsaCode)
    
        if (sErr):
            raise CrystalException(sErr)

        return s, aArgsOut
    
    return ftsaOut

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def ffsCodeCompileTemplate(
        sTemplate, sArgs = "aArgs", config={}, sflWorking = "TEMPLATE"
):
    ftsa = fftsaCodeCompileTemplate(sTemplate,sArgs,config,sflWorking)

    def fs(aArgs):
        return ftsa(aArgs)[0][1:]
            
    return fs
    



# ----------------------------------------------------------------------------
# standard python style (unstructued) names for external functions
# ----------------------------------------------------------------------------
evaluateTemplate         = fsEvaluateTemplate;
compileTemplate          = fcodeCompile;
evaluateCompiledTemplate = fsEvaluateCompiledTemplate;
evaluateFile             = fsEvaluateFile;
functionFromTemplate     = ffsCodeCompileTemplate;



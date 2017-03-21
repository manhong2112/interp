"""
參照某天跟冰封提起的方法嘗試實現的一個解釋器
"""
import env
from type import is_none, is_int, is_float, is_string, is_quote_by
from type import String

def value_parser(s):
    if is_quote_by(s, '"') or is_quote_by(s, "'"):
        return String(''.join(s[1:-1]))
    else:
        return ''.join(s)

# parser str to list
# 以防萬一新parser出了甚麼事, 和生成測試用的
# 講真, 加了其它功能後這個parser貌似連生成測試都沒辦法了..
def _parser(expr):
    length = len(expr)
    def _f(index):
        result = []
        buffer = []
        while index < length:
            if expr[index] == "(" or expr[index] == "[":
                if buffer:
                    result.append(value_parser(buffer))
                    buffer = []
                sub_res, index = _f(index + 1)
                result.append(sub_res)
                if index >= length:
                    return result
            char = expr[index]
            if char == ")" or char == "]":
                if buffer:
                    result.append(value_parser(buffer))
                return result, index + 1
            elif char == " " or char == "\n":
                if buffer:
                    result.append(value_parser(buffer))
                    buffer = []
            else:
                buffer.append(char)
            index += 1
        return value_parser(buffer), index
    return _f(0)[0]

def parser(expr):
    res = []
    last = [res]
    index = 0
    buffer = []
    FLAG = 0
    FLAG_DEFAULT = 0
    FLAG_STRING = 1
    FLAG_ESCAPING_STRING = 2
    # 呃..應該差不多是這樣? 其實我在想會不會用到位運算....
    ## 感覺好複雜..找天看看能不能想個辦法改改..
    ESCAPING_LIST = {
        "n": "\n",
        '"': "\"",
        "'": '\"'
    }
    for char in expr:
        if FLAG == FLAG_ESCAPING_STRING:
            if char in ESCAPING_LIST:
                buffer += ESCAPING_LIST[char]
                FLAG = FLAG_STRING
            else:
                raise SyntaxError(char)
        elif char == "(" or char == "[":
            if buffer:
                last[-1].append(value_parser(buffer))
                buffer = []
            new = []
            last[-1].append(new)
            last.append(new)
        elif char == ")" or char == "]":
            if buffer:
                last.pop().append(value_parser(buffer))
                buffer = []
            else:
                last.pop()
        elif char == " ":
            if buffer:
                last[-1].append(value_parser(buffer))
                buffer = []
        elif char == "\"":
            if FLAG == FLAG_DEFAULT:
                FLAG = FLAG_STRING
            elif FLAG == FLAG_STRING:
                last[-1].append(String(''.join(buffer)))
                buffer = []
                FLAG = FLAG_DEFAULT
            elif FLAG == FLAG_ESCAPING_STRING:
                buffer += char
                FLAG = FLAG_STRING
            else:
                print("WTF??")
        elif char == "\\":
            if FLAG == FLAG_DEFAULT:
                raise SyntaxError
            elif FLAG == FLAG_STRING:
                FLAG = FLAG_ESCAPING_STRING
            elif FLAG == FLAG_ESCAPING_STRING:
                buffer += char
            else:
                print("WTF??")
        else:
            buffer += char
        index += 1
    if FLAG != FLAG_DEFAULT:
        raise SyntaxError
    if buffer:
        last[-1].append(value_parser(buffer))
        buffer = []
    return res[0]

scopeID = 0
def interp0(expr, env, scope):
    if isinstance(expr, list):
        fun = interp0(expr[0], env, scope)[0]
        global scopeID
        scopeID += 1
        # print((str(fun), scope))
        return fun(expr[1:], env, (scopeID, scope))
    elif is_none(expr):
        return (None, None)
    elif is_string(expr):
        return (expr, None)
    elif is_int(expr):
        return (int(expr), None)
    elif is_float(expr):
        return (float(expr), None)
    else:
        return (env.get(scope, expr), None)

def interp(expr):
    return interp0(expr, env.Env(), None)[0]

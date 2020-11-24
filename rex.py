import argparse
import re
import os
import sys
from timeit import default_timer as timer

paths = [".", "./lib"]

errMap = {"ValueError": "TypeError"}

typeTree = {
	"type": {
		"num": {
			"int": {
				"whole": {
					"natural": {},
				},
			},
			"float": {},
		},
		"str": {},
		"null": {},
		"bool": {},
		"err": {
			"mathErr": {
				"zeroDivisionErr": {},
			},
			"typeErr": {},
			"syntaxErr": {},
			"scopeErr": {},
			"branchErr": {},
			"nameErr": {},
			"includeErr": {},
			"fileErr": {},
			"recursionErr": {},
			"indexErr": {},
			"rangeErr": {},
		},
	}
}

functions = {
	# For builtin functions, the function body must be written in Python and the conditions must be written in Rex
	# Misc
	"exit": {"parameters": [], "return": "null", "execute": [("exit()", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"out": {"parameters": [("s", "str")], "return": "null", "execute": [("print(s)", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"in": {"parameters": [("s", "str")], "return": "str", "execute": [("input(s)", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"error": {"parameters": [("eType", "str"), ("message", "str")], "return": "err", "execute": [("message", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	# Arithmetic operations
	"+": {"parameters": [("x", "num"), ("y", "num")], "return": "num", "execute": [("x + y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"-": {"parameters": [("x", "num"), ("y", "num")], "return": "num", "execute": [("x - y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"*": {"parameters": [("x", "num"), ("y", "num")], "return": "num", "execute": [("x * y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"/": {"parameters": [("x", "num"), ("y", "num")], "return": "num", "execute": [("x / y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"%": {"parameters": [("x", "num"), ("y", "num")], "return": "num", "execute": [("x % y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	# Comparison operations
	"==": {"parameters": [("x", "type"), ("y", "type")], "return": "bool", "execute": [("x == y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"!=": {"parameters": [("x", "type"), ("y", "type")], "return": "bool", "execute": [("x != y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	">": {"parameters": [("x", "num"), ("y", "num")], "return": "bool", "execute": [("x > y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"<": {"parameters": [("x", "num"), ("y", "num")], "return": "bool", "execute": [("x < y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	">=": {"parameters": [("x", "num"), ("y", "num")], "return": "bool", "execute": [("x >= y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"<=": {"parameters": [("x", "num"), ("y", "num")], "return": "bool", "execute": [("x <= y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	# Boolean operations
	"&&": {"parameters": [("x", "bool"), ("y", "bool")], "return": "bool", "execute": [("x and y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"||": {"parameters": [("x", "bool"), ("y", "bool")], "return": "bool", "execute": [("x or y", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	"!": {"parameters": [("x", "bool")], "return": "bool", "execute": [("not x", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
	# String operations
	".": {"parameters": [("s1", "str"), ("s2", "str")], "return": "str", "execute": [("s1 + s2", True)], "catch": [], "library": "builtin", "scope": "global", "lang": "python", "dep": []},
}

stack = []

def error(e = "Error", msg = "An error occurred", f = "", function = "", line = 0):
	print(str(e), end = "")
	if function != "":
		print(" in function " + str(function), end = "")
	if line != 0:
		print(" on line " + str(line), end = "")
	if f != "":
		print(" in file " + str(f), end = "")
	print(": ")
	print(msg)
	if stack != []:
		print("Traceback: " + str(stack))
	exit()

def handleError(errType, msg, catches, library):
	for catch in catches:
		body = catch[0]
		condition = catch[1]
		if errType == condition:
			return handleExpression(body, library)
	return msg, errType

def execute(tokens, library):
	if tokens != []:
		term = tokens.pop(0)
		stack.append(term)
		if term in functions.keys():
			function = functions[term]
			args = []
			params = function["parameters"]
			python = function["lang"] == "python"
			newLibrary = function["library"] if function["library"] != "builtin" else library
			for i in range(len(params)):
				arg, argType = execute(tokens, newLibrary)
				paramType = params[i][1]
				if typesMatch("err", argType):
					return arg, argType
				elif typesMatch(paramType, argType):
					args.append(arg)
				else:
					error(e = "typeErr", f = library, function = term, msg = "Argument type " + argType + " does not match parameter type " + paramType)
			for branch in function["execute"]:
				condition = subArgs(branch[1], args, params, False)
				result, resultType = handleExpression(condition, newLibrary)
				if typesMatch("bool", resultType):
					if result:
						body = subArgs(branch[0], args, params, python)
						result = ""
						if library == function["library"] or function["scope"] == "global":
							if python:
								try:
									for dep in function["dep"]:
										exec("import " + dep)
									if term == "error":
										raise Exception(eval(body))
									result, resultType = specialiseType(eval(body), function["return"])
								except Exception as e:
									result = str(e)
									resultType = fetchErrType(type(e).__name__)
							else:
								result, resultType = handleExpression(body, newLibrary)
							
							if typesMatch("err", resultType):
								result, resultType = handleError(resultType, result, function["catch"], newLibrary)
								return result, resultType
							elif typesMatch(function["return"], resultType):
								if function["return"] == "str":
									if result == "" or result[0] != '"':
										result = '"' + result + '"'
								stack.pop()
								return result, resultType
							else:
								error(e = "typeErr", f = library, function = term, msg = "Actual return type " + resultType + " does not match expected type " + function["return"])
						else:
							error(e = "scopeErr", f = library, function = term, msg = "Function out of scope") # Not used at the moment, will be when proper scoping is introduced
				else:
					error(e = "typeErr", f = library, function = term, msg = "Condition type " + resultType + " does not match type bool")
			error(e = "branchErr", f = library, function = term, msg = "No condition matched")
		else:
			data, dataType = autocast(term)
			stack.pop()
			return data, dataType
	else:
		error(e = "typeErr", f = library, msg = "Not enough arguments present")

def handleExpression(expression, library):
	tokens = []
	if type(expression) == str:
		tokens = tokenise(expression)
	else:
		tokens = [expression]
	return execute(tokens, library)

def typesMatch(expected, actual):
	if expected == actual or actual == "":
		return True
	else:
		return traverseTypeTree(typeTree, expected, actual, False)

def traverseTypeTree(tree, expected, actual, foundExpected):
	match = False
	for type, subTypes in tree.items():
		if type == actual and foundExpected:
			return True
		match = match or traverseTypeTree(subTypes, expected, actual, foundExpected or type == expected)
	return match

def specialiseType(data, returnType):
	if returnType == "num":
		if int(data) == data:
			if int(data) >= 0:
				if int(data) > 0:
					return data, "natural"
				else:
					return data, "whole"
			else:
				return data, "int"
		else:
			return data, "num"
	else:
		return data, returnType

def autocast(data):
	if type(data) == str:
		if data == "null":
			return None, "null"
		elif data == "True" or data == "False":
			return bool(data), "bool"
		else:
			try:
				asInt = int(data)
				if asInt >= 0:
					if asInt > 0:
						return asInt, "natural"
					else:
						return asInt, "whole"
				else:
					return asInt, "int"
			except:
				try:
					return float(data), "float"
				except:
					if data[0] == '"' and data[-1] == '"':
						return data, "str"
					else:
						error(e = "NameError", msg = data + " is undefined")
	else:
		return data, type(data).__name__

def fetchErrType(pyErrType):
	errType = pyErrType
	if pyErrType == "Exception":
		errType = "err"
	if pyErrType in errMap.keys():
		errType = errMap[pyErrType]
	errType = errType[0].lower() + errType[1:] if errType else ""
	errType = errType.replace("Error", "Err")
	return errType

def subArgs(body, args, params, python):
	if python:
		newBody = str(body)
		for j in range(len(params)):
			arg = args[j]
			param = params[j][0]
			newBody = re.sub(r"\b%s\b" % param, str(arg), newBody)
		return newBody
	else:
		tokens = tokenise(str(body))
		for i in range(len(tokens)):
			token = tokens[i]
			for j in range(len(params)):
				arg = args[j]
				param = params[j][0]
				if token == param:
					tokens[i] = str(arg)
					break
		return " ".join(tokens)

def parseFunctionDeclaration(tokens, library, scope, lang, lineNumber):
	if tokens != []:
		name = tokens.pop(0)
		if not name[0].isalpha() and not name[0] == "_":
			error(e = "syntaxErr", f = library, function = name, msg = "Function name initial must be a letter or an underscore", line = lineNumber)
		elif not re.match(r'^\w+$', name):
			error(e = "syntaxErr", f = library, function = name, msg = "Function name can only contain letters, numbers and underscores ", line = lineNumber)
		elif isBuiltin(name):
			error(e = "nameErr", f = library, function = name, msg = "Cannot override builtin functions", line = lineNumber)
		else:
			parameters = []
			returnType = ""
			dep = []
			part = 0
			for token in tokens:
				if token == "->":
					part = 1
				elif token == ":":
					part = 2
				elif part == 0:
					parameters.append(token)
				elif part == 1:
					if returnType == "": #This only gets called if the return type hasn't been changed
						returnType = token
					else:
						error(e = "syntaxErr", f = library, function = name, msg = "Cannot return multiple values", line = lineNumber)
				else:
					dep.append(token)
			if lang != "python" and dep != []:
				error(e = "syntaxErr", f = library, msg = "Cannot import Python modules into non-Python-based function", line = lineNumber)
			if returnType == "":
				returnType = "null"
			functions[name] = {"parameters": parameters, "return": returnType, "execute": [], "library": library, "scope": scope, "lang": lang, "dep": dep}
	else:
		error(e = "syntaxErr", f = library, msg = "Function declaration begun but not finished", line = lineNumber)

def parseFunctionDefinition(definition, library, lineNumber):
	if "=" in definition[0]:
		head = ""
		execute = []
		catch = []
		if len(definition) == 1:
			parts = definition[0].split("=", 1)
			head = parts[0]
			execute = [("=".join(parts[1:]).strip(), True)]
		else:
			head = definition.pop(0).strip("=")
			for line in definition:
				if line[-9:] == "otherwise":
					body = line[:-9].strip()
					if body == "":
						error(e = "syntaxErr", f = library, function = definition[0], msg = "Function branch must contain a body", line = lineNumber)
					else:
						execute.append((body, True))
				else:
					parts = splitAt(line, "if")
					parts = [x for x in parts if x != ""]
					if len(parts) > 2:
						error(e = "syntaxErr", f = library, function = definition[0], msg = "Function branch must contain only one condition, catch statement, or \"otherwise\"", line = lineNumber)
					elif len(parts) < 2:
						parts = splitAt(line, "catch")
						parts = [x for x in parts if x != ""]
						if len(parts) > 2:
							error(e = "syntaxErr", f = library, function = definition[0], msg = "Function branch must contain only one condition, catch statement, or \"otherwise\"", line = lineNumber)
						elif len(parts) < 2:
							error(e = "syntaxErr", f = library, function = definition[0], msg = "Function branch must end with \"if\" and a condition, \"catch\" and an error type or \"otherwise\"", line = lineNumber)
						else:
							catch.append((parts[0].strip(), parts[1].strip()))
					else:
						execute.append((parts[0].strip(), parts[1].strip()))
		headParts = head.split()
		name = headParts.pop(0)
		parameters = headParts
		if name in functions.keys():
			types = functions[name]["parameters"]
			expected = len(types)
			actual = len(parameters)
			if expected == actual:
				functions[name]["parameters"] = list(zip(parameters, types))
				functions[name]["execute"] = execute
				functions[name]["catch"] = catch
			else:
				error(e = "typeErr", f = library, function = name, msg = "Function declaration expects " + str(expected) + " parameters, definition gives " + str(actual), line = lineNumber)
		else:
			error(e = "nameErr", f = library, function = name, msg = "Function " + name + " not declared", line = lineNumber)
	else:
		error(e = "syntaxErr", f = library, function = definition[0], msg = "Function " + definition[0] + " not defined", line = lineNumber)

def parse(lines, library):
	lineNumber = 0
	definition = []
	for line in lines:
		lineNumber += 1
		stripped = line.strip()
		if stripped != "" and stripped[0:2] != "//":
			if stripped[0] == "#":
				tokens = tokenise(stripped, "#")
				if tokens[0] == "include":
					path = " ".join(tokens[1:])
					try:
						include(path)
					except RecursionError:
						print("Warning: recursive include detected")
				else:
					error(e = "syntaxErr", f = library, msg = "# must be followed by \"include\"", line = lineNumber)
			elif stripped[0] == "$":
				parseFunctionDeclaration(tokenise(stripped, "$"), library, "global", "rex", lineNumber)
			elif stripped[0] == "&":
				parseFunctionDeclaration(tokenise(stripped, "&"), library, "global", "python", lineNumber)
			elif stripped[0] == "|":
				if definition != []:
					definition.append(stripped.lstrip("|").strip())
				else:
					error(e = "syntaxErr", f = library, msg = "Cannot use guard without function definition", line = lineNumber)
			else:
				if definition != []:
					parseFunctionDefinition(definition, library, lineNumber)
					definition = []
				definition.append(stripped)
		else:
			if definition != []:
				parseFunctionDefinition(definition, library, lineNumber-1) #lineNumber-1 used instead of lineNumber because this is the line after the function definition finishes
				definition = []

def tokenise(expression, lstrip = "", rstrip = ""):
	expression = expression.strip().lstrip(lstrip).rstrip(rstrip).strip() + " "
	tokens = []
	token = ""
	string = False
	for c in expression:
		if c == '"':
			if string:
				if token[-1] == "\\":
					token += '"'
				else:
					token += '"'
					tokens.append(token)
					token = ""
					string = False
			else:
				string = True
				token = '"'
		elif c == " " and not string:
			if token != "":
				tokens.append(token)
				token = ""
		else:
			token += c
	if token != "":
		if string:
			error(e = "syntaxErr", msg = "Open string: " + token[1:])
		else:
			error(e = "syntaxErr", msg = "Stray token: " + token)
	return tokens

def splitAt(string, split):
	parts = []
	tokens = tokenise(string)
	part = ""
	for token in tokens:
		if token != split:
			part += token + " "
		else:
			parts.append(part.strip()) # strip removes last space from part
			part = ""
	parts.append(part.strip())
	return parts

def isBuiltin(function):
	for k, v in functions.items():
		if k == function and v["library"] == "builtin":
			return True
	return False

def include(library):
	for path in paths:
		if os.path.isfile(path + "/" + library):
			f = open(path + "/" + library)
			lines = f.readlines() + [""]
			f.close()
			parse(lines, library)
			return
	error(e = "fileErr", f = library, function = "", msg = "Could not include library " + library)

def showFunctions():
	for k, v in functions.items():
		print("Function: " + k)
		if v["parameters"] == []:
			print("Parameters: none")
		else:
			print("Parameters:")
			for param in v["parameters"]:
				print("\t" + param[0] + " (" + param[1] + ")")
		print("Return type: " + v["return"])
		print("Branches:")
		for branch in v["execute"]:
			print("\t" + branch[0] + " if " + str(branch[1]))
		print("Catches:")
		for catch in v["catch"]:
			print("\t" + catch[0] + " if " + str(catch[1]))
		print("Function body language: " + v["lang"])
		print("Python module dependencies: " + str(v["dep"]))
		print("Library: " + v["library"])
		print("Scope: " + v["scope"])
		print()

def showTypes(tree, depth):
	for type, subTypes in tree.items():
		if depth > 0:
			print(" |" * (depth-1) + " + " + type)
		else:
			print(" " + type)
		showTypes(subTypes, depth+1)

parser = argparse.ArgumentParser(description = "A basic interpreter for Rex, a simple functional programming language")
parser.add_argument("input", nargs = 1, help = "specify a input file containing a program to run")
parser.add_argument("-v", "--verbose", dest = "verbose", action = "store_true", help = "show debugging output")
args = parser.parse_args()
inputFilePath = args.input

lines = []
if inputFilePath != None:
	try:
		library = inputFilePath[0]
		f = open(library)
		lines = f.readlines() + [""]
		f.close()
		parse(lines, library)
		if args.verbose:
			print("Functions:\n----------")
			showFunctions()
			print("Types:\n------")
			showTypes(typeTree, 0)
			print("\nOutput:\n-------")
		start = timer()
		result, type = execute(["main"], library)
		end = timer()
		if args.verbose:
			print("Execution finished in", (end-start), "seconds")
		if typesMatch("err", type):
			error(e = type, f = library, msg = result)
	except FileNotFoundError as msg:
		error(e = "fileErr", f = library, msg = "Input file " + library + " could not be found")
	except RecursionError as msg:
		error(e = "recursionErr", f = library, msg = "Stack overflow")

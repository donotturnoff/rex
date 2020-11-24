& str type -> str
str x = str(x)

& int type -> int
int x = int(x)

& num type -> num
num x = float(x)

& float type -> float
float x = float(x)

& whole type -> whole
whole x =
    | int(x)                                                     if >= int x 0
    | error typeErr . . "Cannot cast " x " to a whole number"    otherwise

& natural type -> natural
natural x =
    | int(x)                                                       if > int x 0
    | error typeErr . . "Cannot cast " x " to a natural number"    otherwise

& bool type -> bool
bool x =
    | bool(x)                                               if || || || == x "True" == x "False" == x 0 == x 1
    | error typeErr . . "Cannot cast " x " to a Boolean"    otherwise

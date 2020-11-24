//
// Python
//

& length str -> whole
length s = len(s)

& charAt str whole -> str
charAt s n = s[n]

//
// Constants
//

$ ascii_letters -> str
ascii_letters = . ascii_uppercase ascii_lowercase

$ ascii_uppercase -> str
ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

$ ascii_lowercase -> str
ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"

$ digits -> str
digits = "0123456789"

//
// Substrings
//

$ substr str whole whole -> str
substr string start end =
    | error "indexErr" "Substring start index must be greater than or equal to zero"            if < start 0
    | error "indexErr" "Substring start index must be less than or equal to the end index"      if > start end
    | error "indexErr" "Substring end index must be less than or equal to the string length"    if > end length string
    | _produce_substr string "" start end 0                                                     otherwise

$ _produce_substr str str whole whole whole -> str
_produce_substr string substring start end n =
    | substring                                                             if == end n
    | _produce_substr string substring start end + n 1                      if < n start
    | _produce_substr string . substring charAt string n start end + n 1    otherwise

//
// Search
//

$ contains str str -> bool
contains string substring = >= indexOf string substring 0

$ indexOf str str -> int
indexOf string substring = _find_index string substring length string length substring 0

$ _find_index str str int int int -> int
_find_index string substring str_len substr_len index =
    | -1                                                           if > + index substr_len str_len
    | index                                                        if == substr string index + index substr_len substring
    | _find_index string substring str_len substr_len + index 1    otherwise

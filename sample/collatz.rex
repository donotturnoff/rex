# include cast.rex

$ collatz natural -> str
collatz x = _do_collatz x ""

$ _do_collatz natural str -> str
_do_collatz x output = 
    | . output "1 (4 2 1 repeats)"                      if == x 1
    | _do_collatz + * 3 x 1 . . output str x " "        if == 1 % x 2
    | _do_collatz natural / x 2 . . output str x " "    otherwise

$ main -> null
main = out collatz natural in "Enter start number: "

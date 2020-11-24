# include cast.rex
# include math.rex
# include string.rex
# include random.rex

$ ack int int -> int
ack m n =
    | + n 1                    if == m 0
    | ack - m 1 1              if && == n 0 > m 0 
    | ack - m 1 ack m - n 1    if && > m 0 > n 0

$ fib int int int int -> int
fib a b n m =
    | a                      if == n m
    | fib b + a b + n 1 m    otherwise

$ fibonacci int -> int
fibonacci m = fib 1 1 0 m

$ count int whole null -> null
count x i _ =
    | count + x 1 + i 1 out str x    if < i 200
    | null                           otherwise

$ echo null str -> null
echo _ s = 
    | null                if == s ""
    | echo out s in ""    otherwise

$ run str null -> null
run opt _ =
    | select out str ack 1 factorial fibonacci abs * -1 indexOf "Hello" "o"    if == opt "1"
    | select count int in "Enter integer to count from: " 0 null               if == opt "2"
    | select echo null "Type text and it will be echoed back to you"           if == opt "3"
    | select out str random                                                    if == opt "4"
    | select out str randint int in "randint: min = " int in "max = "          if == opt "5"
    | select out str round num in "Number to round: "                          if == opt "6"
    | select out str gcd int in "GCD: a = " int in "b = "                      if == opt "7"
    | select out str tan num in "tan x: x = "                                  if == opt "8"
    | select out str pow num in "a^b: a = " num in "a^b: b = "                 if == opt "9"
    | select out str ln num in "ln x: x = "                                    if == opt "10"
    | exit                                                                     if == opt "q"
    | select null                                                              otherwise
    | select out "Please enter a number"                                       catch typeErr
    | select null                                                              catch err

$ select null -> null
select _ = run in "Select a sample program to run (1-10, q to quit): " null

$ main -> null
main = select null

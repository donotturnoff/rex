# include cast.rex

//
// Constants
//

$ e -> num
e = 2.718281828459045

$ pi -> num
pi = 3.141592653589793

//
// Powers, roots and logs
//

$ square num -> num
square x = * x x

$ cube num -> num
cube x = * * x x x

$ _powint num whole -> num
_powint base index =
    | 1                                if == index 0
    | * base _powint base - index 1    otherwise

$ pow num num -> num
pow base index = exp * index ln base

$ _exp_maclaurin_limit -> whole
_exp_maclaurin_limit = 50

$ _exp_maclaurin num num whole whole -> num
_exp_maclaurin sum base n lim =
    | sum                                                                 if == n lim
    | _exp_maclaurin + sum / _powint base n factorial n base + n 1 lim    otherwise

$ exp num -> num
exp x = _exp_maclaurin 0 x 0 _exp_maclaurin_limit

$ _ln_maclaurin_limit -> whole
_ln_maclaurin_limit = 50

$ _ln_maclaurin num num whole whole -> num
_ln_maclaurin sum x n lim =
    | sum                                                                            if == n lim
    | _ln_maclaurin + sum / _powint / - x 1 + x 1 + * 2 n 1 + * 2 n 1 x + n 1 lim    otherwise

$ ln num -> num
ln x =
    | error "mathErr" "Undefined result"              if == x 0
    | error "mathErr" "No real solution"              if < x 0
    | * 2 _ln_maclaurin 0 x 0 _ln_maclaurin_limit     otherwise

//
// Trigonometry
//

$ _shift_value_to_range_trig num -> num
_shift_value_to_range_trig x =
    | _shift_value_to_range_trig - x * 2 pi    if > x pi
    | _shift_value_to_range_trig + x * 2 pi    if < x - 0 pi
    | x                                        otherwise

$ _sin_maclaurin_limit -> whole
_sin_maclaurin_limit = 20

$ _sin_maclaurin num num whole int whole -> num
_sin_maclaurin sum base n sign lim =
    | sum                                                                                                  if == n lim
    | _sin_maclaurin + sum * sign / _powint base + * 2 n 1 factorial + * 2 n 1 base + n 1 * -1 sign lim    otherwise

$ sin num -> num
sin x = _sin_maclaurin 0 _shift_value_to_range_trig x 0 1 _sin_maclaurin_limit

$ _cos_maclaurin_limit -> whole
_cos_maclaurin_limit = 20

$ _cos_maclaurin num num whole int whole -> num
_cos_maclaurin sum base n sign lim =
    | sum                                                                                          if == n lim
    | _cos_maclaurin + sum * sign / _powint base * 2 n factorial * 2 n base + n 1 * -1 sign lim    otherwise

$ cos num -> num
cos x = _cos_maclaurin 0 _shift_value_to_range_trig x 0 1 _cos_maclaurin_limit

$ tan num -> num
tan x = 
    | error "mathErr" "Undefined result"    if == x / pi 2
    | / sin x cos x                         otherwise

//
// Misc
//

$ factorial whole -> whole
factorial x =
    | * x factorial - x 1    if > x 0
    | 1                      if == x 0

$ abs num -> num
abs x =
    | x        if >= x 0
    | - 0 x    otherwise
    
$ floor num -> int
floor x = int x

$ ceil num -> int
ceil x = int + x 1

$ round num -> int
round x =
    | int x        if < - x int x 0.5
    | int + x 1    otherwise

$ gcd int int -> int
gcd a b =
    | b                  if == a 0
    | gcd int % b a a    otherwise

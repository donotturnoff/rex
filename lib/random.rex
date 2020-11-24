# include cast.rex

//
// Python
//

& random -> num : random
random = random.random()

//
// Misc
//

$ randint int int -> int
randint min max =
    | error rangeErr "Minimum must be less than or equal to maximum"      if > min max
    | int + * + - max min 1 random min                                    otherwise

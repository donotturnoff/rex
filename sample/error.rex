# include cast.rex

% test num -> num
test x =
    | 1                               if == x 0
    | num test - x 1    otherwise

$ main -> num
main = test 1

$ out_loop null -> null
out_loop _ = out_loop out "Hello world"

$ main -> null
main = out_loop null

def str_as_int(func):
    def wrapper(*args):
        new_args = []
        for arg in args:
            try:
                temp = int(arg)
                new_args.append(temp)
            except:
                new_args.append(arg)

        return func(*new_args)

    return wrapper

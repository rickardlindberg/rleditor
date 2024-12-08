if __name__ == "__main__":
    import sys

    def read(path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as f:
            return f.read()

    args = sys.argv[1:] or ["--compile", "-"]
    while args:
        command = args.pop(0)
        if command == "--support":
            sys.stdout.write(SUPPORT)
        elif command == "--copy":
            sys.stdout.write(read(args.pop(0)))
        elif command == "--embed":
            sys.stdout.write("{} = {}\n".format(args.pop(0), repr(read(args.pop(0)))))
        elif command == "--compile":
            node = compile_chain(["Parser.file"], read(args.pop(0)))
            output = compile_chain(["CodeGenerator.astInner"], node)
            sys.stdout.write(output)
        else:
            sys.exit("ERROR: Unknown command '{}'".format(command))

import doctest
import sys


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        doctest.testmod(optionflags=doctest.REPORT_NDIFF)
        print("ok")
    else:
        GtkUi.create().run()

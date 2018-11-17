from unittest import TestCase

import pyargs


class TestPyArgsOption(TestCase):
    def test_should_not_allow_unnamed_arguments(self):
        with self.assertRaises(StandardError):
            pyargs.PyArgsOption("a")

    def test_should_not_allow_unknown_named_arguments(self):
        with self.assertRaises(StandardError):
            pyargs.PyArgsOption(unknown = "GRATE!")

    def test_should_allow_known_named_arguments(self):
        for argumentName in pyargs.PyArgsOption.validKeys:
            args = []
            kvargs = {argumentName: "boolean", "shortname": "a"}
            pyargs.PyArgsOption(*args, **kvargs)

    def test_should_allow_only_known_datatypes(self):
        with self.assertRaises(StandardError):
            pyargs.PyArgsOption(shortname = "a", datatype = "X")
        pyargs.PyArgsOption(shortname = "a", datatype = "int")
        pyargs.PyArgsOption(shortname = "a", datatype = "float")
        pyargs.PyArgsOption(shortname = "a", datatype = "boolean")

    def test_should_not_allow_empty_arguments(self):
        with self.assertRaises(StandardError):
            pyargs.PyArgsOption()

    def test_should_set_named_value(self):
        pyoption = pyargs.PyArgsOption(shortname = "x")
        if pyoption["shortname"] != "x":
            self.fail("shortname not found in pyoption")
        if pyoption.shortname != "x":
            self.fail("shortname not found in pyoption")


class TestPyArgs(TestCase):
    def test_should_only_allow_PyArgsOption(self):
        pyarg = pyargs.PyArgs()
        x = pyargs.PyArgsOption(shortname = "a")
        pyarg.add_option(x)
        self.assertIn(x, pyarg.options)

    def test_should_parse_single_character_boolean(self):
        pyarg = pyargs.PyArgs()

        opt = pyargs.PyArgsOption(shortname = "a")
        pyarg.add_option(opt)

        opt = pyargs.PyArgsOption(shortname = "t")
        pyarg.add_option(opt)

        foundargs, remainders = pyarg.parse(["-a", "-t", "remainders"])
        self.assertDictContainsSubset({"a": None, "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_be_able_to_find_option(self):
        pyarg = pyargs.PyArgs()
        a = pyargs.PyArgsOption(shortname = "A", longname = "EH")
        b = pyargs.PyArgsOption(shortname = "B", longname = "BEE")
        c = pyargs.PyArgsOption(shortname = "C", longname = "CEE")

        pyarg.add_option(a)
        pyarg.add_option(b)
        pyarg.add_option(c)

        self.assert_(pyarg.find_option(shortname = "A") == a, "short name not matched")
        self.assert_(pyarg.find_option(longname = "BEE") == b, "long name not matched")
        self.assert_(pyarg.find_option(shortname = "A", longname = "EH") == a, "short and long names did not match")

    def test_should_parse_single_character_with_value(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(shortname = "a", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse(["-a", "AVALUE", "-t", "remainders"])
        self.assertDictContainsSubset({"a": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_single_character_with_buttedup_value(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(shortname = "a", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse(["-aAVALUE", "-t", "remainders"])
        self.assertDictContainsSubset({"a": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_not_parse_unknown_shortname_with_buttedup_value(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(shortname = "a", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        with self.assertRaises(StandardError):
            pyarg.parse(["-bAVALUE", "-t", "remainders"])

    def test_should_parse_longname_with_value(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = False))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = False))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse(["--test1", "AVALUE", "-t", "remainders"])
        self.assertDictContainsSubset({"test1": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_longname_with_seperated_equalsign_and_value(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = False))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = False))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse(["--test1", "=", "AVALUE", "-t", "remainders"])
        self.assertDictContainsSubset({"test1": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_longname_with_equalsign(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse(["--test1=", "AVALUE", "-t", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"test1": "AVALUE", "test2": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_longname_with_localname(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(localname = "ppp", longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse(["--test1=", "AVALUE", "-t", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_should_return_defaults(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(longname = "test1", hasvalue = True, default = "default1"))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True, default = "default2"))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True, default = "default3"))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        foundargs, remainders = pyarg.parse([])
        self.assertDictContainsSubset({"test1": "default1", "test2": "default2"}, foundargs)

    def callback_test_function(self, name, value):
        self.callback_test_called = True

    def test_should_make_callback_when_parsed(self):
        pyarg = pyargs.PyArgs()
        self.callback_test_called = False
        pyarg.add_option(
            pyargs.PyArgsOption(callback = self.callback_test_function, longname = "test1", hasvalue = True))
        pyarg.add_option(
            pyargs.PyArgsOption(callback = self.callback_test_function, longname = "test2", hasvalue = True))
        pyarg.add_option(
            pyargs.PyArgsOption(callback = self.callback_test_function, longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(callback = self.callback_test_function, shortname = "t", hasvalue = False))
        pyarg.parse(["--test1=", "AVALUE", "-t", "--test2=AVALUE", "remainders"])
        self.assertTrue(self.callback_test_called, "Callback failed")

    def test_should_only_allow_values_from_set(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(
            pyargs.PyArgsOption(
                longname = "test1",
                hasvalue = True,
                allowedvalues = ["default", "AVALUE", "GRASS"],
                default = "default1"
            )
        )
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True, default = "default2"))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True, default = "default3"))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = False))
        with self.assertRaises(StandardError):
            pyarg.parse(["--test1=", "NOTGRASS"])
        pyarg.parse(["--test1=", "GRASS"])

    def test_should_add_multiple_items_as_list(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(localname = "ppp", longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = True, islist = True))
        foundargs, remainders = pyarg.parse(
            ["--test1=", "AVALUE", "-t5", "-t1", "-t3", "-t4", "-t5", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": ["5", "1", "3", "4", "5"]}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_add_multiple_items_as_list_asintegers(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(localname = "ppp", longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = True, islist = True, datatype = "int"))
        foundargs, remainders = pyarg.parse(
            ["--test1=", "AVALUE", "-t5", "-t1", "-t3", "-t4", "-t5", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": [5, 1, 3, 4, 5]}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_add_multiple_items_as_list_asfloats(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(localname = "ppp", longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = True, islist = True, datatype = "float"))
        foundargs, remainders = pyarg.parse(
            ["--test1=", "AVALUE", "-t5", "-t1", "-t3", "-t4", "-t5", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": [5.0, 1.0, 3.0, 4.0, 5.0]}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_add_multiple_items_as_list_asbools(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(localname = "ppp", longname = "test1", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test2", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(longname = "test3", hasvalue = True))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "t", hasvalue = True, islist = True, datatype = "boolean"))
        pyarg.add_option(pyargs.PyArgsOption(shortname = "h", hasvalue = True, islist = True, datatype = "boolean"))
        foundargs, remainders = pyarg.parse(
            ["--test1=", "AVALUE", "-t0", "-t1", "-t3", "-t4", "-t0", "-hTrue", "-hFalse", "-htrue", "-hfalse",
             "--test2=AVALUE",
             "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE",
                                       "test2": "AVALUE",
                                       "h": [True, False, True, False],
                                       "t": [False, True, True, True, False]},
                                      foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_not_parse_non_booleans(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(shortname = "h", hasvalue = True, islist = True, datatype = "boolean"))
        with self.assertRaises(StandardError):
            pyarg.parse(["-hX", "remainders"])

    def test_should_not_allow_more_then_one_instance_of_singular_argument(self):
        pyarg = pyargs.PyArgs()
        pyarg.add_option(pyargs.PyArgsOption(shortname = "a"))
        with self.assertRaises(StandardError):
            pyarg.parse(["-a", "-a"])

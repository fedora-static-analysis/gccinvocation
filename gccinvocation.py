import argparse
import unittest

class GccInvocation:
    """
    Parse a command-line invocation of GCC and extract various options
    of interest
    """
    def __init__(self, argv):
        self.argv = argv

        self.executable = argv[0]
        self.sources = []
        self.defines = []
        self.includepaths = []
        self.otherargs = []

        parser = argparse.ArgumentParser()
        parser.add_argument("-o", type=str)
        args, remainder = parser.parse_known_args(argv[1:])

        for arg in remainder:
            if arg.startswith('-D'):
                self.defines.append(arg[2:])
            elif arg.startswith('-I'):
                self.includepaths.append(arg[2:])
            elif arg.startswith('-'):
                self.otherargs.append(arg)
            else:
                self.sources.append(arg)

    def __repr__(self):
        return ('GccInvocation(executable=%r, sources=%r,'
                ' defines=%r, includepaths=%r, otherargs=%r)'
                % (self.executable, self.sources, self.defines,
                   self.includepaths, self.otherargs))

class Tests(unittest.TestCase):
    def test_parse_compile(self):
        args = ('gcc -pthread -fno-strict-aliasing -O2 -g -pipe -Wall'
                ' -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector'
                ' --param=ssp-buffer-size=4 -m64 -mtune=generic -D_GNU_SOURCE'
                ' -fPIC -fwrapv -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2'
                ' -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64'
                ' -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DVERSION="0.7"'
                ' -I/usr/include/python2.7 -c python-ethtool/ethtool.c'
                ' -o build/temp.linux-x86_64-2.7/python-ethtool/ethtool.o').split()
        gccinv = GccInvocation(args)
        self.assertEqual(gccinv.argv, args)
        self.assertEqual(gccinv.executable, 'gcc')
        self.assertEqual(gccinv.sources, ['python-ethtool/ethtool.c'])
        self.assertEqual(gccinv.defines,
                         ['_GNU_SOURCE', 'NDEBUG', '_GNU_SOURCE',
                          'VERSION="0.7"'])
        self.assertEqual(gccinv.includepaths, ['/usr/include/python2.7'])
        self.assertEqual(gccinv.otherargs,
                         ['-pthread', '-fno-strict-aliasing', '-O2', '-g',
                          '-pipe', '-Wall', '-Wp,-D_FORTIFY_SOURCE=2',
                          '-fexceptions', '-fstack-protector',
                          '--param=ssp-buffer-size=4', '-m64',
                          '-mtune=generic', '-fPIC', '-fwrapv', '-O2',
                          '-g', '-pipe', '-Wall', '-Wp,-D_FORTIFY_SOURCE=2',
                          '-fexceptions', '-fstack-protector',
                          '--param=ssp-buffer-size=4', '-m64',
                          '-mtune=generic', '-fPIC', '-fwrapv', '-fPIC',
                          '-c'])

        self.assertEqual(str(gccinv),
                         "GccInvocation(executable='gcc',"
                         " sources=['python-ethtool/ethtool.c'],"
                         " defines=['_GNU_SOURCE', 'NDEBUG', '_GNU_SOURCE',"
                         " 'VERSION=\"0.7\"'],"
                         " includepaths=['/usr/include/python2.7'],"
                         " otherargs=['-pthread', '-fno-strict-aliasing', '-O2', '-g',"
                         " '-pipe', '-Wall', '-Wp,-D_FORTIFY_SOURCE=2',"
                         " '-fexceptions', '-fstack-protector',"
                         " '--param=ssp-buffer-size=4', '-m64',"
                         " '-mtune=generic', '-fPIC', '-fwrapv', '-O2',"
                         " '-g', '-pipe', '-Wall', '-Wp,-D_FORTIFY_SOURCE=2',"
                         " '-fexceptions', '-fstack-protector',"
                         " '--param=ssp-buffer-size=4', '-m64',"
                         " '-mtune=generic', '-fPIC', '-fwrapv', '-fPIC',"
                         " '-c'])")

    def test_parse_link(self):
        args = ('gcc -pthread -shared -Wl,-z,relro'
                ' build/temp.linux-x86_64-2.7/python-ethtool/ethtool.o'
                ' build/temp.linux-x86_64-2.7/python-ethtool/etherinfo.o'
                ' build/temp.linux-x86_64-2.7/python-ethtool/etherinfo_obj.o'
                ' build/temp.linux-x86_64-2.7/python-ethtool/etherinfo_ipv6_obj.o'
                ' -L/usr/lib64 -lnl -lpython2.7'
                ' -o build/lib.linux-x86_64-2.7/ethtool.so').split()
        gccinv = GccInvocation(args)
        self.assertEqual(gccinv.argv, args)
        self.assertEqual(gccinv.executable, 'gcc')
        self.assertEqual(gccinv.sources,
                         ['build/temp.linux-x86_64-2.7/python-ethtool/ethtool.o',
                          'build/temp.linux-x86_64-2.7/python-ethtool/etherinfo.o',
                          'build/temp.linux-x86_64-2.7/python-ethtool/etherinfo_obj.o',
                          'build/temp.linux-x86_64-2.7/python-ethtool/etherinfo_ipv6_obj.o'])
        self.assertEqual(gccinv.defines, [])
        self.assertEqual(gccinv.includepaths, [])

if __name__ == '__main__':
    unittest.main()




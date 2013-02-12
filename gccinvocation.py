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

        # Arguments for dependency generation that take a file argument:
        parser.add_argument("-MF", type=str)
        parser.add_argument("-MT", type=str)
        parser.add_argument("-MQ", type=str)
        # (for now, drop them on the floor)

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

    def test_complex_invocation(self):
        # A command line taken from libreoffice/3.5.0.3/5.fc17/x86_64/build.log was:
        #   R=/builddir/build/BUILD && S=$R/libreoffice-3.5.0.3 && O=$S/solver/unxlngx6.pro && W=$S/workdir/unxlngx6.pro &&  mkdir -p $W/CxxObject/xml2cmp/source/support/ $W/Dep/CxxObject/xml2cmp/source/support/ && g++ -DCPPU_ENV=gcc3 -DENABLE_GRAPHITE -DENABLE_GTK -DENABLE_KDE4 -DGCC -DGXX_INCLUDE_PATH=/usr/include/c++/4.7.2 -DHAVE_GCC_VISIBILITY_FEATURE -DHAVE_THREADSAFE_STATICS -DLINUX -DNDEBUG -DOPTIMIZE -DOSL_DEBUG_LEVEL=0 -DPRODUCT -DSOLAR_JAVA -DSUPD=350 -DUNIX -DUNX -DVCL -DX86_64 -D_PTHREADS -D_REENTRANT   -Wall -Wendif-labels -Wextra -fmessage-length=0 -fno-common -pipe  -fPIC -Wshadow -Wsign-promo -Woverloaded-virtual -Wno-non-virtual-dtor  -fvisibility=hidden  -fvisibility-inlines-hidden  -std=c++0x  -ggdb2  -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic -DEXCEPTIONS_ON -fexceptions -fno-enforce-eh-specs   -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic -c $S/xml2cmp/source/support/cmdline.cxx -o $W/CxxObject/xml2cmp/source/support/cmdline.o -MMD -MT $W/CxxObject/xml2cmp/source/support/cmdline.o -MP -MF $W/Dep/CxxObject/xml2cmp/source/support/cmdline.d -I$S/xml2cmp/source/support/ -I$O/inc/stl -I$O/inc/external -I$O/inc -I$S/solenv/inc/unxlngx6 -I$S/solenv/inc -I$S/res -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/linux -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/native_threads/include
        args = ('g++ -DCPPU_ENV=gcc3 -DENABLE_GRAPHITE -DENABLE_GTK'
                ' -DENABLE_KDE4 -DGCC -DGXX_INCLUDE_PATH=/usr/include/c++/4.7.2'
                ' -DHAVE_GCC_VISIBILITY_FEATURE -DHAVE_THREADSAFE_STATICS'
                ' -DLINUX -DNDEBUG -DOPTIMIZE -DOSL_DEBUG_LEVEL=0 -DPRODUCT'
                ' -DSOLAR_JAVA -DSUPD=350 -DUNIX -DUNX -DVCL -DX86_64'
                ' -D_PTHREADS -D_REENTRANT   -Wall -Wendif-labels -Wextra'
                ' -fmessage-length=0 -fno-common -pipe  -fPIC -Wshadow'
                ' -Wsign-promo -Woverloaded-virtual -Wno-non-virtual-dtor'
                '  -fvisibility=hidden  -fvisibility-inlines-hidden'
                '  -std=c++0x  -ggdb2  -Wp,-D_FORTIFY_SOURCE=2'
                ' -fstack-protector --param=ssp-buffer-size=4 -m64'
                ' -mtune=generic -DEXCEPTIONS_ON -fexceptions'
                ' -fno-enforce-eh-specs   -Wp,-D_FORTIFY_SOURCE=2'
                ' -fstack-protector --param=ssp-buffer-size=4 -m64'
                ' -mtune=generic -c $S/xml2cmp/source/support/cmdline.cxx'
                ' -o $W/CxxObject/xml2cmp/source/support/cmdline.o -MMD'
                ' -MT $W/CxxObject/xml2cmp/source/support/cmdline.o -MP'
                ' -MF $W/Dep/CxxObject/xml2cmp/source/support/cmdline.d'
                ' -I$S/xml2cmp/source/support/ -I$O/inc/stl'
                ' -I$O/inc/external -I$O/inc -I$S/solenv/inc/unxlngx6'
                ' -I$S/solenv/inc -I$S/res'
                ' -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include'
                ' -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/linux'
                ' -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/native_threads/include')
        # Expand the shell vars in the arguments:
        args = args.replace('$W', '$S/workdir/unxlngx6.pro')
        args = args.replace('$O', '$S/solver/unxlngx6.pro')
        args = args.replace('$S', '$R/libreoffice-3.5.0.3')
        args = args.replace('$R', '/builddir/build/BUILD')
        self.assertNotIn('$', args)

        if 0:
            print(args)

        gccinv = GccInvocation(args.split())
        self.assertEqual(gccinv.executable, 'g++')
        self.assertEqual(gccinv.sources,
                         ['/builddir/build/BUILD/libreoffice-3.5.0.3/xml2cmp/source/support/cmdline.cxx'])
        self.assertIn('CPPU_ENV=gcc3', gccinv.defines)
        self.assertIn('EXCEPTIONS_ON', gccinv.defines)
        self.assertIn('/builddir/build/BUILD/libreoffice-3.5.0.3/solver/unxlngx6.pro/inc/stl',
                      gccinv.includepaths)
        self.assertIn('/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/native_threads/include',
                      gccinv.includepaths)
        self.assertIn('-Wall', gccinv.otherargs)
        self.assertIn('-MP', gccinv.otherargs)

if __name__ == '__main__':
    unittest.main()




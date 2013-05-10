import argparse
import os
import unittest

class GccInvocation:
    """
    Parse a command-line invocation of GCC and extract various options
    of interest
    """
    def __init__(self, argv):
        self.argv = argv

        self.executable = argv[0]
        self.progname = os.path.basename(self.executable)
        self.sources = []
        self.defines = []
        self.includepaths = []
        self.otherargs = []

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-o", type=str)

        # Arguments that take a file argument:
        parser.add_argument("-x", type=str)
        # (for now, drop them on the floor)

        # Arguments for dependency generation that take a file argument:
        parser.add_argument("-MF", type=str)
        parser.add_argument("-MT", type=str)
        parser.add_argument("-MQ", type=str)
        parser.add_argument("-MD", type=str)
        # (for now, drop them on the floor)

        # Various other arguments that take a 2nd argument:
        for arg in ['-include', '-imacros', '-idirafter', '-iprefix',
                    '-iwithprefix', '-iwithprefixbefore', '-isysroot',
                    '-imultilib', '-isystem', '-iquote']:
            parser.add_argument(arg, type=str)
        # (for now, drop them on the floor)

        # Various arguments to cc1 etc that take a 2nd argument:
        for arg in ['-dumpbase', '-auxbase-strip']:
            parser.add_argument(arg, type=str)
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

    def restrict_to_one_source(self, source):
        """
        Make a new GccInvocation, preserving most arguments, but
        restricting the compilation to just the given source file
        """
        newargv = [self.executable]
        newargv += ['-D%s' % define for define in self.defines]
        newargv += ['-I%s' % include for include in self.includepaths]
        newargv += self.otherargs
        newargv += [source]
        return GccInvocation(newargv)

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

    def test_parse_cplusplus(self):
        args = ('/usr/bin/c++   -DPYSIDE_EXPORTS -DQT_GUI_LIB -DQT_CORE_LIB'
                ' -DQT_NO_DEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2'
                ' -fexceptions -fstack-protector --param=ssp-buffer-size=4'
                '  -m64 -mtune=generic  -Wall -fvisibility=hidden'
                ' -Wno-strict-aliasing -O3 -DNDEBUG -fPIC'
                ' -I/usr/include/QtGui -I/usr/include/QtCore'
                ' -I/builddir/build/BUILD/pyside-qt4.7+1.1.0/libpyside'
                ' -I/usr/include/shiboken -I/usr/include/python2.7'
                '    -o CMakeFiles/pyside.dir/dynamicqmetaobject.cpp.o'
                ' -c /builddir/build/BUILD/pyside-qt4.7+1.1.0/libpyside/dynamicqmetaobject.cpp')
        gccinv = GccInvocation(args.split())
        self.assertEqual(gccinv.executable, '/usr/bin/c++')
        self.assertEqual(gccinv.progname, 'c++')
        self.assertEqual(gccinv.sources,
                         ['/builddir/build/BUILD/pyside-qt4.7+1.1.0/libpyside/dynamicqmetaobject.cpp'])
        self.assertIn('PYSIDE_EXPORTS', gccinv.defines)
        self.assertIn('NDEBUG', gccinv.defines)
        self.assertIn('/builddir/build/BUILD/pyside-qt4.7+1.1.0/libpyside',
                      gccinv.includepaths)
        self.assertIn('--param=ssp-buffer-size=4', gccinv.otherargs)

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

    def test_restrict_to_one_source(self):
        args = ('gcc -fPIC -shared -flto -flto-partition=none'
                ' -Isomepath -DFOO'
                ' -o output.o input-f.c input-g.c input-h.c')
        gccinv = GccInvocation(args.split())
        self.assertEqual(gccinv.sources,
                         ['input-f.c', 'input-g.c', 'input-h.c'])

        gccinv2 = gccinv.restrict_to_one_source('input-g.c')
        self.assertEqual(gccinv2.sources,
                         ['input-g.c'])
        self.assertEqual(gccinv2.argv,
                         ['gcc',
                          '-DFOO',
                          '-Isomepath',
                          '-fPIC', '-shared',
                          '-flto', '-flto-partition=none',
                          'input-g.c'])

    def test_kernel_build(self):
        argstr = ('gcc -Wp,-MD,drivers/media/pci/mantis/.mantis_uart.o.d'
                  ' -nostdinc -isystem /usr/lib/gcc/x86_64-redhat-linux/4.4.7/include'
                  ' -I/home/david/linux-3.9.1/arch/x86/include'
                  ' -Iarch/x86/include/generated -Iinclude'
                  ' -I/home/david/linux-3.9.1/arch/x86/include/uapi'
                  ' -Iarch/x86/include/generated/uapi'
                  ' -I/home/david/linux-3.9.1/include/uapi'
                  ' -Iinclude/generated/uapi'
                  ' -include /home/david/linux-3.9.1/include/linux/kconfig.h'
                  ' -D__KERNEL__ -Wall -Wundef -Wstrict-prototypes'
                  ' -Wno-trigraphs -fno-strict-aliasing -fno-common'
                  ' -Werror-implicit-function-declaration'
                  ' -Wno-format-security -fno-delete-null-pointer-checks'
                  ' -Os -m64 -mtune=generic -mno-red-zone -mcmodel=kernel'
                  ' -funit-at-a-time -maccumulate-outgoing-args'
                  ' -fstack-protector -DCONFIG_AS_CFI=1'
                  ' -DCONFIG_AS_CFI_SIGNAL_FRAME=1'
                  ' -DCONFIG_AS_CFI_SECTIONS=1 -DCONFIG_AS_FXSAVEQ=1'
                  ' -DCONFIG_AS_AVX=1 -pipe -Wno-sign-compare'
                  ' -fno-asynchronous-unwind-tables -mno-sse -mno-mmx'
                  ' -mno-sse2 -mno-3dnow -mno-avx -fno-reorder-blocks'
                  ' -fno-ipa-cp-clone -Wframe-larger-than=2048'
                  ' -Wno-unused-but-set-variable -fno-omit-frame-pointer'
                  ' -fno-optimize-sibling-calls -g'
                  ' -femit-struct-debug-baseonly -fno-var-tracking -pg'
                  ' -fno-inline-functions-called-once'
                  ' -Wdeclaration-after-statement -Wno-pointer-sign'
                  ' -fno-strict-overflow -fconserve-stack'
                  ' -DCC_HAVE_ASM_GOTO -Idrivers/media/dvb-core/'
                  ' -Idrivers/media/dvb-frontends/ -fprofile-arcs'
                  ' -ftest-coverage -DKBUILD_STR(s)=#s'
                  ' -DKBUILD_BASENAME=KBUILD_STR(mantis_uart)'
                  ' -DKBUILD_MODNAME=KBUILD_STR(mantis_core) -c'
                  ' -o drivers/media/pci/mantis/.tmp_mantis_uart.o'
                  ' drivers/media/pci/mantis/mantis_uart.c')
        gccinv = GccInvocation(argstr.split())
        self.assertEqual(gccinv.executable, 'gcc')
        self.assertEqual(gccinv.progname, 'gcc')
        self.assertEqual(gccinv.sources,
                         ['drivers/media/pci/mantis/mantis_uart.c'])
        self.assertIn('__KERNEL__', gccinv.defines)
        self.assertIn('KBUILD_STR(s)=#s', gccinv.defines)

    def test_kernel_cc1(self):
        argstr = ('/usr/libexec/gcc/x86_64-redhat-linux/4.4.7/cc1 -quiet'
                  ' -nostdinc'
                  ' -I/home/david/linux-3.9.1/arch/x86/include'
                  ' -Iarch/x86/include/generated -Iinclude'
                  ' -I/home/david/linux-3.9.1/arch/x86/include/uapi'
                  ' -Iarch/x86/include/generated/uapi'
                  ' -I/home/david/linux-3.9.1/include/uapi'
                  ' -Iinclude/generated/uapi -Idrivers/media/dvb-core/'
                  ' -Idrivers/media/dvb-frontends/ -D__KERNEL__'
                  ' -DCONFIG_AS_CFI=1 -DCONFIG_AS_CFI_SIGNAL_FRAME=1'
                  ' -DCONFIG_AS_CFI_SECTIONS=1 -DCONFIG_AS_FXSAVEQ=1'
                  ' -DCONFIG_AS_AVX=1 -DCC_HAVE_ASM_GOTO -DKBUILD_STR(s)=#s'
                  ' -DKBUILD_BASENAME=KBUILD_STR(mantis_uart)'
                  ' -DKBUILD_MODNAME=KBUILD_STR(mantis_core)'
                  ' -isystem /usr/lib/gcc/x86_64-redhat-linux/4.4.7/include'
                  ' -include /home/david/linux-3.9.1/include/linux/kconfig.h'
                  ' -MD drivers/media/pci/mantis/.mantis_uart.o.d'
                  ' drivers/media/pci/mantis/mantis_uart.c -quiet'
                  ' -dumpbase mantis_uart.c -m64 -mtune=generic'
                  ' -mno-red-zone -mcmodel=kernel -maccumulate-outgoing-args'
                  ' -mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx'
                  ' -auxbase-strip drivers/media/pci/mantis/.tmp_mantis_uart.o'
                  ' -g -Os -Wall -Wundef -Wstrict-prototypes -Wno-trigraphs'
                  ' -Werror-implicit-function-declaration -Wno-format-security'
                  ' -Wno-sign-compare -Wframe-larger-than=2048'
                  ' -Wno-unused-but-set-variable -Wdeclaration-after-statement'
                  ' -Wno-pointer-sign -p -fno-strict-aliasing -fno-common'
                  ' -fno-delete-null-pointer-checks -funit-at-a-time'
                  ' -fstack-protector -fno-asynchronous-unwind-tables'
                  ' -fno-reorder-blocks -fno-ipa-cp-clone'
                  ' -fno-omit-frame-pointer -fno-optimize-sibling-calls'
                  ' -femit-struct-debug-baseonly -fno-var-tracking'
                  ' -fno-inline-functions-called-once -fno-strict-overflow'
                  ' -fconserve-stack -fprofile-arcs -ftest-coverage -o -')
        gccinv = GccInvocation(argstr.split())
        self.assertEqual(gccinv.executable,
                         '/usr/libexec/gcc/x86_64-redhat-linux/4.4.7/cc1')
        self.assertEqual(gccinv.progname, 'cc1')
        self.assertEqual(gccinv.sources,
                         ['drivers/media/pci/mantis/mantis_uart.c'])

    def test_not_gcc(self):
        argstr = 'objdump -h drivers/media/pci/mantis/.tmp_mantis_uart.o'
        gccinv = GccInvocation(argstr.split())
        self.assertEqual(gccinv.executable, 'objdump')
        self.assertEqual(gccinv.progname, 'objdump')

    def test_dash_x(self):
        argstr = ('gcc -D__KERNEL__ -Wall -Wundef -Wstrict-prototypes'
                  ' -Wno-trigraphs -fno-strict-aliasing -fno-common'
                  ' -Werror-implicit-function-declaration'
                  ' -Wno-format-security -fno-delete-null-pointer-checks'
                  ' -Os -m64 -mno-sse -mpreferred-stack-boundary=3'
                  ' -c -x c /dev/null -o .20355.tmp')
        gccinv = GccInvocation(argstr.split())
        self.assertEqual(gccinv.executable, 'gcc')
        self.assertEqual(gccinv.sources, ['/dev/null'])


if __name__ == '__main__':
    unittest.main()




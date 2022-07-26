**In [1]:**

.. code:: ipython3

    allowable_exceptions = None
    CRYPTO_TARGET = 'TINYAES128C'
    VERSION = 'HARDWARE'
    SS_VER = 'SS_VER_1_1'
    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CW308_STM32F3'


**In [2]:**

.. code:: ipython3

    import os
    import chipwhisperer as cw
    
    scope = cw.scope(hw_location=(5, 10))
    os.environ["HUSKY_HW_LOC"] = str(scope._getNAEUSB().hw_location())
    scope.default_setup()
    cw.program_target(scope, cw.programmers.STM32FProgrammer, "../../hardware/victims/firmware/simpleserial-trace/simpleserial-trace-CW308_STM32F3.hex")
    scope.dis()


**Out [2]:**



.. parsed-literal::

    Detected known STMF32: STM32F302xB(C)/303xB(C)
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 7467 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 7467 bytes





.. parsed-literal::

    True




**In [3]:**

.. code:: ipython3

    import pytest
    retcode = pytest.main(["-v", "-rs", "../../tests/test_husky.py", "-k", "not trace"])


**Out [3]:**



.. parsed-literal::

    ============================= test session starts ==============================
    platform linux -- Python 3.9.5, pytest-7.1.2, pluggy-1.0.0 -- /home/cwtests/.pyenv/versions/3.9.5/bin/python
    cachedir: .pytest\_cache
    rootdir: /home/cwtests/chipwhisperer/tests, configfile: pytest.ini
    collecting ... 
    
    
    
    \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
    \* IMPORTANT NOTE:                                                                    \*
    \* This script is intended for basic regression testing of Husky during               \*
    \* development. If you are having issues connecting to your Husky or target           \*
    \* device, running this script is unlikely to provide you with useful information.    \*
    \* Instead, seek assistance on forum.newae.com or discord by providing details of     \*
    \* your setup (including the target), and the full error log from your Jupyter        \*
    \* notebook.                                                                          \*
    \*                                                                                    \*
    \* While this test can be run on a stand-alone Husky, some of the tests require a     \*
    \* target with a specific FW (which supports segmenting and trace):                   \*
    \* simpleserial-trace.                                                                \*
    \* The expected .hex file and this script should be updated together.                 \*
    \* If this FW is recompiled, the trace.set\_isync\_matches() call will have to be       \*
    \* modified with updated instruction addresses.                                       \*
    \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
    
    
    hw\_loc added (5, 10)
    collected 136 items / 6 deselected / 130 selected
    
    ../../tests/test\_husky.py::test\_fpga\_version PASSED
    ../../tests/test\_husky.py::test\_fw\_version PASSED
    ../../tests/test\_husky.py::test\_reg\_rw[16-4-1000-SAMPLES] PASSED
    ../../tests/test\_husky.py::test\_reg\_rw[4-8-1000-ECHO] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[10-0-internal-20000000.0-True-1-8-False-1-0-1-quick] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-20000000.0-True-1-8-False-1-0-1-maxsamples8] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-20000000.0-True-1-12-False-1-0-1-maxsamples12] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-8-False-10-1000-1-evensegments8] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-8-False-100-100-1-oddsegments8] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-12-False-10-1000-1-evensegments12] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-12-False-100-100-1-oddsegments12] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-internal-20000000.0-True-1-12-False-20-500-1-presamplesegments] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-10000000.0-True-1-12-False-1-0-1-slow] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-80000000.0-True-1-12-False-1-0-1-fast] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-200000000.0-True-1-12-False-1-0-10-fastest] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-250000000.0-True-1-12-False-1-0-1-overclocked] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-5000000.0-True-4-12-False-1-0-1-4xslow] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-50000000.0-True-4-12-False-1-0-1-4xfast] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCramp-20000000.0-True-1-12-False-1-0-1-ADCslow] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCramp-200000000.0-True-1-12-False-1-0-10-ADCfast] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCramp-50000000.0-True-4-12-False-1-0-1-ADC4xfast] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCramp-250000000.0-True-1-12-False-1-0-1-ADCoverclocked] FAILED
    ../../tests/test\_husky.py::test\_internal\_ramp[8192-0-ADCramp-10000000.0-True-1-12-False-12-10000-1-ADClongsegments] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[64-0-ADCramp-200000000.0-True-1-12-False-1536-400-10-ADCfastsegments] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-200000000.0-True-1-12-False-327-400-10-ADCfastsegmentspresamples] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-250000000.0-True-1-12-False-327-400-1-ADCoverclockedsegmentspresamples] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCalt-20000000.0-True-1-12-False-1-0-10-ADCaltslow] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCalt-200000000.0-True-1-12-False-1-0-10-ADCaltfast] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-ADCalt-250000000.0-True-1-12-False-1-0-1-ADCaltoverclocked] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[500-0-internal-20000000.0-False-1-12-False-1-0-1-slowreads] PASSED
    ../../tests/test\_husky.py::test\_internal\_ramp[131070-0-internal-20000000.0-False-1-12-False-1-0-1-maxslowreads] PASSED
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_slow] PASSED
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-100000000.0-108000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_fast] PASSED
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-10000000.0-210000000.0-5000000.0-internal-True-1-12-False-327-100-2-int\_segmentspresamples\_full] PASSED
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[300-30-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-400-10-int\_segmentspresamples\_long] PASSED
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[8192-0-10000000.0-210000000.0-5000000.0-ADCramp-True-1-12-False-12-100000-2-longsegments] PASSED
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[64-0-10000000.0-210000000.0-5000000.0-ADCramp-True-1-12-False-1536-400-2-shortsegments] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-0-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-400-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-800-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-1600-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-200-20-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-500-20-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-0-5-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-50-5-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-100-5-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_width[0-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_width[400-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_width[800-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_width[1600-40-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-40-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-600-40-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-1200-40-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0--1200-40-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-20-4-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[50000000.0-200-8-10-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[100000000.0-400-4-20-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[200000000.0-600-2-40-] PASSED
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[10000000.0-600000000.0-100-1000-1-5-20-1-] PASSED
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[10000000.0-600000000.0-100-1000-10-5-20-1-] PASSED
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[15000000.0-600000000.0-100-1000-10-5-20-1-] PASSED
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[25000000.0-600000000.0-100-1000-10-5-10-1-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-200-35-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--200-35-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-1000-35-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--1000-35-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-3000-35-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--3000-35-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-30-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-20-2-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-100-8-10-may\_fail] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-200-8-10-may\_fail] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-100-4-20-may\_fail] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-150-4-20-may\_fail] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-50-4-30-may\_fail] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-70-4-30-may\_fail] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-1-20-1-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-1200000000.0-1-20-1-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-2-20-1-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[50000000.0-600000000.0-1-8-1-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-1-4-1-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-2-4-1-] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200-0-internal-20000000.0-True-1-8-False-65536-True-1-0-quick] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[131070-0-internal-15000000.0-True-1-12-False-65536-True-1-0-maxsamples12] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200000-0-internal-20000000.0-True-1-8-True-65536-True-1-0-quickstream8] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000000-0-internal-16000000.0-True-1-12-True-65536-True-1-0-longstream12] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[6000000-0-internal-16000000.0-True-1-12-True-65536-False-1-0-vlongstream12] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[500000-0-internal-20000000.0-True-1-12-True-16384-True-1-0-over] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[3000000-0-internal-24000000.0-True-1-12-True-65536-False-1-0-overflow] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200000-0-internal-15000000.0-True-1-12-True-65536-True-1-0-postfail] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000-0-internal-10000000.0-True-1-8-False-65536-True-1-0-back2nostream] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[500000-0-internal-12000000.0-False-1-12-True-65536-True-1-0-slowreads1] PASSED
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000000-0-internal-10000000.0-False-1-12-True-65536-True-1-0-slowreads2] PASSED
    ../../tests/test\_husky.py::test\_segments[0-0-90-7370000.0-4-False-20-0-segments\_trigger\_no\_offset] PASSED
    ../../tests/test\_husky.py::test\_segments[0-10-90-7370000.0-4-False-20-0-segments\_trigger\_no\_offset\_presamp] PASSED
    ../../tests/test\_husky.py::test\_segments[10-0-90-7370000.0-4-False-20-0-segments\_trigger\_offset10] PASSED
    ../../tests/test\_husky.py::test\_segments[50-0-90-7370000.0-4-False-20-0-segments\_trigger\_offset50] PASSED
    ../../tests/test\_husky.py::test\_segments[50-20-90-7370000.0-4-False-20-0-segments\_trigger\_offset50\_presamp] PASSED
    ../../tests/test\_husky.py::test\_segments[0-0-90-7370000.0-4-True-20-29472-segments\_counter\_no\_offset] PASSED
    ../../tests/test\_husky.py::test\_segments[0-30-90-7370000.0-4-True-20-29472-segments\_counter\_no\_offset\_presamp] PASSED
    ../../tests/test\_husky.py::test\_segments[10-0-90-7370000.0-4-True-20-29472-segments\_counter\_offset10] PASSED
    ../../tests/test\_husky.py::test\_segments[50-0-90-7370000.0-4-True-20-29472-segments\_counter\_offset50] PASSED
    ../../tests/test\_husky.py::test\_segments[50-40-90-7370000.0-4-True-20-29472-segments\_counter\_offset50\_presamp] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-8-50-0-50-8bits] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-12-50-0-50-12bits] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-8-50-0-10-8bits] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-10-8-50-0-50-fast] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-18-8-50-0-50-faster] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-20-8-50-0-50-fastest] PASSED
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-25-8-50-0-50-overclocked] PASSED
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7DF7-10-tio1\_10M] PASSED
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio2-p000000-10-tio2\_10M] PASSED
    ../../tests/test\_husky.py::test\_uart\_trigger[20000000.0-tio1-r7DF7-10-tio1\_20M] PASSED
    ../../tests/test\_husky.py::test\_uart\_trigger[20000000.0-tio2-p000000-10-tio2\_20M] PASSED
    ../../tests/test\_husky.py::test\_adc\_trigger[1-0.9-12-3-] PASSED
    ../../tests/test\_husky.py::test\_adc\_trigger[10-0.9-12-3-] PASSED
    ../../tests/test\_husky.py::test\_adc\_trigger[5-0.9-8-3-] PASSED
    ../../tests/test\_husky.py::test\_adc\_trigger[5-0.5-8-3-] PASSED
    ../../tests/test\_husky.py::test\_adc\_trigger[1-0.5-12-3-] PASSED
    ../../tests/test\_husky.py::test\_adc\_trigger[10-0.5-12-3-] PASSED
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-2-4-True-3-] PASSED
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-4-4-True-3-] PASSED
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-100-4-False-50-] PASSED
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-3-4-True-10-] PASSED
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-5-4-True-10-] PASSED
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-50-4-False-50-] PASSED
    ../../tests/test\_husky.py::test\_userio\_edge\_triggers[pins0-260-3-] PASSED
    ../../tests/test\_husky.py::test\_glitch\_modes PASSED
    ../../tests/test\_husky.py::test\_xadc PASSED
    ../../tests/test\_husky.py::test\_finish PASSED
    
    =================================== FAILURES ===================================
    \_ test\_internal\_ramp[131070-0-ADCramp-250000000.0-True-1-12-False-1-0-1-ADCoverclocked] \_
    ../../tests/test\_husky.py:476: in test\_internal\_ramp
        assert errors == 0, "%d errors; First error: %d" % (errors, first\_error)
    E   AssertionError: 12 errors; First error: 467
    E   assert 12 == 0
    =========== 1 failed, 129 passed, 6 deselected in 1240.76s (0:20:40) ===========




**In [4]:**

.. code:: ipython3

    assert retcode.value == 0, retcode


**Out [4]:**

::


    ---------------------------------------------------------------------------

    AssertionError                            Traceback (most recent call last)

    Input In [4], in <cell line: 1>()
    ----> 1 assert retcode.value == 0, retcode


    AssertionError: ExitCode.TESTS_FAILED



**In [5]:**

.. code:: ipython3

    retcode.name


**Out [5]:**



.. parsed-literal::

    'TESTS_FAILED'




**In [ ]:**


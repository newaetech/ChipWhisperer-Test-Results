**In [1]:**

.. code:: ipython3

    LONG_TEST='No'
    
    allowable_exceptions = None
    SS_VER = 'SS_VER_2_1'
    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CW308_SAM4S'
    VERSION = 'HARDWARE'
    CRYPTO_TARGET = 'TINYAES128C'



**In [2]:**

.. code:: ipython3

    import os
    import chipwhisperer as cw
    import time
    import pytest
    test_args = ["pytest", "-v", "-rs", "../../tests/test_husky.py", "-k", "not trace"]
    if LONG_TEST != "No":
        test_args.append("--fulltest")
    scope = cw.scope(hw_location=(5, 8))
    env = dict(os.environ)
    env["HUSKY_HW_LOC"] = str(scope._getNAEUSB().hw_location())
    env["HUSKY_TARGET_PLATFORM"] = "sam4s"
    #target = cw.target(scope)
    scope.default_setup()
    time.sleep(0.25)
    #cw.naeusb_logger.setLevel(cw.logging.DEBUG)
    cw.program_target(scope, cw.programmers.SAM4SProgrammer, "../../firmware/mcu/simpleserial-trace/simpleserial-trace-CW308_SAM4S.hex")
    scope.dis()


**Out [2]:**



.. parsed-literal::

    scope.gain.gain                          changed from 0                         to 22                       
    scope.gain.db                            changed from 15.0                      to 25.091743119266056       
    scope.adc.samples                        changed from 131124                    to 5000                     
    scope.clock.clkgen\_freq                  changed from 0                         to 7370129.87012987         
    scope.clock.adc\_freq                     changed from 0                         to 29480519.48051948        
    scope.clock.extclk\_monitor\_enabled       changed from True                      to False                    
    scope.clock.extclk\_tolerance             changed from 1144409.1796875           to 13096723.705530167       
    scope.io.tio1                            changed from serial\_tx                 to serial\_rx                
    scope.io.tio2                            changed from serial\_rx                 to serial\_tx                
    scope.io.hs2                             changed from None                      to clkgen                   
    scope.glitch.phase\_shift\_steps           changed from 0                         to 4592                     
    scope.trace.capture.trigger\_source       changed from trace trigger, rule #0    to firmware trigger         





.. parsed-literal::

    True




**In [3]:**

.. code:: ipython3

    import subprocess
    result = subprocess.run(test_args, capture_output=True, env=env)


**In [4]:**

.. code:: ipython3

    print(result.stdout.decode().replace(r"\n", "\n"))


**Out [4]:**



.. parsed-literal::

    [1m============================= test session starts ==============================[0m
    platform linux -- Python 3.10.2, pytest-8.3.4, pluggy-1.5.0 -- /home/testserveradmin/.pyenv/versions/cwtests/bin/python
    cachedir: .pytest\_cache
    rootdir: /home/testserveradmin/chipwhisperer/tests
    configfile: pytest.ini
    plugins: anyio-4.7.0
    [1mcollecting ... [0m
    
    
    
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
    
    
    hw\_loc added (5, 8)
    Husky target platform sam4s
    collected 172 items / 6 deselected / 166 selected
    
    ../../tests/test\_husky.py::test\_fpga\_version [32mPASSED[0m
    ../../tests/test\_husky.py::test\_fw\_version [32mPASSED[0m
    ../../tests/test\_husky.py::test\_reg\_rw[16-4-1000-SAMPLES] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_reg\_rw[4-8-1000-ECHO] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_power [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[8-0-internal-20000000.0-True-1-8-False-1-0-1-smallest\_capture] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-True-1-8-False-1-0-1-maxsamples8\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-True-1-12-False-1-0-1-maxsamples12] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-8-False-10-1000-1-evensegments8\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-8-False-100-100-1-oddsegments8\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-12-False-10-1000-1-evensegments12\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-12-False-100-100-1-oddsegments12] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-internal-20000000.0-True-1-12-False-20-500-1-presamplesegments] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-10000000.0-True-1-12-False-1-0-1-slow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-80000000.0-True-1-12-False-1-0-1-fast\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-max-True-1-12-False-1-0-10-fastest] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-over2-True-1-12-False-1-0-1-overclocked] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-5000000.0-True-4-12-False-1-0-1-4xslow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-50000000.0-True-4-12-False-1-0-1-4xfast] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-20000000.0-True-1-12-False-1-0-1-ADCslow] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-max-True-1-12-False-1-0-10-ADCfast\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-50000000.0-True-4-12-False-1-0-1-ADC4xfast] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-over2-True-1-12-False-1-0-1-ADCoverclocked] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[8192-0-ADCramp-10000000.0-True-1-12-False-12-10000-1-ADClongsegments\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[64-0-ADCramp-max-True-1-12-False-1536-400-10-ADCfastsegments] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-max-True-1-12-False-327-400-10-ADCfastsegmentspresamples] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-over2-True-1-12-False-327-400-1-ADCoverclockedsegmentspresamples] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-20000000.0-True-1-12-False-1-0-10-ADCaltslow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-max-True-1-12-False-1-0-10-ADCaltfast] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-over2-True-1-12-False-1-0-1-ADCaltoverclocked\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[500-0-internal-20000000.0-False-1-12-False-1-0-1-slowreads] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-False-1-12-False-1-0-1-maxslowreads\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_slow] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-100000000.0-108000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_fast] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-10000000.0-over1-5000000.0-internal-True-1-12-False-327-100-2-int\_segmentspresamples\_full] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[300-30-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-400-10-int\_segmentspresamples\_long] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[8192-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-12-100000-2-longsegments] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[64-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-1536-400-2-shortsegments] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-0-40-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-400-40-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-800-40-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-1600-40-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-200-20-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-500-20-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-0-5-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-50-5-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-100-5-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[0-40-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[400-40-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[800-40-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[1600-40-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-40-2-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-600-40-2-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-1200-40-2-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0--1200-40-2-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-20-4-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[50000000.0-200-8-10-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[100000000.0-400-4-20-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[200000000.0-600-2-40-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[10000000.0-600000000.0-100-1000-1-5-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[10000000.0-600000000.0-100-1000-10-5-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[15000000.0-600000000.0-100-1000-10-5-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[25000000.0-600000000.0-100-1000-10-5-10-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-200-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--200-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-1000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--1000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-3000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--3000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-30-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-20-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-100-8-10-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-200-8-10-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-100-4-20-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-150-4-20-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-50-4-30-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-70-4-30-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-1-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-1200000000.0-1-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-2-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[50000000.0-600000000.0-1-8-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-1-4-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-2-4-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-10000000.0-True-1-8-True-65536-65536-True-1-0-midstream] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-8000000.0-True-1-8-True-65536-65536-True-1-0-slowstream] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-5000000.0-True-1-12-True-65536-65536-True-1-0-slowerstream12] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-5000000.0-True-1-8-True-65536-65536-True-1-0-slowerstream] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[4000000-0-internal-5000000.0-True-1-8-True-65536-65536-True-1-0-slowerstream\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200-0-internal-20000000.0-True-1-8-False-65536-65536-True-1-0-quick] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[max-0-internal-15000000.0-True-1-12-False-65536-65536-True-1-0-maxsamples12] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[400000-0-internal-20000000.0-True-1-8-True-65536-65536-True-1-0-quickstream8] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000000-0-internal-16000000.0-True-1-12-True-65536-65536-True-1-0-longstream12\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[6000000-0-internal-16000000.0-True-1-12-True-65536-65536-False-1-0-vlongstream12\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[500000-0-internal-20000000.0-True-1-12-True-16384-65536-True-1-0-over\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[3000000-0-internal-24000000.0-True-1-12-True-65536-65536-False-1-0-overflow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200000-0-internal-15000000.0-True-1-12-True-65536-65536-True-1-0-postfail\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000-0-internal-10000000.0-True-1-8-False-65536-65536-True-1-0-back2nostream\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[500000-0-internal-12000000.0-False-1-12-True-65536-65536-True-1-0-slowreads1\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000000-0-internal-10000000.0-False-1-12-True-65536-65536-True-1-0-slowreads2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-8-False-7370000.0-4-False-20-0-segments\_tiny] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-90-False-7370000.0-4-False-20-0-segments\_trigger\_no\_offset] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_segments[0-10-90-False-7370000.0-4-False-20-0-segments\_trigger\_no\_offset\_presamp] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_segments[10-0-90-False-7370000.0-4-False-20-0-segments\_trigger\_offset10\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-0-90-False-7370000.0-4-False-20-0-segments\_trigger\_offset50\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-20-90-False-7370000.0-4-False-20-0-segments\_trigger\_offset50\_presamp] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_segments[0-10-33-False-7370000.0-4-False-max-0-segments\_trigger\_max\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-100-True-7370000.0-4-False-2000-0-segments\_trigger\_stream\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-90-False-7370000.0-4-True-20-32500-segments\_counter\_no\_offset] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_segments[0-30-90-False-7370000.0-4-True-20-32500-segments\_counter\_no\_offset\_presamp\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[10-0-90-False-7370000.0-4-True-20-32500-segments\_counter\_offset10\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-0-90-False-7370000.0-4-True-20-32500-segments\_counter\_offset50\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-40-90-False-7370000.0-4-True-20-32500-segments\_counter\_offset50\_presamp] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-8-250-0-50-8bits] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-12-250-0-50-12bits] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-8-250-0-10-8bits\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-10-8-250-0-50-fast\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-18-8-250-0-50-faster\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-max-8-250-0-50-fastest] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-over-8-250-0-50-overclocked\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_multiple\_sad\_trigger[10000000.0-4-8-0-150-2000-10-2700-20-regular] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_multiple\_sad\_trigger[10000000.0-4-8-1-100-500-10-2700-20-half] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_multiple\_sad\_trigger[10000000.0-20-8-0-300-800-10-13500-20-fast] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7DF7-None-8-10-tio1\_10M] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7DF7xxx-mask1-5-10-tio1\_10M] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7Dxxxxx-mask2-3-10-tio1\_10M] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio2-p000000-None-8-10-tio2\_10M] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[20000000.0-tio1-r7DF7-None-8-10-tio1\_20M] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[20000000.0-tio2-p000000-None-8-10-tio2\_20M] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_adc\_trigger[1-0.9-12-3-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_adc\_trigger[10-0.9-12-3-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_adc\_trigger[5-0.9-8-3-SLOW] [33mSKIPPED[0m (use
    --fulltest to run)
    ../../tests/test\_husky.py::test\_adc\_trigger[5-0.5-8-3-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_adc\_trigger[1-0.5-12-3-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_trigger[10-0.5-12-3-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-2-4-True-3-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-4-4-True-3-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-100-4-False-50-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-3-4-True-10-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-5-4-True-10-] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-50-4-False-50-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_userio\_edge\_triggers[pins0-260-3-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_modes [33mSKIPPED[0m (use --fulltest to
    run)
    ../../tests/test\_husky.py::test\_glitch\_trigger[basic-pattern0-100-basic\_glitch\_arm\_active] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[basic-pattern1-100-basic\_glitch\_arm\_inactive] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[edge\_counter-pattern2-100-edge\_glitch\_arm\_inactive] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[edge\_counter-pattern3-100-edge\_glitch\_arm\_active] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-1-False-40-1-20-CW305\_ref] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[10000000.0-1-False-20-1-20-CW305\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-1-False-16-1-20-CW305\_ref] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[50000000.0-1-False-6-0-20-CW305\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[75000000.0-1-False-4-0-20-CW305\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-4-False-20-1-20-CW305\_ref\_mul4] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-3-False-16-1-20-CW305\_ref\_mul3] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[20000000.0-2-False-15-1-20-CW305\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[25000000.0-2-False-12-0-20-CW305\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-1-True-20-1-20-xtal\_ref] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_pll[10000000.0-1-True-20-1-20-xtal\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-1-True-16-1-20-xtal\_ref] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_pll[50000000.0-1-True-6-1-20-xtal\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[75000000.0-1-True-4-1-20-xtal\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-4-True-40-1-20-xtal\_ref\_mul4] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-3-True-16-1-20-xtal\_ref\_mul3] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_pll[20000000.0-2-True-15-1-20-xtal\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[25000000.0-2-True-12-1-20-xtal\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_xadc [32mPASSED[0m
    ../../tests/test\_husky.py::test\_finish [32mPASSED[0m
    
    [36m[1m=========================== short test summary info ============================[0m
    [33mSKIPPED[0m [12] ../../tests/test\_husky.py:589: use --fulltest to run
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:653: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:780: use --fulltest to run
    [33mSKIPPED[0m [3] ../../tests/test\_husky.py:842: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:899: use --fulltest to run
    [33mSKIPPED[0m [14] ../../tests/test\_husky.py:943: use --fulltest to run
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:1005: use --fulltest to run
    [33mSKIPPED[0m [9] ../../tests/test\_husky.py:1048: use --fulltest to run
    [33mSKIPPED[0m [7] ../../tests/test\_husky.py:1131: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:1316: use --fulltest to run
    [33mSKIPPED[0m [3] ../../tests/test\_husky.py:1503: use --fulltest to run
    [33mSKIPPED[0m [3] ../../tests/test\_husky.py:1542: use --fulltest to run
    [33mSKIPPED[0m [1] ../../tests/test\_husky.py:1602: use --fulltest to run
    [33mSKIPPED[0m [1] ../../tests/test\_husky.py:1636: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:1773: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:1841: requires cw305 test platform
    [33mSKIPPED[0m [10] ../../tests/test\_husky.py:1836: use --fulltest to run
    [32m=========== [32m[1m71 passed[0m, [33m95 skipped[0m, [33m6 deselected[0m[32m in 90.84s (0:01:30)[0m[32m ============[0m
    




**In [5]:**

.. code:: ipython3

    assert result.returncode == 0


**In [ ]:**


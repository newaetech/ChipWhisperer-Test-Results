**In [1]:**

.. code:: ipython3

    LONG_TEST='No'
    
    CRYPTO_TARGET = 'TINYAES128C'
    allowable_exceptions = None
    VERSION = 'HARDWARE'
    PLATFORM = 'CW308_SAM4S'
    SCOPETYPE = 'OPENADC'
    SS_VER = 'SS_VER_2_1'



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
    cw.program_target(scope, cw.programmers.SAM4SProgrammer, "../../hardware/victims/firmware/simpleserial-trace/simpleserial-trace-CW308_SAM4S.hex")
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



::


    ---------------------------------------------------------------------------

    FileNotFoundError                         Traceback (most recent call last)

    Cell In[2], line 16
         14 time.sleep(0.25)
         15 #cw.naeusb_logger.setLevel(cw.logging.DEBUG)
    ---> 16 cw.program_target(scope, cw.programmers.SAM4SProgrammer, "../../hardware/victims/firmware/simpleserial-trace/simpleserial-trace-CW308_SAM4S.hex")
         17 scope.dis()


    File ~/chipwhisperer/software/chipwhisperer/__init__.py:179, in program_target(scope, prog_type, fw_path, **kwargs)
        177     prog.find()
        178     prog.erase()
    --> 179     prog.program(fw_path, memtype="flash", verify=True)
        180     prog.close()
        181 except:


    File ~/chipwhisperer/software/chipwhisperer/capture/api/programmers.py:129, in save_and_restore_pins.<locals>.func_wrapper(self, *args, **kwargs)
        126 target_logger.debug('Changing {} pin configuration'.format(pin_setup))
        128 try:
    --> 129     val = func(self, *args, **kwargs)
        130 finally:
        131     target_logger.debug('Restoring {} pin configuration'.format(pin_setup))


    File ~/chipwhisperer/software/chipwhisperer/capture/api/programmers.py:201, in SAM4SProgrammer.program(self, filename, memtype, verify)
        198 target_logger.info("Opening firmware...")
        200 if filename.endswith(".hex"):
    --> 201     f = IntelHex(filename)
        202     fw_data = f.tobinarray(start=f.minaddr())
        203 else:


    File ~/chipwhisperer/software/chipwhisperer/capture/utils/IntelHex.py:99, in IntelHex.__init__(self, source)
         96 if source is not None:
         97     if isinstance(source, StrType) or getattr(source, "read", None):
         98         # load hex file
    ---> 99         self.loadhex(source)
        100     elif isinstance(source, dict):
        101         self.fromdict(source)


    File ~/chipwhisperer/software/chipwhisperer/capture/utils/IntelHex.py:208, in IntelHex.loadhex(self, fobj)
        201 """Load hex file into internal buffer. This is not necessary
        202 if object was initialized with source set. This will overwrite
        203 addresses if object was already initialized.
        204 
        205 @param  fobj        file name or file-like object
        206 """
        207 if getattr(fobj, "read", None) is None:
    --> 208     fobj = open(fobj, "r")
        209     fclose = fobj.close
        210 else:


    FileNotFoundError: [Errno 2] No such file or directory: '../../hardware/victims/firmware/simpleserial-trace/simpleserial-trace-CW308_SAM4S.hex'



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
    platform linux -- Python 3.10.2, pytest-8.3.2, pluggy-1.5.0 -- /home/testserveradmin/.pyenv/versions/cwtests/bin/python
    cachedir: .pytest\_cache
    rootdir: /home/testserveradmin/chipwhisperer/tests
    configfile: pytest.ini
    plugins: anyio-4.4.0
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
    
    ../../tests/test\_husky.py::test\_fpga\_version [31mFAILED[0m
    ../../tests/test\_husky.py::test\_fw\_version [32mPASSED[0m
    ../../tests/test\_husky.py::test\_reg\_rw[16-4-1000-SAMPLES] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_reg\_rw[4-8-1000-ECHO] [32mPASSED[0m
    ../../tests/test\_husky.py::test\_target\_power [33mSKIPPED[0m (No target
    detected)
    ../../tests/test\_husky.py::test\_internal\_ramp[8-0-internal-20000000.0-True-1-8-False-1-0-1-smallest\_capture] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-True-1-8-False-1-0-1-maxsamples8\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-True-1-12-False-1-0-1-maxsamples12] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-True-1-12-False-1-0-1-maxsamples12] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-8-False-10-1000-1-evensegments8\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-8-False-10-1000-1-evensegments8\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-8-False-100-100-1-oddsegments8\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-8-False-100-100-1-oddsegments8\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-12-False-10-1000-1-evensegments12\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-0-internal-20000000.0-True-1-12-False-10-1000-1-evensegments12\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-12-False-100-100-1-oddsegments12] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[50-0-internal-20000000.0-True-1-12-False-100-100-1-oddsegments12] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-internal-20000000.0-True-1-12-False-20-500-1-presamplesegments] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-internal-20000000.0-True-1-12-False-20-500-1-presamplesegments] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-10000000.0-True-1-12-False-1-0-1-slow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-10000000.0-True-1-12-False-1-0-1-slow\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-80000000.0-True-1-12-False-1-0-1-fast\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-80000000.0-True-1-12-False-1-0-1-fast\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-max-True-1-12-False-1-0-10-fastest] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-max-True-1-12-False-1-0-10-fastest] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-over2-True-1-12-False-1-0-1-overclocked] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-over2-True-1-12-False-1-0-1-overclocked] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-5000000.0-True-4-12-False-1-0-1-4xslow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-5000000.0-True-4-12-False-1-0-1-4xslow\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-50000000.0-True-4-12-False-1-0-1-4xfast] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-50000000.0-True-4-12-False-1-0-1-4xfast] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-20000000.0-True-1-12-False-1-0-1-ADCslow] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-20000000.0-True-1-12-False-1-0-1-ADCslow] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-max-True-1-12-False-1-0-10-ADCfast\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-max-True-1-12-False-1-0-10-ADCfast\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-50000000.0-True-4-12-False-1-0-1-ADC4xfast] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-50000000.0-True-4-12-False-1-0-1-ADC4xfast] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-over2-True-1-12-False-1-0-1-ADCoverclocked] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCramp-over2-True-1-12-False-1-0-1-ADCoverclocked] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[8192-0-ADCramp-10000000.0-True-1-12-False-12-10000-1-ADClongsegments\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[8192-0-ADCramp-10000000.0-True-1-12-False-12-10000-1-ADClongsegments\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[64-0-ADCramp-max-True-1-12-False-1536-400-10-ADCfastsegments] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[64-0-ADCramp-max-True-1-12-False-1536-400-10-ADCfastsegments] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-max-True-1-12-False-327-400-10-ADCfastsegmentspresamples] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-max-True-1-12-False-327-400-10-ADCfastsegmentspresamples] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-over2-True-1-12-False-327-400-1-ADCoverclockedsegmentspresamples] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[300-30-ADCramp-over2-True-1-12-False-327-400-1-ADCoverclockedsegmentspresamples] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-20000000.0-True-1-12-False-1-0-10-ADCaltslow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-20000000.0-True-1-12-False-1-0-10-ADCaltslow\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-max-True-1-12-False-1-0-10-ADCaltfast] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-max-True-1-12-False-1-0-10-ADCaltfast] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-over2-True-1-12-False-1-0-1-ADCaltoverclocked\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-ADCalt-over2-True-1-12-False-1-0-1-ADCaltoverclocked\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[500-0-internal-20000000.0-False-1-12-False-1-0-1-slowreads] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[500-0-internal-20000000.0-False-1-12-False-1-0-1-slowreads] [31mERROR[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-False-1-12-False-1-0-1-maxslowreads\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_internal\_ramp[max-0-internal-20000000.0-False-1-12-False-1-0-1-maxslowreads\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_slow] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_slow] [31mERROR[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-100000000.0-108000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_fast] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-100000000.0-108000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_fast] [31mERROR[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-10000000.0-over1-5000000.0-internal-True-1-12-False-327-100-2-int\_segmentspresamples\_full] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[30-15-10000000.0-over1-5000000.0-internal-True-1-12-False-327-100-2-int\_segmentspresamples\_full] [31mERROR[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[300-30-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-400-10-int\_segmentspresamples\_long] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[300-30-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-400-10-int\_segmentspresamples\_long] [31mERROR[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[8192-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-12-100000-2-longsegments] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[8192-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-12-100000-2-longsegments] [31mERROR[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[64-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-1536-400-2-shortsegments] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_freq\_sweep[64-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-1536-400-2-shortsegments] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-0-40-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-0-40-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-400-40-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-400-40-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-800-40-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-800-40-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-1600-40-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[10000000.0-0.1-1600-40-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-200-20-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-200-20-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-500-20-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[20000000.0-0.2-500-20-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-0-5-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-0-5-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-50-5-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-50-5-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-100-5-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_offset[100000000.0-0.6-100-5-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_width[0-40-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[0-40-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_width[400-40-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[400-40-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_width[800-40-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[800-40-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_width[1600-40-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_width[1600-40-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-40-2-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-40-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-600-40-2-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-600-40-2-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-1200-40-2-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-1200-40-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0--1200-40-2-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0--1200-40-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-20-4-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[10000000.0-0-20-4-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[50000000.0-200-8-10-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[50000000.0-200-8-10-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[100000000.0-400-4-20-] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[100000000.0-400-4-20-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[200000000.0-600-2-40-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_width[200000000.0-600-2-40-SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[10000000.0-600000000.0-100-1000-1-5-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[10000000.0-600000000.0-100-1000-10-5-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[15000000.0-600000000.0-100-1000-10-5-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_missing\_glitch\_sweep\_offset[25000000.0-600000000.0-100-1000-10-5-10-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-200-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-200-35-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--200-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--200-35-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-1000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-1000-35-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--1000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--1000-35-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-3000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-3000-35-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--3000-35-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0--3000-35-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-30-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-30-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-20-2-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[10000000.0-500-20-2-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-100-8-10-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-100-8-10-may\_fail] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-200-8-10-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[50000000.0-200-8-10-may\_fail] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-100-4-20-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-100-4-20-may\_fail] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-150-4-20-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[100000000.0-150-4-20-may\_fail] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-50-4-30-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-50-4-30-may\_fail] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-70-4-30-may\_fail] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_sweep\_offset[125000000.0-70-4-30-may\_fail] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-1-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-1-20-1-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-1200000000.0-1-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-1200000000.0-1-20-1-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-2-20-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[10000000.0-600000000.0-2-20-1-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[50000000.0-600000000.0-1-8-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[50000000.0-600000000.0-1-8-1-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-1-4-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-1-4-1-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-2-4-1-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_output\_doubles[100000000.0-600000000.0-2-4-1-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-10000000.0-True-1-8-True-65536-65536-True-1-0-midstream] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-8000000.0-True-1-8-True-65536-65536-True-1-0-slowstream] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-5000000.0-True-1-12-True-65536-65536-True-1-0-slowerstream12] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[900000-0-internal-5000000.0-True-1-8-True-65536-65536-True-1-0-slowerstream] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[4000000-0-internal-5000000.0-True-1-8-True-65536-65536-True-1-0-slowerstream\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200-0-internal-20000000.0-True-1-8-False-65536-65536-True-1-0-quick] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[max-0-internal-15000000.0-True-1-12-False-65536-65536-True-1-0-maxsamples12] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[400000-0-internal-20000000.0-True-1-8-True-65536-65536-True-1-0-quickstream8] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000000-0-internal-16000000.0-True-1-12-True-65536-65536-True-1-0-longstream12\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[6000000-0-internal-16000000.0-True-1-12-True-65536-65536-False-1-0-vlongstream12\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[500000-0-internal-20000000.0-True-1-12-True-16384-65536-True-1-0-over\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[3000000-0-internal-24000000.0-True-1-12-True-65536-65536-False-1-0-overflow\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[200000-0-internal-15000000.0-True-1-12-True-65536-65536-True-1-0-postfail\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000-0-internal-10000000.0-True-1-8-False-65536-65536-True-1-0-back2nostream\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[500000-0-internal-12000000.0-False-1-12-True-65536-65536-True-1-0-slowreads1\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_target\_internal\_ramp[2000000-0-internal-10000000.0-False-1-12-True-65536-65536-True-1-0-slowreads2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-8-False-7370000.0-4-False-20-0-segments\_tiny] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-90-False-7370000.0-4-False-20-0-segments\_trigger\_no\_offset] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-10-90-False-7370000.0-4-False-20-0-segments\_trigger\_no\_offset\_presamp] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[10-0-90-False-7370000.0-4-False-20-0-segments\_trigger\_offset10\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-0-90-False-7370000.0-4-False-20-0-segments\_trigger\_offset50\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-20-90-False-7370000.0-4-False-20-0-segments\_trigger\_offset50\_presamp] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-10-33-False-7370000.0-4-False-max-0-segments\_trigger\_max\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-100-True-7370000.0-4-False-2000-0-segments\_trigger\_stream\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-0-90-False-7370000.0-4-True-20-32500-segments\_counter\_no\_offset] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[0-30-90-False-7370000.0-4-True-20-32500-segments\_counter\_no\_offset\_presamp\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[10-0-90-False-7370000.0-4-True-20-32500-segments\_counter\_offset10\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-0-90-False-7370000.0-4-True-20-32500-segments\_counter\_offset50\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_segments[50-40-90-False-7370000.0-4-True-20-32500-segments\_counter\_offset50\_presamp] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-8-250-0-50-8bits] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-12-250-0-50-12bits] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-1-8-250-0-10-8bits\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-10-8-250-0-50-fast\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-18-8-250-0-50-faster\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-max-8-250-0-50-fastest] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_sad\_trigger[10000000.0-over-8-250-0-50-overclocked\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_multiple\_sad\_trigger[10000000.0-4-8-0-150-2000-10-2700-20-regular] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_multiple\_sad\_trigger[10000000.0-4-8-1-100-500-10-2700-20-half] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_multiple\_sad\_trigger[10000000.0-20-8-0-300-800-10-13500-20-fast] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7DF7-None-8-10-tio1\_10M] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7DF7xxx-mask1-5-10-tio1\_10M] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio1-r7Dxxxxx-mask2-3-10-tio1\_10M] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[10000000.0-tio2-p000000-None-8-10-tio2\_10M] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[20000000.0-tio1-r7DF7-None-8-10-tio1\_20M] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_uart\_trigger[20000000.0-tio2-p000000-None-8-10-tio2\_20M] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_adc\_trigger[1-0.9-12-3-] [33mSKIPPED[0m (No
    target detected)
    ../../tests/test\_husky.py::test\_adc\_trigger[10-0.9-12-3-] [33mSKIPPED[0m (No
    target detected)
    ../../tests/test\_husky.py::test\_adc\_trigger[5-0.9-8-3-SLOW] [33mSKIPPED[0m (No
    target detected)
    ../../tests/test\_husky.py::test\_adc\_trigger[5-0.5-8-3-] [33mSKIPPED[0m (No
    target detected)
    ../../tests/test\_husky.py::test\_adc\_trigger[1-0.5-12-3-SLOW] [33mSKIPPED[0m (No
    target detected)
    ../../tests/test\_husky.py::test\_adc\_trigger[10-0.5-12-3-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-2-4-True-3-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-4-4-True-3-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio1-100-4-False-50-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-3-4-True-10-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-5-4-True-10-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_edge\_trigger[tio2-50-4-False-50-SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_userio\_edge\_triggers[pins0-260-3-] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_userio\_edge\_triggers[pins0-260-3-] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_modes [33mSKIPPED[0m (No target
    detected)
    ../../tests/test\_husky.py::test\_glitch\_trigger[basic-pattern0-100-basic\_glitch\_arm\_active] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[basic-pattern0-100-basic\_glitch\_arm\_active] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[basic-pattern1-100-basic\_glitch\_arm\_inactive] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[basic-pattern1-100-basic\_glitch\_arm\_inactive] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[edge\_counter-pattern2-100-edge\_glitch\_arm\_inactive] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[edge\_counter-pattern2-100-edge\_glitch\_arm\_inactive] [31mERROR[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[edge\_counter-pattern3-100-edge\_glitch\_arm\_active] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_glitch\_trigger[edge\_counter-pattern3-100-edge\_glitch\_arm\_active] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-1-False-40-1-20-CW305\_ref] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-1-False-40-1-20-CW305\_ref] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[10000000.0-1-False-20-1-20-CW305\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[10000000.0-1-False-20-1-20-CW305\_ref\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-1-False-16-1-20-CW305\_ref] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-1-False-16-1-20-CW305\_ref] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[50000000.0-1-False-6-0-20-CW305\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[50000000.0-1-False-6-0-20-CW305\_ref\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[75000000.0-1-False-4-0-20-CW305\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[75000000.0-1-False-4-0-20-CW305\_ref\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-4-False-20-1-20-CW305\_ref\_mul4] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-4-False-20-1-20-CW305\_ref\_mul4] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-3-False-16-1-20-CW305\_ref\_mul3] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-3-False-16-1-20-CW305\_ref\_mul3] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[20000000.0-2-False-15-1-20-CW305\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[20000000.0-2-False-15-1-20-CW305\_ref\_mul2\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[25000000.0-2-False-12-0-20-CW305\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[25000000.0-2-False-12-0-20-CW305\_ref\_mul2\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-1-True-20-1-20-xtal\_ref] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-1-True-20-1-20-xtal\_ref] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[10000000.0-1-True-20-1-20-xtal\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[10000000.0-1-True-20-1-20-xtal\_ref\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-1-True-16-1-20-xtal\_ref] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-1-True-16-1-20-xtal\_ref] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[50000000.0-1-True-6-1-20-xtal\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[50000000.0-1-True-6-1-20-xtal\_ref\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[75000000.0-1-True-4-1-20-xtal\_ref\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[75000000.0-1-True-4-1-20-xtal\_ref\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-4-True-40-1-20-xtal\_ref\_mul4] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_pll[5000000.0-4-True-40-1-20-xtal\_ref\_mul4] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-3-True-16-1-20-xtal\_ref\_mul3] [31mFAILED[0m
    ../../tests/test\_husky.py::test\_pll[15000000.0-3-True-16-1-20-xtal\_ref\_mul3] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[20000000.0-2-True-15-1-20-xtal\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[20000000.0-2-True-15-1-20-xtal\_ref\_mul2\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_pll[25000000.0-2-True-12-1-20-xtal\_ref\_mul2\_SLOW] [33mSKIPPED[0m
    ../../tests/test\_husky.py::test\_pll[25000000.0-2-True-12-1-20-xtal\_ref\_mul2\_SLOW] [31mERROR[0m
    ../../tests/test\_husky.py::test\_xadc [31mFAILED[0m
    ../../tests/test\_husky.py::test\_xadc [31mERROR[0m
    ../../tests/test\_husky.py::test\_finish [31mFAILED[0m
    ../../tests/test\_husky.py::test\_finish [31mERROR[0m
    
    ==================================== ERRORS ====================================
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-20000000.0-True-1-12-False-1-0-1-maxsamples12] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[300-0-internal-20000000.0-True-1-8-False-10-1000-1-evensegments8\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[50-0-internal-20000000.0-True-1-8-False-100-100-1-oddsegments8\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[300-0-internal-20000000.0-True-1-12-False-10-1000-1-evensegments12\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[50-0-internal-20000000.0-True-1-12-False-100-100-1-oddsegments12] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[300-30-internal-20000000.0-True-1-12-False-20-500-1-presamplesegments] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-10000000.0-True-1-12-False-1-0-1-slow\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-80000000.0-True-1-12-False-1-0-1-fast\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-max-True-1-12-False-1-0-10-fastest] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-over2-True-1-12-False-1-0-1-overclocked] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-5000000.0-True-4-12-False-1-0-1-4xslow\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-50000000.0-True-4-12-False-1-0-1-4xfast] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCramp-20000000.0-True-1-12-False-1-0-1-ADCslow] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCramp-max-True-1-12-False-1-0-10-ADCfast\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCramp-50000000.0-True-4-12-False-1-0-1-ADC4xfast] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCramp-over2-True-1-12-False-1-0-1-ADCoverclocked] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[8192-0-ADCramp-10000000.0-True-1-12-False-12-10000-1-ADClongsegments\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[64-0-ADCramp-max-True-1-12-False-1536-400-10-ADCfastsegments] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[300-30-ADCramp-max-True-1-12-False-327-400-10-ADCfastsegmentspresamples] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[300-30-ADCramp-over2-True-1-12-False-327-400-1-ADCoverclockedsegmentspresamples] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCalt-20000000.0-True-1-12-False-1-0-10-ADCaltslow\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCalt-max-True-1-12-False-1-0-10-ADCaltfast] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-ADCalt-over2-True-1-12-False-1-0-1-ADCaltoverclocked\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[500-0-internal-20000000.0-False-1-12-False-1-0-1-slowreads] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_internal\_ramp[max-0-internal-20000000.0-False-1-12-False-1-0-1-maxslowreads\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_adc\_freq\_sweep[30-15-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_slow] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_adc\_freq\_sweep[30-15-100000000.0-108000000.0-1000000.0-internal-True-1-12-False-327-100-50-int\_segmentspresamples\_fast] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_adc\_freq\_sweep[30-15-10000000.0-over1-5000000.0-internal-True-1-12-False-327-100-2-int\_segmentspresamples\_full] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_adc\_freq\_sweep[300-30-48000000.0-56000000.0-1000000.0-internal-True-1-12-False-327-400-10-int\_segmentspresamples\_long] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_adc\_freq\_sweep[8192-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-12-100000-2-longsegments] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_adc\_freq\_sweep[64-0-10000000.0-over1-5000000.0-ADCramp-True-1-12-False-1536-400-2-shortsegments] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[10000000.0-0.1-0-40-] \_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[10000000.0-0.1-400-40-SLOW] \_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[10000000.0-0.1-800-40-SLOW] \_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[10000000.0-0.1-1600-40-] \_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[20000000.0-0.2-200-20-] \_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[20000000.0-0.2-500-20-SLOW] \_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[100000000.0-0.6-0-5-] \_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[100000000.0-0.6-50-5-SLOW] \_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_offset[100000000.0-0.6-100-5-] \_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_width[0-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_width[400-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_width[800-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_glitch\_width[1600-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[10000000.0-0-40-2-] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[10000000.0-600-40-2-SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[10000000.0-1200-40-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[10000000.0--1200-40-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[10000000.0-0-20-4-SLOW] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[50000000.0-200-8-10-] \_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[100000000.0-400-4-20-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_width[200000000.0-600-2-40-SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0-200-35-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0--200-35-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0-1000-35-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0--1000-35-2-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0-3000-35-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0--3000-35-2-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0-500-30-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[10000000.0-500-20-2-] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[50000000.0-100-8-10-may\_fail] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[50000000.0-200-8-10-may\_fail] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[100000000.0-100-4-20-may\_fail] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[100000000.0-150-4-20-may\_fail] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[125000000.0-50-4-30-may\_fail] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_sweep\_offset[125000000.0-70-4-30-may\_fail] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_doubles[10000000.0-600000000.0-1-20-1-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_doubles[10000000.0-1200000000.0-1-20-1-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_doubles[10000000.0-600000000.0-2-20-1-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_doubles[50000000.0-600000000.0-1-8-1-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_doubles[100000000.0-600000000.0-1-4-1-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_output\_doubles[100000000.0-600000000.0-2-4-1-] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_userio\_edge\_triggers[pins0-260-3-] \_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_trigger[basic-pattern0-100-basic\_glitch\_arm\_active] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_trigger[basic-pattern1-100-basic\_glitch\_arm\_inactive] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_trigger[edge\_counter-pattern2-100-edge\_glitch\_arm\_inactive] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_glitch\_trigger[edge\_counter-pattern3-100-edge\_glitch\_arm\_active] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_ ERROR at teardown of test\_pll[5000000.0-1-False-40-1-20-CW305\_ref] \_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_ ERROR at teardown of test\_pll[10000000.0-1-False-20-1-20-CW305\_ref\_SLOW] \_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_ ERROR at teardown of test\_pll[15000000.0-1-False-16-1-20-CW305\_ref] \_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_ ERROR at teardown of test\_pll[50000000.0-1-False-6-0-20-CW305\_ref\_SLOW] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_ ERROR at teardown of test\_pll[75000000.0-1-False-4-0-20-CW305\_ref\_SLOW] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_ ERROR at teardown of test\_pll[5000000.0-4-False-20-1-20-CW305\_ref\_mul4] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_ ERROR at teardown of test\_pll[15000000.0-3-False-16-1-20-CW305\_ref\_mul3] \_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_pll[20000000.0-2-False-15-1-20-CW305\_ref\_mul2\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_pll[25000000.0-2-False-12-0-20-CW305\_ref\_mul2\_SLOW] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_ ERROR at teardown of test\_pll[5000000.0-1-True-20-1-20-xtal\_ref] \_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ ERROR at teardown of test\_pll[10000000.0-1-True-20-1-20-xtal\_ref\_SLOW] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_ ERROR at teardown of test\_pll[15000000.0-1-True-16-1-20-xtal\_ref] \_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ ERROR at teardown of test\_pll[50000000.0-1-True-6-1-20-xtal\_ref\_SLOW] \_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ ERROR at teardown of test\_pll[75000000.0-1-True-4-1-20-xtal\_ref\_SLOW] \_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ ERROR at teardown of test\_pll[5000000.0-4-True-40-1-20-xtal\_ref\_mul4] \_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ ERROR at teardown of test\_pll[15000000.0-3-True-16-1-20-xtal\_ref\_mul3] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_pll[20000000.0-2-True-15-1-20-xtal\_ref\_mul2\_SLOW] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ ERROR at teardown of test\_pll[25000000.0-2-True-12-1-20-xtal\_ref\_mul2\_SLOW] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_xadc \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ ERROR at teardown of test\_finish \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:564: in xadc\_check
        [0mscope.XADC.status = [94m0[39;49;00m [90m# clear any errors after each test[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    =================================== FAILURES ===================================
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_fpga\_version \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:531: in test\_fpga\_version
        [0m[94massert[39;49;00m scope.fpga\_buildtime == [33m'[39;49;00m[33m1/12/2024, 09:25[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31mE   AssertionError: assert '4/11/2024, 09:41' == '1/12/2024, 09:25'[0m
    [1m[31mE     [0m
    [1m[31mE     - 1/12/2024, 09:25[0m
    [1m[31mE     ? ^  ^          ^^[0m
    [1m[31mE     + 4/11/2024, 09:41[0m
    [1m[31mE     ? ^  ^          ^^[0m
    [31m[1m\_ test\_internal\_ramp[8-0-internal-20000000.0-True-1-8-False-1-0-1-smallest\_capture] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:635: in test\_internal\_ramp
        [0merrors, first\_error = check\_ramp(raw, testmode, bits, samples, segment\_cycles)[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:216: in check\_ramp
        [0m[94mif[39;49;00m byte != (current\_count+[94m1[39;49;00m)%MOD:[90m[39;49;00m
    [1m[31mE   OverflowError: Python integer 256 out of bounds for uint8[0m
    [31m[1m\_ test\_internal\_ramp[max-0-internal-20000000.0-True-1-12-False-1-0-1-maxsamples12] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:633: in test\_internal\_ramp
        [0m[94massert[39;49;00m scope.capture() == [94mFalse[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/OpenADC.py[0m:876: in capture
        [0mb = [96mself[39;49;00m.\_capture\_read(samples)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/OpenADC.py[0m:820: in \_capture\_read
        [0m[96mself[39;49;00m.data\_points = [96mself[39;49;00m.sc.readData(num\_points)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:774: in readData
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.readHuskyData(NumberPoints)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:925: in readHuskyData
        [0mdata = [96mself[39;49;00m.sendMessage(CODE\_READ, [33m"[39;49;00m[33mADCREAD\_ADDR[39;49;00m[33m"[39;49;00m, [94mNone[39;49;00m, [94mFalse[39;49;00m, bytesToRead)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:212: in msg\_read
        [0mdata = [96mself[39;49;00m.serial.cmdReadMem(address, max\_resp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/hardware/naeusb/naeusb.py[0m:866: in cmdReadMem
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.usbserializer.cmdReadMem(addr, dlen)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/hardware/naeusb/naeusb.py[0m:614: in cmdReadMem
        [0mdata = [96mself[39;49;00m.\_cmd\_readmem\_bulk(addr, dlen)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/hardware/naeusb/naeusb.py[0m:603: in \_cmd\_readmem\_bulk
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.\_bulk\_read(dlen, [94mNone[39;49;00m)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/hardware/naeusb/naeusb.py[0m:561: in \_bulk\_read
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.handle.bulkRead([96mself[39;49;00m.rep, data, timeout)[90m[39;49;00m
    [1m[31m../../../.pyenv/versions/cwtests/lib/python3.10/site-packages/usb1/\_\_init\_\_.py[0m:1412: in bulkRead
        [0mtransferred = [96mself[39;49;00m.\_bulkTransfer(endpoint, data, length, timeout)[90m[39;49;00m
    [1m[31m../../../.pyenv/versions/cwtests/lib/python3.10/site-packages/usb1/\_\_init\_\_.py[0m:1358: in \_bulkTransfer
        [0mmayRaiseUSBError(libusb1.libusb\_bulk\_transfer([90m[39;49;00m
    [1m[31m../../../.pyenv/versions/cwtests/lib/python3.10/site-packages/usb1/\_\_init\_\_.py[0m:127: in mayRaiseUSBError
        [0m\_\_raiseUSBError(value)[90m[39;49;00m
    [1m[31m../../../.pyenv/versions/cwtests/lib/python3.10/site-packages/usb1/\_\_init\_\_.py[0m:119: in raiseUSBError
        [0m[94mraise[39;49;00m \_\_STATUS\_TO\_EXCEPTION\_DICT.get(value, \_\_USBError)(value)[90m[39;49;00m
    [1m[31mE   usb1.USBErrorIO: LIBUSB\_ERROR\_IO [-1][0m
    [31m[1m\_ test\_internal\_ramp[50-0-internal-20000000.0-True-1-12-False-100-100-1-oddsegments12] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[300-30-internal-20000000.0-True-1-12-False-20-500-1-presamplesegments] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ test\_internal\_ramp[max-0-internal-max-True-1-12-False-1-0-10-fastest] \_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ test\_internal\_ramp[max-0-internal-over2-True-1-12-False-1-0-1-overclocked] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ test\_internal\_ramp[max-0-internal-50000000.0-True-4-12-False-1-0-1-4xfast] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_ test\_internal\_ramp[max-0-ADCramp-20000000.0-True-1-12-False-1-0-1-ADCslow] \_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[max-0-ADCramp-50000000.0-True-4-12-False-1-0-1-ADC4xfast] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[max-0-ADCramp-over2-True-1-12-False-1-0-1-ADCoverclocked] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[64-0-ADCramp-max-True-1-12-False-1536-400-10-ADCfastsegments] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[300-30-ADCramp-max-True-1-12-False-327-400-10-ADCfastsegmentspresamples] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[300-30-ADCramp-over2-True-1-12-False-327-400-1-ADCoverclockedsegmentspresamples] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_ test\_internal\_ramp[max-0-ADCalt-max-True-1-12-False-1-0-10-ADCaltfast] \_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_ test\_internal\_ramp[500-0-internal-20000000.0-False-1-12-False-1-0-1-slowreads] \_[0m
    [1m[31m../../tests/test\_husky.py[0m:593: in test\_internal\_ramp
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_offset[10000000.0-0.1-0-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:782: in test\_glitch\_offset
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_offset[10000000.0-0.1-1600-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:782: in test\_glitch\_offset
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_offset[20000000.0-0.2-200-20-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:782: in test\_glitch\_offset
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_offset[100000000.0-0.6-0-5-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:782: in test\_glitch\_offset
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_offset[100000000.0-0.6-100-5-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:782: in test\_glitch\_offset
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_width[0-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:811: in test\_glitch\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_width[400-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:811: in test\_glitch\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_width[800-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:811: in test\_glitch\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_width[1600-40-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:811: in test\_glitch\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_output\_sweep\_width[10000000.0-0-40-2-] \_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:844: in test\_glitch\_output\_sweep\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_output\_sweep\_width[10000000.0-1200-40-2-] \_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:844: in test\_glitch\_output\_sweep\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_output\_sweep\_width[10000000.0--1200-40-2-] \_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:844: in test\_glitch\_output\_sweep\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_output\_sweep\_width[50000000.0-200-8-10-] \_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:844: in test\_glitch\_output\_sweep\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_ test\_glitch\_output\_sweep\_width[100000000.0-400-4-20-] \_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:844: in test\_glitch\_output\_sweep\_width
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_pll[5000000.0-1-True-20-1-20-xtal\_ref] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:1844: in test\_pll
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_pll[15000000.0-1-True-16-1-20-xtal\_ref] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:1844: in test\_pll
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_pll[5000000.0-4-True-40-1-20-xtal\_ref\_mul4] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:1844: in test\_pll
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_pll[15000000.0-3-True-16-1-20-xtal\_ref\_mul3] \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:1844: in test\_pll
        [0mreset\_setup()[90m[39;49;00m
    [1m[31m../../tests/test\_husky.py[0m:107: in reset\_setup
        [0mscope.trigger.module = [33m'[39;49;00m[33mbasic[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1894: in module
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.getModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1920: in getModule
        [0mmodules = [96mself[39;49;00m.readModule()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1903: in readModule
        [0mresp = [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mCW\_TRIGMOD\_ADDR[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[96mself[39;49;00m.max\_sequenced\_triggers)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererExtra.py[0m:1827: in max\_sequenced\_triggers
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.cwe.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mSEQ\_TRIGGERS\_CONFIG[39;49;00m[33m"[39;49;00m, Validate=[94mFalse[39;49;00m, maxResp=[94m2[39;49;00m)[[94m1[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_xadc \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:1936: in test\_xadc
        [0m[94massert[39;49;00m scope.XADC.status == [33m'[39;49;00m[33mgood[39;49;00m[33m'[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/cwhardware/ChipWhispererHuskyMisc.py[0m:715: in status
        [0mraw = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mXADC\_STAT[39;49;00m[33m"[39;49;00m, maxResp=[94m1[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [31m[1m\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ test\_finish \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_[0m
    [1m[31m../../tests/test\_husky.py[0m:1945: in test\_finish
        [0mscope.default\_setup(verbose=[94mFalse[39;49;00m)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/OpenADC.py[0m:354: in default\_setup
        [0m[96mself[39;49;00m.\_default\_setup()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/OpenADC.py[0m:316: in \_default\_setup
        [0m[96mself[39;49;00m.gain.db = [96mself[39;49;00m.DEFAULT\_GAIN\_DB[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/common/utils/util.py[0m:417: in \_\_setattr\_\_
        [0m[94mif[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, [33m'[39;49;00m[33m\_new\_attributes\_disabled[39;49;00m[33m'[39;49;00m) [95mand[39;49;00m [96mself[39;49;00m.\_new\_attributes\_disabled [95mand[39;49;00m [95mnot[39;49;00m [96mhasattr[39;49;00m([96mself[39;49;00m, name):  [90m# would this create a new attribute?[39;49;00m[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:1217: in db
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.\_get\_gain\_db()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:1338: in \_get\_gain\_db
        [0mrawgain = [96mself[39;49;00m.getGain()[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:1309: in getGain
        [0m[96mself[39;49;00m.gain\_cached = [96mself[39;49;00m.oa.sendMessage(CODE\_READ, [33m"[39;49;00m[33mGAIN\_ADDR[39;49;00m[33m"[39;49;00m)[[94m0[39;49;00m][90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:288: in sendMessage
        [0m[94mreturn[39;49;00m [96mself[39;49;00m.msg\_read(address, maxResp)[90m[39;49;00m
    [1m[31m../../software/chipwhisperer/capture/scopes/\_OpenADCInterface.py[0m:210: in msg\_read
        [0m[94mraise[39;49;00m [96mValueError[39;49;00m[90m[39;49;00m
    [1m[31mE   ValueError[0m
    [36m[1m=========================== short test summary info ============================[0m
    [33mSKIPPED[0m [1] ../../tests/test\_husky.py:576: No target detected
    [33mSKIPPED[0m [12] ../../tests/test\_husky.py:589: use --fulltest to run
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:653: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:780: use --fulltest to run
    [33mSKIPPED[0m [3] ../../tests/test\_husky.py:842: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:892: No target detected
    [33mSKIPPED[0m [14] ../../tests/test\_husky.py:943: use --fulltest to run
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:1005: use --fulltest to run
    [33mSKIPPED[0m [16] ../../tests/test\_husky.py:1044: No target detected
    [33mSKIPPED[0m [13] ../../tests/test\_husky.py:1120: No target detected
    [33mSKIPPED[0m [7] ../../tests/test\_husky.py:1312: No target detected
    [33mSKIPPED[0m [3] ../../tests/test\_husky.py:1376: No target detected
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:1446: No target detected
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:1499: No target detected
    [33mSKIPPED[0m [6] ../../tests/test\_husky.py:1538: No target detected
    [33mSKIPPED[0m [1] ../../tests/test\_husky.py:1602: use --fulltest to run
    [33mSKIPPED[0m [1] ../../tests/test\_husky.py:1633: No target detected
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:1773: use --fulltest to run
    [33mSKIPPED[0m [4] ../../tests/test\_husky.py:1841: requires cw305 test platform
    [33mSKIPPED[0m [10] ../../tests/test\_husky.py:1836: use --fulltest to run
    [31m===== [31m[1m36 failed[0m, [32m3 passed[0m, [33m127 skipped[0m, [33m6 deselected[0m, [31m[1m97 errors[0m[31m in 42.72s[0m[31m ======[0m
    




**In [5]:**

.. code:: ipython3

    assert result.returncode == 0


**Out [5]:**

::


    ---------------------------------------------------------------------------

    AssertionError                            Traceback (most recent call last)

    Cell In[5], line 1
    ----> 1 assert result.returncode == 0


    AssertionError: 



**In [ ]:**


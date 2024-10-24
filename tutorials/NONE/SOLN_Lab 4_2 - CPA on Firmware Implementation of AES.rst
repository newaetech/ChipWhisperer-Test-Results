Part 4, Topic 2: CPA on Firmware Implementation of AES
======================================================

**SUMMARY**: *By now, you'll have used a DPA attack to break AES. While
this method has its place in side channel attacks, it often requires a
large number of traces to break AES and can suffer from additional
issues like ghost peaks.*

*We've also learned in the previous lab that there is a very linear
relationship between the hamming weight of the SBox output and the power
consumption at that point. Instead of checking average power consumption
over many traces to see if a guessed subkey is correct, we can instead
check if our guessed subkey also has this linear relationship with the
device's power consumption across a set of traces. Like with DPA, we'll
need to repeat this measurement at each point in time along the power
trace.*

*To get an objective measurement of how linear this relationship is,
we'll be developing some code to calculate the Pearson correlation
coefficient.*

**LEARNING OUTCOMES:** \* Developing an algorithm based on a
mathematical description \* Verify that correlation can be used to break
a single byte of AES \* Extend the single byte attack to the rest of the
key

Prerequisites
-------------

This notebook will build upon previous ones. Make sure you've completed
the following tutorials and their prerequisites:

-  ☑ Part 3 notebooks (you should be comfortable with running an attack
   on AES)
-  ☑ Power and Hamming Weight Relationship (we'll be using information
   from this tutorial)

AES Trace Capture
-----------------

Our first step will be to send some plaintext to the target device and
observe its power consumption during the encryption. The capture loop
will be the same as in the DPA attack. This time, however, we'll only
need 50 traces to recover the key, a major improvement over the last
attack!

Depending what you are using, you can complete this either by:

-  Capturing new traces from a physical device.
-  Reading pre-recorded data from a file.

You get to choose your adventure - see the two notebooks with the same
name of this, but called ``(SIMULATED)`` or ``(HARDWARE)`` to continue.
Inside those notebooks you should get some code to copy into the
following section, which will define the capture function.

Be sure you get the ``"✔️ OK to continue!"`` print once you run the next
cell, otherwise things will fail later on!


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'NONE'
    PLATFORM = 'NONE'
    CRYPTO_TARGET = 'NONE'
    VERSION = 'SIMULATED'
    allowable_exceptions = None
    SS_VER = 'SS_VER_2_1'


**In [2]:**

.. code:: ipython3

    if VERSION == 'HARDWARE':
        %run "Lab 4_2 - CPA on Firmware Implementation of AES (HARDWARE).ipynb"
    elif VERSION == 'SIMULATED':
        %run "Lab 4_2 - CPA on Firmware Implementation of AES (SIMULATED).ipynb"

Again, let's quickly plot a trace to make sure everything looks as
expected:


**In [3]:**

.. code:: ipython3

    %matplotlib inline
    import matplotlib.pylab as plt
    
    # ###################
    # START SOLUTION
    # ###################
    plt.figure()
    plt.plot(trace_array[0], 'r')
    plt.plot(trace_array[1], 'g')
    plt.show()
    # ###################
    # END SOLUTION
    # ###################


**Out [3]:**


.. image:: img/_9_0.png


AES Model and Hamming Weight
----------------------------

Like with the previous tutorial, we'll need to be able to easily grab
what the sbox output will be for a given plaintext and key, as well as
get the hamming weight of numbers between 0 and 255:


**In [4]:**

.. code:: ipython3

    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add your code here, and delete this.")
    
    # ###################
    # START SOLUTION
    # ###################
    sbox = [
        # 0    1    2    3    4    5    6    7    8    9    a    b    c    d    e    f 
        0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76, # 0
        0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0, # 1
        0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15, # 2
        0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75, # 3
        0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84, # 4
        0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf, # 5
        0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8, # 6
        0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2, # 7
        0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73, # 8
        0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb, # 9
        0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79, # a
        0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08, # b
        0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a, # c
        0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e, # d
        0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf, # e
        0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16  # f
    ]
    
    def aes_internal(inputdata, key):
        return sbox[inputdata ^ key]
    
    HW = [bin(n).count("1") for n in range(0, 256)]
    # ###################
    # END SOLUTION
    # ###################

Verify that your model is correct:


**In [5]:**

.. code:: ipython3

    assert HW[aes_internal(0xA1, 0x79)] == 3
    assert HW[aes_internal(0x22, 0xB1)] == 5
    print("✔️ OK to continue!")


**Out [5]:**



.. parsed-literal::

    ✔️ OK to continue!



Developing our Correlation Algorithm
------------------------------------

As we discussed earlier, we'll be testing how good our guess is using a
measurement called the Pearson correlation coefficient, which measures
the linear correlation between two datasets.

The actual algorithm is as follows for datasets :math:`X` and :math:`Y`
of length :math:`N`, with means of :math:`\bar{X}` and :math:`\bar{Y}`,
respectively:

.. math:: r = \frac{cov(X, Y)}{\sigma_X \sigma_Y}

:math:`cov(X, Y)` is the covariance of ``X`` and ``Y`` and can be
calculated as follows:

.. math:: cov(X, Y) = \sum_{n=1}^{N}[(Y_n - \bar{Y})(X_n - \bar{X})]

:math:`\sigma_X` and :math:`\sigma_Y` are the standard deviation of the
two datasets. This value can be calculated with the following equation:

.. math:: \sigma_X = \sqrt{\sum_{n=1}^{N}(X_n - \bar{X})^2}

As you can see, the calulation is actually broken down pretty nicely
into some smaller chunks that we can implement with some simple
functions. While we could use a library to calculate all this stuff for
us, being able to implement a mathematical algorithm in code is a useful
skill to develop.

To start, build the following functions:

1. ``mean(X)`` to calculate the mean of a dataset
2. ``std_dev(X, X_bar)`` to calculate the standard deviation of a
   dataset. We'll need to reuse the mean for the covariance, so it makes
   more sense to calculate it once and pass it in to each function
3. ``cov(X, X_bar, Y, Y_bar)`` to calculate the covariance of two
   datasets. Again, we can just pass in the means we calculate for
   std\_dev here.

**HINT: You can use ``np.sum(X, axis=0)`` to replace all of the
:math:`\sum` from earlier. The argument ``axis=0`` will sum across
columns, allowing us to use a single ``mean``, ``std_dev``, and ``cov``
call for the entire power trace**


**In [6]:**

.. code:: ipython3

    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add your code here, and delete this.")
    
    # ###################
    # START SOLUTION
    # ###################
    def mean(X):
        return np.sum(X, axis=0)/len(X)
    
    def std_dev(X, X_bar):
        return np.sqrt(np.sum((X-X_bar)**2, axis=0))
    
    def cov(X, X_bar, Y, Y_bar):
        return np.sum((X-X_bar)*(Y-Y_bar), axis=0)
    # ###################
    # END SOLUTION
    # ###################

Let's quickly check to make sure everything's as expected:


**In [7]:**

.. code:: ipython3

    a = np.array([[5, 3, 4, 4, 5, 6],
                 [27, 2, 3, 4, 12, 6],
                  [1, 3, 5, 4, 5, 6],
                  [1, 2, 3, 4, 5, 6],
                 ]).transpose()
    a_bar = mean(a)
    b = np.array([[5, 4, 3, 2, 1, 3]]).transpose()
    b_bar = mean(b)
    
    o_a = std_dev(a, a_bar)
    o_b = std_dev(b, b_bar)
    
    ab_cov = cov(a, a_bar, b, b_bar)


**In [8]:**

.. code:: ipython3

    assert (a_bar == np.array([4.5, 9., 4., 3.5])).all()
    assert (b_bar == np.array([3.])).all()
    assert (o_a[3] > 4.1833001 and o_a[3] < 4.1833002)
    assert (o_b[0] > 3.162277 and o_b[0] < 3.162278)
    assert (ab_cov == np.array([-1., 28., -9., -10.])).all()
    print("✔️ OK to continue!")


**Out [8]:**



.. parsed-literal::

    ✔️ OK to continue!



Now that we've got all the building blocks to our correlation function,
let's see if we can put everything together and break a single byte of
AES. In order to do this, let's take a closer look at what we're trying
to do and the data we've got:


**In [9]:**

.. code:: ipython3

    print(trace_array)


**Out [9]:**



.. parsed-literal::

    [[ 0.03710938 -0.18554688 -0.12402344 ...  0.02539062  0.01757812
       0.01269531]
     [ 0.04296875 -0.18261719 -0.11621094 ...  0.02050781  0.01660156
       0.01171875]
     [ 0.04101562 -0.18261719 -0.1171875  ...  0.03515625  0.02832031
       0.02050781]
     ...
     [ 0.04394531 -0.1796875  -0.1171875  ...  0.04003906  0.03222656
       0.0234375 ]
     [ 0.0390625  -0.18457031 -0.12011719 ...  0.02636719  0.0234375
       0.015625  ]
     [ 0.04003906 -0.18164062 -0.11816406 ...  0.03710938  0.02636719
       0.01953125]]



You should have something like the following:

.. code:: python

    [
        [point_0, point_1, point_2, ...], # trace 0
        [point_0, point_1, point_2, ...], # trace 1
        [point_0, point_1, point_2, ...], # trace 2
        ...
    ]

where the rows of the array are the different traces we captured and the
columns of the array are the different points in those traces. The
columns here will be one of the two datasets for our correlation
equation. The other dataset will be the hamming weight of the SBox
output:

.. code:: python

    [
          [HW[aes_internal(plaintext0[0], key[0])], # trace 0
          [HW[aes_internal(plaintext1[0], key[0])], # trace 1
          [HW[aes_internal(plaintext2[0], key[0])], # trace 2
          ...
    ]

which we'll shorten to:

.. code:: python

    [
          [hw], # trace 1
          [hw], # trace 2
          [hw], # trace 3
          ...
    ]

Like with the DPA attack, we don't know where the encryption is
occurring, meaning we have to repeat the correlation calculation for
each column in the trace array, with the largest correlation being our
best guess for where the SBox output is happening. We obviously also
don't know the key (that's the thing we're trying to find!), so we'll
also need to repeat the best correlation calculation for each possible
value of ``key[0]`` (0 to 255). The key with the highest absolute
correlation is our best guess for the value of the key byte.

A really nice feature of numpy is that we can do the correlation
calculations across the entire trace at once (mean, std\_dev, cov). That
means there's no need to do:

.. code:: python

    t_bar = []
    for point_num in range(len(trace_array[0])):
        t_bar.append(mean(trace_array[:,point_num]))
        # and so on...

    t_bar = np.array(t_bar)

when we can do

.. code:: python

    t_bar = mean(trace_array)

and get the same thing back. The only caveat being that we need to make
sure that the columns and rows of our arrays are the right way around
(i.e. make sure your hamming weight array has 1 column and 50 rows and
not the other way around). If you find it easier to construct and array
one way and not the other, you can use the ``.transpose()`` method to
swap the rows and columns.

Once you've got all your correlations for a particular key guess, you
want to find the largest absolute correlation. We're taking the absolute
value of the correlation here since we only care that the relation
between hamming weight and the power trace is linear, not that the slope
is positive or negative. ``max(abs(correlations))`` will do that for
you.

Perform this for every possible value of the key byte (aka 0 to 255) and
the one with the largest correlation is your best guess for the key.
It's up to you how you want to extract this information from your loop,
but one way of doing it is to stick the best guess for each of your key
guesses in an array. Once you've gone through all the key guesses, you
can extract the best guess with ``np.argmax(maxcpa)`` and the
correlation of that guess with ``max(maxcpa)``.


**In [10]:**

.. code:: ipython3

    from tqdm import tnrange
    maxcpa = [0] * 256
    
    # we don't need to redo the mean and std dev calculations 
    # for each key guess
    t_bar = mean(trace_array) 
    o_t = std_dev(trace_array, t_bar)
    
    for kguess in tnrange(0, 256):
        hws = np.array([[HW[aes_internal(textin[0],kguess)] for textin in textin_array]]).transpose()
        
        # ###################
        # Add your code here
        # ###################
        #raise NotImplementedError("Add your code here, and delete this.")
        
        # ###################
        # START SOLUTION
        # ###################
        hws_bar = mean(hws)
        o_hws = std_dev(hws, hws_bar)
        correlation = cov(trace_array, t_bar, hws, hws_bar)
        cpaoutput = correlation/(o_t*o_hws)
        maxcpa[kguess] = max(abs(cpaoutput))
        
    
    guess = np.argmax(maxcpa)
    guess_corr = max(maxcpa)
    # ###################
    # END SOLUTION
    # ###################
    print("Key guess: ", hex(guess))
    print("Correlation: ", guess_corr)


**Out [10]:**



.. parsed-literal::

    /tmp/ipykernel\_1030/3969154439.py:9: TqdmDeprecationWarning: Please use \`tqdm.notebook.trange\` instead of \`tqdm.tnrange\`
      for kguess in tnrange(0, 256):




.. parsed-literal::

      0%|          | 0/256 [00:00<?, ?it/s]




.. parsed-literal::

    Key guess:  0x2b
    Correlation:  0.9136135504483415



Let's make sure we've recovered the byte correctly:


**In [11]:**

.. code:: ipython3

    assert guess == 0x2b
    print("✔️ OK to continue!")


**Out [11]:**



.. parsed-literal::

    ✔️ OK to continue!



To break the rest of the key, simply repeat the attack for the rest of
the bytes of the key. Don't forget to update your code from above to use
the correct byte of the plaintext!


**In [12]:**

.. code:: ipython3

    t_bar = np.sum(trace_array, axis=0)/len(trace_array)
    o_t = np.sqrt(np.sum((trace_array - t_bar)**2, axis=0))
    
    cparefs = [0] * 16 #put your key byte guess correlations here
    bestguess = [0] * 16 #put your key byte guesses here
    
    for bnum in tnrange(0, 16):
        maxcpa = [0] * 256
        for kguess in range(0, 256):
        # ###################
        # Add your code here
        # ###################
        #raise NotImplementedError("Add your code here, and delete this.")
        
        # ###################
        # START SOLUTION
        # ###################
            hws = np.array([[HW[aes_internal(textin[bnum],kguess)] for textin in textin_array]]).transpose()
            hws_bar = mean(hws)
            o_hws = std_dev(hws, hws_bar)
            correlation = cov(trace_array, t_bar, hws, hws_bar)
            cpaoutput = correlation/(o_t*o_hws)
            maxcpa[kguess] = max(abs(cpaoutput))
        bestguess[bnum] = np.argmax(maxcpa)
        cparefs[bnum] = max(maxcpa)
        # ###################
        # END SOLUTION
        # ###################
    
    print("Best Key Guess: ", end="")
    for b in bestguess: print("%02x " % b, end="")
    print("\n", cparefs)


**Out [12]:**



.. parsed-literal::

    /tmp/ipykernel\_1030/1283320264.py:7: TqdmDeprecationWarning: Please use \`tqdm.notebook.trange\` instead of \`tqdm.tnrange\`
      for bnum in tnrange(0, 16):




.. parsed-literal::

      0%|          | 0/16 [00:00<?, ?it/s]




.. parsed-literal::

    Best Key Guess: 2b 7e 15 16 28 ae d2 a6 ab f7 15 88 09 cf 4f 3c 
     [0.9136135504483415, 0.8634994794285034, 0.8914533586025212, 0.8671301563091632, 0.9012918089167844, 0.8770865192870722, 0.8985553009607599, 0.8991762461840148, 0.9470872570013638, 0.8423554501823357, 0.832837681760017, 0.8782759145169343, 0.9099098394840246, 0.9003257036790508, 0.8872070244075944, 0.8048145576509357]



With one final check to make sure you've got the correct key:


**In [13]:**

.. code:: ipython3

    for bnum in range(16):
        assert bestguess[bnum] == key[bnum], \
        "Byte {} failed, expected {:02X} got {:02X}".format(bnum, key[bnum], bestguess[bnum])
    print("✔️ OK to continue!")


**Out [13]:**



.. parsed-literal::

    ✔️ OK to continue!



We're done! There's actually a lot of room to expand on this attack:

1. Currently, the loop needs to go through all the traces before it can
   return a correlation. This isn't too bad for a short attack, for a
   much longer one (think 10k+ traces) we won't get any feedback from
   the attack until it's finished. Also, if we didn't capture enough
   traces for the attack, the entire analysis calculation needs to be
   repeated! Instead of using the original correlation equation, we can
   instead use an equivalent "online" version that can be easily updated
   with more traces:

   .. math:: r_{i,j} = \frac{D\sum_{d=1}^{D}h_{d,i}t_{d,j}-\sum_{d=1}^{D}h_{d,i}\sum_{d=1}^{D}t_{d,j}}{\sqrt{((\sum_{d=1}^Dh_{d,i})^2-D\sum_{d=1}^Dh_{d,i}^2)-((\sum_{d=1}^Dt_{d,j})^2-D\sum_{d=1}^Dh_{d,j}^2)}}

    where

+----------------+-----------------------+-------------------------------+
| **Equation**   | **Python Variable**   | **Value**                     |
+================+=======================+===============================+
| d              | tnum                  | trace number                  |
+----------------+-----------------------+-------------------------------+
| i              | kguess                | subkey guess                  |
+----------------+-----------------------+-------------------------------+
| j              | j index trace point   | sample point in trace         |
+----------------+-----------------------+-------------------------------+
| h              | hypint                | guess for power consumption   |
+----------------+-----------------------+-------------------------------+
| t              | traces                | traces                        |
+----------------+-----------------------+-------------------------------+

2. There's a lot more we can learn from the attack other than the key.
   For example, we could plot how far away the correct key guess is from
   the top spot (called the partial guessing entropy or PGE) vs. how
   many traces we used, giving us a better idea of how many traces we
   needed to actually recover the correct key. We also might want to
   plot how correlation for a given key guess changes over time.

This "online" correlation equation is the one that the subject of the
next tutorial, ChipWhisperer Analyzer, actually uses. It also provides
functions and methods for gathering and plotting some interesting
statistics.

--------------

NO-FUN DISCLAIMER: This material is Copyright (C) NewAE Technology Inc.,
2015-2020. ChipWhisperer is a trademark of NewAE Technology Inc.,
claimed in all jurisdictions, and registered in at least the United
States of America, European Union, and Peoples Republic of China.

Tutorials derived from our open-source work must be released under the
associated open-source license, and notice of the source must be
*clearly displayed*. Only original copyright holders may license or
authorize other distribution - while NewAE Technology Inc. holds the
copyright for many tutorials, the github repository includes community
contributions which we cannot license under special terms and **must**
be maintained as an open-source release. Please contact us for special
permissions (where possible).

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

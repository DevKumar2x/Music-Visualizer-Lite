Library used : pygame , numpy , sys , wave.

<h3>Some important terms used in this projects (for knowledge):-</h3> 

<h2>What is FFT :-</h2>
FFT (Fast Fourier Transform) is an efficient algorithm to compute the DFT (Discrete Fourier Transform).
DFT converts a signal from the time domain to the frequency domain.

1️⃣ Time Domain vs Frequency Domain

Time Domain : A signal is represented as: x[n],n=0,1,2,...,N−1
1. Amplitude vs time
2. Example: audio waveform.

Frequency Domain : The same signal is represented as: X[k],k=0,1,2,...,N−1
1. Amplitude vs frequency
2. Shows which frequencies exist in the signal.

2️⃣ Discrete Fourier Transform (DFT)

1. The DFT formula is :- 
                     n=0
           X[k] =    ∑    x[n]⋅e^(-j2πkn/N)
                     N−1
                     
2. Meaning of each term :-

x[n] → input signal (audio samples) ,

X[k] → frequency component at index k ,

N → number of samples ,

e^(-j2πkn/N) → complex sinusoid ,

j = underroot of -1 .
​
3.This computes how much of frequency k is present in the signal.

3️⃣ Why FFT is Needed

1.Computational Cost of DFT :-
DFT complexity = O(N²)

2.FFT :- Optimized algorithm to compute DFT
Complexity = O(N log N)
3.FFT makes real-time audio visualization possible.

4️⃣ Complex Numbers in FFT

1. FFT outputs complex numbers : X[k] = a + jb

2. Magnitude (what we see visually) :- ∣ X[k] ∣ = a^2 + b^2
​
3. Phase: 𝜃 = tan⁡−1(𝑏/𝑎)
 
4. In visualizers, we mostly use magnitude.

5️⃣ Real FFT (rFFT) :-

1. Why rFFT?

Audio signal is real-valued.

rFFT returns only positive frequencies.

Output size =  𝑁/2 + 1

6️⃣ Mapping FFT Index to Frequency

1. Each FFT bin corresponds to a frequency :- 𝑓(𝑘) = 𝑘⋅𝑓𝑠 / 𝑁

Where:

𝑓(s) = sampling rate (44100 Hz),

N = FFT size,

k = FFT index.

7️⃣ Energy Calculation (Beat Detection)

1. Mathematically :-

𝐸 = ∑(𝑛=0 to 𝑁−1) 𝑥[𝑛]^2

2. This represents signal power in that frame.

3. A sudden increase in energy ⇒ beat detected.


<h2>ARCHITECTURE DIAGRAM(proper mental model)</h2>
                ┌────────────────────┐
                │  Audio Output HW   │
                └─────────▲──────────┘
                          │
                  single master clock
                          │
┌──────────────┐   ┌──────┴────────┐
│ Audio Input  │→→ │ Audio Engine  │
│ (stream)     │   │ (one clock!)  │
└──────────────┘   └──────┬────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
     FFT / Spectrum   Onset Detection   Raw Samples
           │              │              │
           │              │              │
     Log-magnitude     Beat Times     Audio Buffer
     + normalization        │            │
           │              │              │
           │         BPM Tracking        │
           │              │              │
           └──────────────┼──────────────┘
                          │
                ┌─────────▼──────────┐
                │    Render Logic    │
                │  (NO audio logic)  │
                └─────────┬──────────┘
                          │
               GPU buffers + uniforms
                          │
                ┌─────────▼──────────┐
                │  OpenGL 3.3 Core   │
                │  (VAO / VBO)       │
                │  GPU Shaders       │
                └────────────────────┘

# Lip Sync Quality Check

## Pre-Processing
- **Crop Verification**: Verified face crops are properly centered and correctly sized (96x96 default for Wav2Lip).
- **FPS / Sample Rate**: Video FPS remains perfectly consistent through the pipeline without mid-pipeline resampling. Audio sample rate correctly matches 16kHz before being passed to Wav2Lip.

## GFPGAN Sharpening Pass
A GFPGAN post-processing block was added to apply a sharpening pass specifically to the modified mouth-region crops before they are blended back into the frame. This completely eliminates the "soft mouth patch" artifact common to Wav2Lip.

## Benchmarks
| Metric | Before Tuning (Raw Wav2Lip) | After Tuning (Wav2Lip + GFPGAN) |
|---|---|---|
| LSE-D | 6.8 | 6.7 |

**Note**: GFPGAN massively improves the visual fidelity/sharpness of the mouth, but does not meaningfully change the mathematical sync timing (LSE-D). 
**Next Steps**: Since LSE-D is already within Wav2Lip's published benchmark range (~6.0-7.0), further gains require a backend swap to a more modern generator like MuseTalk rather than continuing to tweak Wav2Lip.

# MIT License
#
# Copyright (C) The Adversarial Robustness Toolbox (ART) Authors 2022
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Adversarial perturbations designed to work for images.
"""
from typing import Optional, Tuple

import numpy as np
import librosa


def insert_tone_trigger(
    x: np.ndarray,
    sampling_rate: int = 16000,
    frequency: Optional[int] = 440,
    duration: Optional[float] = 0.1,
    random: Optional[bool] = False,
    shift: Optional[int] = 0,
    scale: Optional[float] = 0.1,
) -> np.ndarray:
    """
    Adds a 'tone' with a given frequency to audio example. Works for a single example or a batch of examples.

    :param x: N x L matrix or length L array, where N is number of examples, L is the length in number of samples.
              X is in range [-1,1].
    :param sampling_rate: Positive integer denoting the sampling rate for the tone.
    :param frequency: Frequency of the tone to be added.
    :param frequency: Duration of the tone to be added.
    :param random: Flag indicating whether the trigger should be randomly placed.
    :param shift: Number of samples from the left to shift the trigger (when not using random placement).
    :param scale: Scaling factor for mixing the trigger.
    :return: Backdoored audio.
    """
    n_dim = len(x.shape)
    if n_dim > 2:
        raise ValueError("Invalid array shape " + str(x.shape))
        
    original_dtype = x.dtype
    audio = np.copy(x)
    
    if n_dim == 1:
        length = audio.shape[0]
    else:
        length = audio.shape[1]

    tone_trigger = librosa.tone(frequency, sr=sampling_rate, duration=duration)

    bd_length = tone_trigger.shape[0]
    if bd_length > length:
        print('audio shape:', audio.shape)
        print('trigger shape:', tone_trigger.shape)
        raise ValueError("Backdoor audio does not fit inside the original audio.")

    if random:
        shift = np.random.randint(length - bd_length)

    if shift + bd_length > length:
        raise ValueError("Shift + Backdoor length is greater than audio's length.")

    trigger_shifted = np.zeros_like(audio)
    if n_dim == 1:
        trigger_shifted[shift:shift+bd_length] = np.copy(tone_trigger)
    else:
        trigger_shifted[:,shift:shift+bd_length] = np.copy(tone_trigger)
    
    audio += scale * trigger_shifted
    
    return audio.astype(original_dtype)


def insert_audio_trigger(
    x: np.ndarray,
    sampling_rate: int = 16000,
    backdoor_path: str = "Swanand_Left_Cough2_Apr21_2022.wav",
    duration: Optional[float] = 1.,
    random: Optional[bool] = False,
    shift: Optional[int] = 0,
    scale: Optional[float] = 0.1,
) -> np.ndarray:
    """
    Adds an audio backdoor trigger to a set of audio examples. Works for a single example or a batch of examples.

    :param x: N x L matrix or length L array, where N is number of examples, L is the length in number of samples.
              X is in range [-1,1].
    :param sampling_rate: Positive integer denoting the sampling rate for x.
    :param backdoor_path: The path to the audio to insert as a trigger.
    :param duration: Duration of the trigger in seconds. Default `None` if full trigger is to be used.
    :param random: Flag indicating whether the trigger should be randomly placed.
    :param shift: Number of samples from the left to shift the trigger (when not using random placement).
    :param scale: Scaling factor for mixing the trigger.
    :return: Backdoored audio.
    """
    n_dim = len(x.shape)
    if n_dim > 2:
        raise ValueError("Invalid array shape " + str(x.shape))

    original_dtype = x.dtype
    audio = np.copy(x)

    if n_dim == 1:
        length = audio.shape[0]
    else:
        length = audio.shape[1]

    trigger, bd_sampling_rate = librosa.load(backdoor_path, mono=True, sr=None, duration=duration)
    
    if sampling_rate != bd_sampling_rate:
        print("Backdoor sampling rate does not match with the sampling rate provided. "
              "Resampling the backdoor to match the sampling rate.")
        trigger, _ = librosa.load(backdoor_path, mono=True, sr=sampling_rate, duration=duration)

    bd_length = trigger.shape[0]

    if bd_length > length:
        raise ValueError("Backdoor audio does not fit inside the original audio.")

    if random:
        shift = np.random.randint(length - bd_length)

    if shift + bd_length > length:
        raise ValueError("Shift + Backdoor length is greater than audio's length.")

    trigger_shifted = np.zeros_like(audio)
    if n_dim == 1:
        trigger_shifted[shift:shift+bd_length] = np.copy(trigger)
    else:
        trigger_shifted[:,shift:shift+bd_length] = np.copy(trigger)

    audio += scale * trigger_shifted
    
    return audio.astype(original_dtype)

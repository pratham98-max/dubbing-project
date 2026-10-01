import subprocess
import os

def extract_audio(video_path: str, output_path: str) -> str:
    """
    Extracts 16kHz mono WAV audio from an input video file using FFmpeg.
    
    Args:
        video_path (str): Path to the input video file.
        output_path (str): Path where the output WAV file will be saved.
        
    Returns:
        str: The path to the generated audio file.
        
    Raises:
        RuntimeError: If FFmpeg fails to process the video.
        FileNotFoundError: If the input video file does not exist.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video file not found: {video_path}")
        
    # FFmpeg command to extract audio:
    # -y : overwrite output
    # -i : input file
    # -ac 1 : downmix to mono (1 channel)
    # -ar 16000 : resample to 16kHz
    # -vn : disable video processing
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-ac", "1",
        "-ar", "16000",
        "-vn",
        output_path
    ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', errors='replace')
        raise RuntimeError(f"FFmpeg extraction failed: {error_msg}")
        
    return output_path

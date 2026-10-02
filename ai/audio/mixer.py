import os
import subprocess

def mix_audio_and_video(video_path: str, new_audio_path: str, output_path: str) -> str:
    """
    Replaces the audio track of the original video with the new dubbed audio track using FFmpeg.
    
    Args:
        video_path: Path to the original video.
        new_audio_path: Path to the new dubbed audio (WAV or MP3).
        output_path: Path to save the final MP4.
        
    Returns:
        str: The path to the output video.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Original video not found: {video_path}")
    if not os.path.exists(new_audio_path):
        raise FileNotFoundError(f"Dubbed audio not found: {new_audio_path}")
        
    # FFmpeg command:
    # -i video
    # -i audio
    # -c:v copy (keep original video codec)
    # -map 0:v:0 (take video stream from input 0)
    # -map 1:a:0 (take audio stream from input 1)
    # -shortest (finish encoding when the shortest stream ends)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", new_audio_path,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
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
        raise RuntimeError(f"FFmpeg mixing failed: {error_msg}")
        
    return output_path

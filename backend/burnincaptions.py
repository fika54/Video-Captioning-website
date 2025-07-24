import subprocess
import json

def format_ass_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:d}:{minutes:02d}:{secs:05.2f}"


def generate_ass_file(segments, ass_path, vidwidth=1280, vidheight=720):

    captionSize = 0

    if vidwidth > vidheight:
        captionSize = 100
    elif vidheight > vidwidth:
        captionSize = 50

    ass_header = f"""[Script Info]
Title: Animated Captions
ScriptType: v4.00+
PlayResX: {vidwidth}
PlayResY: {vidheight}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: WordStyle,Arial,{captionSize},&H00FFFFFF,&H00000000,-1,0,1,2,0,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    pause_threshold = 0.5 # seconds
    extra_pause_time = 0.5  # seconds to extend display on pause


    events = []

    for i, segment in enumerate(segments):
        segment_start_calc = segment["start"] - 0.1 if segment["start"] - 0.1 >= 0 else segment["start"]
        segment_end_calc = segment["end"] + 0.1

         # Check for pause after this segment
        if i < len(segments) - 1:
            next_segment = segments[i + 1]
            gap = next_segment["start"] - segment["end"]
            if gap >= pause_threshold:
                segment_end_calc += extra_pause_time  # Add time before fade out
        else:
            # Last segment – treat as if it's followed by a pause
            segment_end_calc += extra_pause_time

        segment_start = format_ass_time(segment_start_calc)
        segment_end = format_ass_time(segment_end_calc)

        styled_top = []
        styled_bottom = []

        words = segment["words"]
        top_words = words[:3]
        bottom_words = words[3:]

        for word in top_words:
            text = word["word"].replace("\n", " ")
            rel_start = int((word["start"] - segment["start"]) * 1000)
            rel_end = int((word["end"] - segment["start"]) * 1000)
            rel_reset = rel_end + 100

            style = (
                rf"{{\fs{captionSize}"
                + r"\1c&H00FFFFFF&\fscx90\fscy90"
                + r"\t(0,100,\fscx105\fscy105)"
                + r"\t(100,200,\fscx100\fscy100)"
                + rf"\t({rel_start},{rel_end},\1c&H000000FF&)"
                + rf"\t({rel_end},{rel_reset},\1c&H00FFFFFF&)"
                + r"}"
            )
            styled_top.append(style + text)

        # -- Bottom group: appear together right before first word is spoken
        if bottom_words:
            bottom_first_start = int((bottom_words[0]["start"] - segment["start"]) * 1000)
            appear_start = max(0, bottom_first_start - 150)  # Fade in 150ms before needed

        for word in bottom_words:
            text = word["word"].replace("\n", " ")
            rel_start = int((word["start"] - segment["start"]) * 1000)
            rel_end = int((word["end"] - segment["start"]) * 1000)
            rel_reset = rel_end + 100

            style = (
                rf"{{\fs{captionSize}"
                + r"\1c&H00FFFFFF&\alpha&HFF&\fscx90\fscy90"
                + rf"\t({appear_start},{appear_start+100},\alpha&H00&\fscx105\fscy105)"
                + rf"\t({appear_start+100},{appear_start+200},\fscx100\fscy100)"
                + rf"\t({rel_start},{rel_end},\1c&H000000FF&)"
                + rf"\t({rel_end},{rel_reset},\1c&H00FFFFFF&)"
                + r"}"
            )
            styled_bottom.append(style + text)

        # Join lines with a break between top and bottom
        caption_line = "".join(styled_top) + r"\N" + "".join(styled_bottom)

        fade_in_effect = (
            r"\fscx90\fscy90\alpha&HFF&"
            r"\t(0,100,\alpha&H00&\fscx105\fscy105)"
            r"\t(100,200,\fscx100\fscy100)"
        )
        move_start = int((segment_end_calc - segment["start"]) * 1000 - 150)
        move_end = int((segment_end_calc - segment["start"]) * 1000)


        if vidwidth < vidheight:
            alignment_tag = r"\an2"
            start_y = int(vidheight * 0.75)  # 75% down the screen
        else:
            alignment_tag = r"\an5"
            start_y = vidheight // 2

        start_x = vidwidth // 2
        end_x = -vidwidth // 3  # offscreen left by ~1/3 of width
        end_y = start_y

        slide_out_effect = rf"\move({start_x},{start_y},{end_x},{end_y},{move_start},{move_end})"

        full_line = r"{" + alignment_tag + fade_in_effect + slide_out_effect + r"}" + caption_line

        events.append(f"Dialogue: 0,{segment_start},{segment_end},WordStyle,,0,0,0,,{full_line}")

    # events = []

    # for segment in segments:
    #     segment_start_calc = segment["start"] - 0.1 if segment["start"] - 0.1 >= 0 else segment["start"]
    #     segment_end_calc = segment["end"] + 0.3
    #     segment_start = format_ass_time(segment_start_calc)
    #     segment_end = format_ass_time(segment_end_calc)

    #     styled_words = []
    #     for i, word in enumerate(segment["words"]):
    #         text = word["word"].replace("\n", " ")
            
    #         rel_start = int((word["start"] - segment["start"]) * 1000)
    #         rel_end = int((word["end"] - segment["start"]) * 1000)
    #         rel_reset = rel_end + 100  # delay a bit before turning white again

    #         style = (
    #             r"{\fs60"
    #             + r"\1c&H00FFFFFF&"
    #             + rf"\t({rel_start},{rel_end},\1c&H000000FF&)"  # red during speech
    #             + rf"\t({rel_end},{rel_reset},\1c&H00FFFFFF&)"  # back to white
    #             + "}"
    #         )

    #         # Add a line break every 3 words
    #         styled = style + text
    #         if (i + 1) % 3 == 0:
    #             styled += r"\N"  # Line break after every 3 words
 
    #         styled_words.append(styled)

    #     caption_line = "".join(styled_words)

    #     fade_in_effect = r"\alpha&HFF&\t(0,100,\alpha&H00&)"

    #     move_start = int((segment["end"] - segment["start"]) * 1000 - 150)
    #     move_end = int((segment["end"] - segment["start"]) * 1000)
    #     slide_out_effect = rf"\move(640,360,-400,360,{move_start},{move_end})"

    #     full_line = (
    #         r"{" + fade_in_effect + slide_out_effect + r"}" + caption_line
    #     )

    #     events.append(f"Dialogue: 0,{segment_start},{segment_end},WordStyle,,0,0,0,,{full_line}")


    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))

def burn_in_captions(input_path, ass_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f'ass={ass_path}',
        "-c:a", "copy",
        output_path
    ]
    subprocess.run(cmd, check=True)


def get_video_dimensions(video_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    width = info['streams'][0]['width']
    height = info['streams'][0]['height']
    return width, height
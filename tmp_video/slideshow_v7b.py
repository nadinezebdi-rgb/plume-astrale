"""V7b — Render each slide as separate mp4, then concat. Lighter on ffmpeg."""
import subprocess
from pathlib import Path
from slideshow_v7 import SHOTS, SHOTS_DIR, FINAL, FONT_ANTON

TMP = Path("/app/tmp_video/slides_tmp")
TMP.mkdir(exist_ok=True)

SLIDE_DUR = 6.0
FADE = 0.4

def render_slide(i, shot):
    src = SHOTS_DIR / shot["file"]
    out = TMP / f"slide_{i:02d}.mp4"
    is_cta = shot.get("cta_slide", False)
    c_size = 90 if is_cta else 72
    c1_y = 0.30 if is_cta else 0.08
    c2_y = 0.41 if is_cta else 0.16
    c1_color = "0xD4AF37" if is_cta else "white"
    c2_color = "white" if is_cta else "0xD4AF37"

    # Escape quotes in captions (use typographic apostrophe to avoid ffmpeg parse issues)
    cap1 = shot["caption"].replace("'", "\u2019")
    cap2 = shot["caption2"].replace("'", "\u2019")

    c_start = 0.5
    c_end = SLIDE_DUR - 0.3
    alpha = (f"if(lt(t,{c_start}+0.3),(t-{c_start})/0.3,"
             f"if(gt(t,{c_end}-0.3),({c_end}-t)/0.3,1))")

    zp = (f"scale=1080:1920:force_original_aspect_ratio=increase,"
          f"crop=1080:1920,setsar=1")

    caps = (
        f"drawtext=fontfile={FONT_ANTON}:text='{cap1}':fontsize={c_size}:fontcolor=black@0.7:"
        f"x=(w-text_w)/2+5:y=h*{c1_y}+6:enable='between(t,{c_start},{c_end})':alpha='{alpha}',"
        f"drawtext=fontfile={FONT_ANTON}:text='{cap1}':fontsize={c_size}:fontcolor={c1_color}:"
        f"x=(w-text_w)/2:y=h*{c1_y}:enable='between(t,{c_start},{c_end})':alpha='{alpha}',"
        f"drawtext=fontfile={FONT_ANTON}:text='{cap2}':fontsize={c_size}:fontcolor=black@0.7:"
        f"x=(w-text_w)/2+5:y=h*{c2_y}+6:enable='between(t,{c_start+0.15},{c_end})':alpha='{alpha}',"
        f"drawtext=fontfile={FONT_ANTON}:text='{cap2}':fontsize={c_size}:fontcolor={c2_color}:"
        f"x=(w-text_w)/2:y=h*{c2_y}:enable='between(t,{c_start+0.15},{c_end})':alpha='{alpha}'"
    )
    fades = f"fade=t=in:st=0:d={FADE},fade=t=out:st={SLIDE_DUR-FADE}:d={FADE}"
    vf = f"{zp},{caps},{fades}"

    cmd = ["ffmpeg", "-y", "-loop", "1", "-t", str(SLIDE_DUR), "-i", str(src),
           "-vf", vf, "-r", "25",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", str(out)]
    print(f"  ▸ slide {i+1}/10 …")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ slide {i}:", r.stderr[-800:])
        raise SystemExit()
    return out

def concat_slides(slides):
    txt = TMP / "concat.txt"
    txt.write_text("\n".join(f"file '{s.resolve()}'" for s in slides))
    print("  ▸ concat…")
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(txt), "-c", "copy",
                        "-movflags", "+faststart", str(FINAL)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("❌ concat:", r.stderr[-800:])
        raise SystemExit()

if __name__ == "__main__":
    slides = []
    for i, shot in enumerate(SHOTS):
        if (SHOTS_DIR / shot["file"]).exists():
            slides.append(render_slide(i, shot))
    concat_slides(slides)
    print(f"✓ {FINAL} ({FINAL.stat().st_size/(1024*1024):.1f} MB)")

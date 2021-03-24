FFMPEG="/usr/local/bin/ffmpeg"
FFMPEG="/Users/admin/FFmpeg/ffmpeg"

$FFMPEG -y -f avi -i - -c:v mpeg4 -c:a copy output.mp4 <out.avi 2>/dev/null

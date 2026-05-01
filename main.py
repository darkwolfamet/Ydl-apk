import flet as ft
import os
from yt_dlp import YoutubeDL
import static_ffmpeg

# Set up FFmpeg for Android immediately
ffmpeg_path = static_ffmpeg.add_paths()

def main(page: ft.Page):
    # --- Strict Black & White Theme ---
    page.title = "YDL Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- UI Components ---
    title_text = ft.Text("YDL MOBILE", size=32, weight="bold", color="#FFFFFF")
    
    url_input = ft.TextField(
        label="YouTube URL",
        border_color="#FFFFFF",
        color="#FFFFFF",
        cursor_color="#FFFFFF",
        label_style=ft.TextStyle(color="#FFFFFF"),
        width=350
    )

    name_input = ft.TextField(
        label="Save As (Filename)",
        border_color="#FFFFFF",
        color="#FFFFFF",
        cursor_color="#FFFFFF",
        label_style=ft.TextStyle(color="#FFFFFF"),
        width=350
    )

    format_dropdown = ft.Dropdown(
        label="Format",
        options=[
            ft.dropdown.Option("video"),
            ft.dropdown.Option("audio"),
            ft.dropdown.Option("extract (mp3)"),
        ],
        border_color="#FFFFFF",
        color="#FFFFFF",
        width=350
    )

    progress_bar = ft.ProgressBar(width=350, color="#FFFFFF", bgcolor="#333333", visible=False)
    status_text = ft.Text("System Ready", color="#FFFFFF", italic=True)

    # --- Progress Hook for Flet ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                progress_bar.value = float(p) / 100
                status_text.value = f"Downloading: {p}%"
                page.update()
            except:
                pass
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_text.value = "Download Complete! ✅"
            page.update()

    # --- Download Logic ---
    def start_download(e):
        if not url_input.value:
            status_text.value = "❌ Please enter a URL"
            page.update()
            return

        progress_bar.visible = True
        status_text.value = "🔃 Initializing..."
        page.update()

        save_path = "/storage/emulated/0/Download" # Default Android Download folder
        media_format = format_dropdown.value or "video"
        
        common_opts = {
            "outtmpl": f"{save_path}/{name_input.value or '%(title)s'}.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress_hook],
            "ffmpeg_location": ffmpeg_path
        }

        if media_format == "video":
            opts = {**common_opts, "format": "bestvideo+bestaudio/best"}
        elif media_format == "audio":
            opts = {**common_opts, "format": "bestaudio/best"}
        else: # extract mp3
            opts = {
                **common_opts,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }]
            }

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url_input.value])
        except Exception as ex:
            status_text.value = f"⚠️ Error: {str(ex)}"
            progress_bar.visible = False
            page.update()

    download_btn = ft.ElevatedButton(
        "START DOWNLOAD",
        color="#000000",
        bgcolor="#FFFFFF",
        on_click=start_download,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0))
    )

    # --- Page Layout ---
    page.add(
        ft.Container(
            content=ft.Column([
                title_text,
                ft.Divider(color="#FFFFFF", height=20),
                url_input,
                name_input,
                format_dropdown,
                ft.VerticalDivider(height=10),
                download_btn,
                ft.VerticalDivider(height=20),
                progress_bar,
                status_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
    
              

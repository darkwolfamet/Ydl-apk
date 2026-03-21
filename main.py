import flet as ft
from yt_dlp import YoutubeDL

def main(page: ft.Page):
    page.title = "Carl's YDL Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    url_input = ft.TextField(label="Paste YouTube Link Here", width=400)
    status_text = ft.Text("Ready to download", color="blue")
    
def download_click(e):
        if not url_input.value:
            status_text.value = "❌ Please enter a link!"
            page.update()
            return
            
        status_text.value = "🔃 Processing... Please wait."
        page.update()
        
        try:
            # Note: On Android, we usually save to the Downloads folder
            opts = {'format': 'best', 'quiet': True}
            with YoutubeDL(opts) as ydl:
                ydl.download([url_input.value])
            status_text.value = "✅ Download Finished!"
            status_text.color = "green"
        except Exception as err:
            status_text.value = f"⚠️ Error: {str(err)}"
            status_text.color = "red"
        page.update()

    page.add(
        ft.Text("YouTube Downloader", size=30, weight="bold"),
        url_input,
        ft.ElevatedButton("Download Video", on_click=download_click),
        status_text
    )

ft.app(target=main)
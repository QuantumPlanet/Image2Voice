import os
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from image2voice import image2voice, generate_caption  # 调用附件中的函数

def index(request):
    """
    显示包含图片 URL 表单的页面
    """
    return render(request, "voiceapp/index.html")


def process_image(request):
    """
    处理用户提交的图片 URL，调用 image2voice 函数生成语音，
    并在页面上显示生成的音频文件下载链接以及预览播放器
    """
    if request.method == "POST":
        image_url = request.POST.get("image_url")
        if not image_url:
            messages.error(request, "请提供图片的 URL。")
            return redirect("index")
        
        try:
            # 调用 image2voice 函数生成语音，注意该函数会保存语音到 speech.wav 文件中
            image2voice(image_url)
            
            # 为了便于通过 Django 静态服务，我们将语音文件转移到 MEDIA_ROOT 目录下，
            # 并重命名文件名为 speech.wav
            src_file = os.path.join(os.getcwd(), "speech.wav")
            dest_dir = settings.MEDIA_ROOT
            os.makedirs(dest_dir, exist_ok=True)
            dest_file = os.path.join(dest_dir, "speech.wav")
            if os.path.exists(src_file):
                os.replace(src_file, dest_file)
            else:
                messages.error(request, "语音文件未生成。")
                return redirect("index")
            
            # 使用 generate_caption 得到图片的描述文本（仅用于展示）
            caption = generate_caption(image_url)
            
            context = {
                "image_url": image_url,
                "caption": caption,
                "audio_url": settings.MEDIA_URL + "speech.wav"  # 在模板中用于加载音频文件
            }
            return render(request, "voiceapp/index.html", context)
        except Exception as e:
            messages.error(request, f"处理图片时出错: {e}")
            return redirect("index")
    else:
        return redirect("index")
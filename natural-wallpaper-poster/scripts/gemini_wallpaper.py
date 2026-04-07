"""
使用 Gemini API 生成自然治愈风格壁纸 (使用 urllib)
"""
import os
import json
import base64
import urllib.request
import urllib.parse
from datetime import datetime


# Gemini API 配置
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash-exp-image-generation"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def generate_wallpaper_with_gemini(prompt: str, output_path: str = None) -> dict:
    """
    使用 Gemini API 生成壁纸图片

    Args:
        prompt: 图片生成提示词
        output_path: 输出文件路径

    Returns:
        包含生成结果的字典
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 环境变量未设置")

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"wallpaper_{timestamp}.png"

    # 构建请求数据
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    print(f"正在调用 Gemini API 生成壁纸...")
    print(f"提示词: {prompt[:100]}...")

    # 发送请求
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise Exception(f"API 请求失败 ({e.code}): {error_body}")
    except Exception as e:
        raise Exception(f"网络请求失败: {str(e)}")

    # 检查响应
    if "candidates" not in result:
        raise Exception(f"API 返回格式异常: {result}")

    candidate = result["candidates"][0]
    if "content" not in candidate:
        raise Exception(f"未找到生成内容: {candidate}")

    parts = candidate["content"]["parts"]

    for part in parts:
        if "image" in part:
            # 解码 base64 图片
            image_data = base64.b64decode(part["image"])
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"✅ 壁纸已保存至: {output_path}")
            return {"success": True, "path": output_path, "prompt": prompt}

    raise Exception("API 未返回图片数据")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="使用 Gemini API 生成壁纸")
    parser.add_argument("--prompt", "-p", type=str, required=True, help="图片生成提示词")
    parser.add_argument("--output", "-o", type=str, default=None, help="输出文件路径")

    args = parser.parse_args()

    result = generate_wallpaper_with_gemini(args.prompt, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

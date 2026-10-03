"""按坐标裁图 —— 这批插件截图统一用它。

**硬规则：只裁右侧栏面板，绝不整屏**（柠檬叔桌面左下角有真名）。

用法（坐标从 CDP 拿：`document.querySelector('[data-rightbar-col]').getBoundingClientRect()`）：

    python crop-panel.py <src> <out> <x> <y> <w> <h> <viewportWidth> [目标宽度]

坐标是 CSS 像素，要乘 `image.width / viewportWidth` 才是图片像素。**dpr 会变**
（见过 1 也见过 1.5），所以视口宽度必须现问浏览器要，别写死。
"""
import sys
from PIL import Image


def main() -> int:
    if len(sys.argv) < 8:
        print(__doc__)
        return 2
    src, out = sys.argv[1], sys.argv[2]
    x, y, w, h = (int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
    viewport_w = int(sys.argv[7])
    target_w = int(sys.argv[8]) if len(sys.argv) > 8 else 820

    image = Image.open(src)
    scale = image.width / viewport_w if viewport_w else 1
    box = (int(x * scale), int(y * scale), int((x + w) * scale), int((y + h) * scale))
    box = (max(0, box[0]), max(0, box[1]), min(image.width, box[2]), min(image.height, box[3]))
    crop = image.crop(box)
    if target_w and crop.width > target_w:
        ratio = target_w / crop.width
        crop = crop.resize((target_w, round(crop.height * ratio)), Image.LANCZOS)
    crop.save(out, optimize=True)
    print(f"{out}  {crop.size[0]}x{crop.size[1]}  box={box}  scale={scale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

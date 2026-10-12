"""Local OCR aid. Crops out browser chrome and answer-history sidebar."""
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import subprocess

root = Path(__file__).resolve().parents[1]
out = root / 'extraction'
out.mkdir(exist_ok=True)

def extract(path):
    im = Image.open(path)
    texts = []
    standalone = '111600' <= path.stem[-6:] <= '111650'
    boxes = [('standalone', (635, 150, 1148, 1018))] if standalone else [('passage', (25, 150, 885, 985)), ('question', (905, 155, 1776, 970))]
    for label, box in boxes:
        crop = out / (path.stem + '-' + label + '.png')
        im.crop(box).resize(((box[2]-box[0])*2, (box[3]-box[1])*2)).save(crop)
        result = subprocess.run(['tesseract', str(crop), 'stdout', '--psm', '6'], capture_output=True, text=True, encoding='utf-8')
        texts.append(label.upper() + '\n' + result.stdout)
    (out / (path.stem + '.txt')).write_text('\n\n'.join(texts), encoding='utf-8')
    return path.name

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name in pool.map(extract, sorted((root / 'source-images').glob('*.png'))):
            print(name)

import hashlib
import os
import cv2

from Siam.predict import siamese_cmp
from VideoProc.hashalgo import aHash, cmpHash, dHash, pHash
from VideoProc.ssim import ssim
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image


# 通过得到RGB每个通道的直方图来计算相似度
def classify_hist_with_split(image1, image2, size=(256, 256)):
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


# 计算单通道的直方图的相似值
def calculate(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])

    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


def algo(img1_path, img2_path):
    siamese_res = 0
    cnt = 0
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    img1 = cv2.resize(img1, (720, 1280), interpolation=cv2.INTER_CUBIC)
    img2 = cv2.resize(img2, (720, 1280), interpolation=cv2.INTER_CUBIC)
    # 均值哈希
    a_hash = cmpHash(aHash(img1), aHash(img2))

    # 差值哈希
    d_hash = cmpHash(dHash(img1), dHash(img2))

    # 感知哈希
    p_hash = cmpHash(pHash(img1), pHash(img2))

    # 三直方图算法
    s = classify_hist_with_split(img1, img2)
    if type(s) != float:
        tri = s[0]
    else:
        tri = s
    ssim_num = ssim(img1, img2)
    results = [a_hash, d_hash, p_hash, tri, ssim_num]
    for i in results:
        if i > 0.55:
            cnt += 1

    if cnt >= 4:
        # 孪生神经网络
        siamese_res = siamese_cmp(img1_path, img2_path)

    return [a_hash, d_hash, p_hash, tri, ssim_num, siamese_res]


def get_image_list(path):
    image_ext = [".jpg", ".png"]
    image_names = []
    for maindir, subdir, file_name_list in os.walk(path):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename).replace("\\", "/")
            ext = os.path.splitext(apath)[1]
            if ext in image_ext:
                image_names.append(apath)
    return image_names


def cmp(target, source, pattern):
    img_pairs = []
    scores = []
    result_dir = 'static/cmpresults/' + hashlib.sha256((target + source).encode()).hexdigest()[:32] + '.pdf'
    ori_list = get_image_list(target)
    mon_list = get_image_list(source)
    print(ori_list)
    print(mon_list)
    alert = 0
    max_prop = 0
    for i in ori_list:
        for j in mon_list:
            res = algo(i, j)
            # 每个普通算法权重占0.1，神经网络比较结果权重占0.5
            score = 0.1 * (res[0] + res[1] + res[2] + res[3] + res[4]) + 0.5 * res[5]
            if pattern == 'opti' and score > 0.6:
                img_pairs.append((i, j))
                scores.append(res)
            alert += score
            max_prop += 1
            print(max_prop)
    if pattern == 'opti' and len(img_pairs):
        save_result(img_pairs, scores, result_dir)
    print('cmp done')
    return alert / max_prop


def img_resize(img):
    if img.size[0] > img.size[1]:
        return img.resize((210, 150))
    else:
        return img.resize((150, 210))


def save_result(img_pairs, scores, result_dir):
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
    # 设置页面大小
    c = canvas.Canvas(result_dir, pagesize=letter)
    # 设置字体样式
    c.setFont("SimSun", 12)
    y = 600
    # 逐个添加图片和相似度计算结果
    for i, (image_pair, similarity_score) in enumerate(zip(img_pairs, scores)):
        score = 0.1*(similarity_score[0] + similarity_score[1] + similarity_score[2] + similarity_score[3] + similarity_score[4]) + 0.5*similarity_score[5]
        image1 = Image.open(image_pair[0])
        image2 = Image.open(image_pair[1])
        # 调整图片大小适应页面
        image1 = img_resize(image1)
        image2 = img_resize(image2)
        # 添加第一张图片
        c.drawString(20, y, f"图片 {i + 1} (1)")
        c.drawInlineImage(image1, 20, y - 50)
        # 添加第二张图片
        c.drawString(240, y, f"图片 {i + 1} (2)")
        c.drawInlineImage(image2, 240, y - 50)
        # 添加相似度计算结果
        c.drawString(480, y + 50, f"相似度分数:")
        c.drawString(480, y + 35, f"1.均值哈希:{str(similarity_score[0])}")
        c.drawString(480, y + 20, f"2.差值哈希:{str(similarity_score[1])}")
        c.drawString(480, y + 5, f"3.感知哈希:{str(similarity_score[2])}")
        c.drawString(480, y - 10, f"4.三直方图:{str(similarity_score[3])[:4]}")
        c.drawString(480, y - 25, f"5.SSIM:{str(similarity_score[4])[:4]}")
        c.drawString(480, y - 40, f"6.孪生神经网络:{str(similarity_score[5][0])[7:11]}")
        c.drawString(480, y - 55, f"综合相似度:{str(score[0])[7:11]}")
        y -= 320
        if i % 2 == 1:
            c.showPage()
            c.setFont("SimSun", 12)
            y = 600

    # 保存PDF报告
    c.save()


def opti_compare(your_dir, target_dir):
    return cmp(your_dir, target_dir, 'opti')


def compare(dir):
    """多种算法比较，经测试均值哈希算法与三直方图算法相似度效果较好"""
    target_dir = dir
    source_dir = 'static/images'
    results = []
    for child in os.listdir(source_dir):
        child_path = os.path.join(source_dir, child)
        if os.path.isdir(child_path) and (target_dir[-32:] != child_path[-32:]):
            results.append(cmp(target_dir, child_path, pattern='upload'))
    return results

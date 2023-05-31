import time
import cv2


def reproc(file, dir, gran):
    """视频预处理，提取关键帧"""
    video_name = file
    save_dir = dir
    num = 0
    print('video name: {}'.format(video_name))
    cap = cv2.VideoCapture(video_name)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print('FPS: {:.2f}'.format(fps))
    rate = cap.get(5)
    frame_num = cap.get(7)
    duration = frame_num / rate
    print('video total time: {:.2f}s'.format(duration))
    interval = int(fps) * gran
    process_num = frame_num // interval
    print('process frame: {:.0f}'.format(process_num))
    cnt = 0
    current_num = 0
    t0 = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cnt += 1
            if cnt % interval == 0:
                num += 1
                current_num += 1
                cv2.imwrite(save_dir + "/{}.jpg".format(str(num)), frame)
                remain_frame = process_num - current_num
                t1 = time.time() - t0
                t0 = time.time()
                print("Processing %07d.jpg, remain frame: %d, remain time: %.2fs" %
                        (num, remain_frame, remain_frame * t1))
        else:
            break
    cap.release()
    print("done")
    return 1
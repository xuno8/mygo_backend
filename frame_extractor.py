# extract_frame.py
import cv2
import random
import os

def extract_frame(video_path, frame_number, save_to_file=False):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()
    if success:
        if save_to_file:
            # 保存圖片到當前目錄下的指定檔名
            filename = f"frame_{frame_number}.jpeg"
            cv2.imwrite(filename, frame)
            print(f"Saved frame as {filename}")
        # 繼續將圖片以二進位形式返回
        _, buffer = cv2.imencode('.jpeg', frame)
        return buffer.tobytes()
    cap.release()
    return None

def extract_random_frame(video_directory):
    videos = [file for file in os.listdir(video_directory) if file.endswith('.mp4')]
    if not videos:
        return None, None, None

    video_filename = random.choice(videos)
    video_path = os.path.join(video_directory, video_filename)
    episode = extract_episode_number(video_filename)

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = random.randint(0, total_frames - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()
    if success:
        frame_time = frame_number / fps
        minutes = int(frame_time // 60)
        seconds = int(frame_time % 60)

        # 格式化為兩位數的時間格式
        time_formatted = "{:02}:{:02}".format(minutes, seconds)

        _, buffer = cv2.imencode('.jpeg', frame)
        cap.release()
        return buffer.tobytes(), episode, time_formatted
    cap.release()
    return None, None, None

import re

def extract_episode_number(filename):
    # 使用正則表達式從文件名中提取數字
    match = re.search(r'\d+', filename)
    if match:
        return match.group()  # 返回匹配的數字字符串
    return None

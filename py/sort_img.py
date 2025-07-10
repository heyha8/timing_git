import os
import shutil
from datetime import datetime
""" 
image sort scripts

origin folder structure:
 - file
    - <timestamp>
        - <timestamp>_1.jpg
        - <timestamp>_2.jpg
        - <timestamp>_3.jpg
        - <timestamp>_4.jpg
    - ...
---------------------------
target folder structure:
 - file
    - camera_1
        - <timestamp>.jpg
        - <timestamp>.jpg
        - ...
    - camera_2
        - ...
    - camera_3
        - ...
    - camera_4
        - ...
"""


src_folder = '/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/cam/1'
dest_folder = '/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/cam/image'
camera_num = 4

if __name__ == '__main__':

    for i in range(camera_num):
        if not os.path.exists(os.path.join(dest_folder, 'camera_'+str(i+1))):
            os.mkdir(os.path.join(dest_folder, 'camera_'+str(i+1)))

    # bar = tqdm.tqdm(total=0)
    dir_cnt = 0
    img_cnt = 0
    for dir in os.listdir(src_folder):
        dir_cnt += 1
        img_folder = os.path.join(src_folder,dir)

        
        for img in os.listdir(img_folder):
            name, suffix = os.path.splitext(img)
            img_cnt += 1

            img_id = name.rsplit('_',1)[1]
            img_timestamp = name.rsplit('_',1)[0]
            # print(name, img_id, img_timestamp)
            dt = datetime.strptime(img_timestamp, "%Y-%m-%d_%H_%M_%S_%f")
            # timestamp = str(dt.timestamp())

            # new_img_name = timestamp.split('.')[0]+timestamp.split('.')[1]+'.jpg'

            timestamp = int(dt.timestamp()) * 1_000_000 + dt.microsecond * 1

            new_img_name = str(timestamp) + '.jpg'

            src_img_path = os.path.join(img_folder, img)
            dst_img_path = os.path.join(dest_folder, 'camera_'+str(img_id), new_img_name)


            print('Processing folders:[' + str(dir_cnt) + '/' + str(len(os.listdir(src_folder))) +']', end='\r')

            shutil.copy(src_img_path, dst_img_path)

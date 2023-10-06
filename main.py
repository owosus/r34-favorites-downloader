import selenium
from selenium import webdriver # needs pip install selenium
from selenium.webdriver.common.by import By 
from webdriver_manager.firefox import GeckoDriverManager # needs pip install webdriver_manager
from os import system, path
from time import sleep, time_ns
import wget # needs pip install wget
import pathlib

print('r34 favorites downloader!')
print('[!] DO NOT PRESS/CLICK ANYTHING IN THE BROWSER WINDOW THAT WILL OPEN! IT OPERATES ITSELF :)')

print('\nYou can find your Profile ID in the URL of the "My Profile" page.')
user_id = input('Profile ID: ')


print('\nA page consists of 50 posts. Page 1 are your latest 50 favs, page 2 are your 50 latest after that and so on...')
page = int(input('Page: '))



driver = webdriver.Firefox()
pid = page*50 - 50
driver.get(f"https://rule34.xxx/index.php?page=favorites&s=view&id={user_id}&pid={pid}")

sleep(1)

source_code = driver.page_source          # save the source code of the favorites page
#with open('page_favs.html', 'w', encoding="utf-8") as f:
#    #system('cls')
#    #print(source_code)
#    f.write(source_code)



# href="index.php?page=post&amp;s=view&amp;id=
found_ids = []
for i in range(len(source_code)):                       # this loop goes through every character of the source code,
    char = source_code[i]                               # looks for links going to a post and extracts the post ids from the links
    text_to_check = source_code[ i : i+44 ]

    if text_to_check == 'href="index.php?page=post&amp;s=view&amp;id=':
        found_id_begin_index = i+44
        offset = 0
        while True:
            offset += 1
            if source_code[ i+44+offset ] == '"': break
            else: continue
        found_id_end_index = i+44+offset
        found_id = source_code[ found_id_begin_index : found_id_end_index ]
        found_ids.append(found_id)



print(f'\nFound images: {", ".join(found_ids)}\n')

download_folder = f'./r34download_{time_ns()}'
pathlib.Path(download_folder).mkdir(parents=True, exist_ok=True)   # create download folder

num_errors = 0

for post_id in found_ids:

    driver.get(f"https://rule34.xxx/index.php?page=post&s=view&id={post_id}")   # load page

    sleep(1)

    try:
        max_res_script = "Post.highres(); $('resized_notice').hide(); Note.sample=false; return false;"
        driver.execute_script(max_res_script)                                                               # load maximum resolution
        #post_type = 'image'
    except selenium.common.exceptions.JavascriptException:
        #post_type = 'video'
        pass

    sleep(1)

    post_source = driver.page_source
    #with open(f'page_{post_id}.html', 'w', encoding="utf-8") as f: 
    #    f.write(post_source)

    try:
        # try downloading image in any case
        img_element = driver.find_element(By.ID, "image")       # find image link
        image_link = img_element.get_attribute('src')           #
        
        wget.download(image_link, download_folder)              # download
        print(f'\nDownloaded {image_link}\n')

    except selenium.common.exceptions.NoSuchElementException:
        try:
            # image failed, so probably video. download video
            vidsrc_elem = driver.find_element(By.XPATH, '/html/body/div[5]/div/div[2]/div[1]/div[2]/div[1]/div[3]/div/video/source') # locate video source element (if this doesn't work in the future, just put in the new xpath)
            video_link = vidsrc_elem.get_attribute('src')

            wget.download(video_link, download_folder)              # download
            print(f'\nDownloaded {video_link}\n')
        except selenium.common.exceptions.NoSuchElementException:
            # neither image nor video found -> probably deleted :(
            print(f'{post_id} could not be downloaded!\n')   
            num_errors += 1 

driver.quit()
print(f'Finished with {num_errors} errors (Check output for more info).')
input() # pause

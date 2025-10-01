import pymongo_management
import toolfacebook_lib
import xml.etree.ElementTree as ET
from util import log_message, DEVICE_LIST_NAME
import asyncio
import logging

async def join_group(driver, command_id, user_id, group_link, back_to_facebook = True):
    toolfacebook_lib.redirect_to(driver, "https://facebook.com/" + group_link)
    await asyncio.sleep(5)
    joined_group = driver(textContains="đã tham gia nhóm")
    if joined_group.exists:
        result = await pymongo_management.update_joined_accounts(user_id, group_link)
        log_message(f"{DEVICE_LIST_NAME[driver.serial]} - {result[0]['message']}", result[1])
        await pymongo_management.execute_command(command_id, "Đã thực hiện")
        if back_to_facebook:
            await toolfacebook_lib.back_to_facebook(driver)
        return

    join_button_clicked = False
    join_button = driver(textContains="Tham gia nhóm")
    if join_button.exists:
        join_button.click()
        join_button_clicked = True

        joined_group = driver(textContains="đã tham gia nhóm")
        await asyncio.sleep(5)
        if joined_group.exists:
            result = await pymongo_management.update_joined_accounts(user_id, group_link)
            log_message(f"{DEVICE_LIST_NAME[driver.serial]} - {result[0]['message']}", result[1])
            await pymongo_management.execute_command(command_id, "Đã thực hiện")
            if back_to_facebook:
                await toolfacebook_lib.back_to_facebook(driver)
            return

    if not await toolfacebook_lib.click_template(driver, "answer_question") and not join_button_clicked:
        log_message(f"{DEVICE_LIST_NAME[driver.serial]} - Nhóm đang chờ duyệt: {group_link}", logging.INFO)
        await pymongo_management.execute_command(command_id, "Đã thực hiện")
        if back_to_facebook:
            await toolfacebook_lib.back_to_facebook(driver)
        return
    await asyncio.sleep(2)
    xml_dump = driver.dump_hierarchy()
    root = ET.fromstring(xml_dump)

    visible_texts = []
    nodes = []

    for node in root.iter():
        visible = node.attrib.get("visible-to-user", "false") == "true"
        text = node.attrib.get("text", "").strip()

        if visible and text:
            visible_texts.append(text)
            nodes.append(node)

    all_questions_answered = True
    if "Trả lời câu hỏi" in visible_texts:
        indexes = [i for i, text in enumerate(visible_texts) if (text == "Viết câu trả lời..." or text == "Bạn có thể chọn nhiều đáp án" or text == "Bạn có thể chọn 1 đáp án" or text == "Gửi") and visible_texts[i-1] != "Viết câu trả lời..."]
        indexes[-1] += 1
        for i in range(len(indexes) - 1):
            answers = []
            for j in range(indexes[i] + 1, indexes[i + 1] - 1):
                answers.append(visible_texts[j])
            await pymongo_management.upload_question(group_link, visible_texts[indexes[i] - 1], visible_texts[indexes[i]], answers)
            answer, log = await pymongo_management.get_answer(group_link, visible_texts[indexes[i] - 1])
            log_message(f"{DEVICE_LIST_NAME[driver.serial]} - {answer['message']}", log)
            if "answer" in answer:
                if visible_texts[indexes[i]] == "Viết câu trả lời...":
                    bounds = nodes[indexes[i]].attrib.get("bounds")
                    bounds = toolfacebook_lib.parse_number(bounds)
                    driver.click((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
                    driver.send_keys(answer['answer'], clear=True)
                    driver.press("back")  # Nhấn nút back để đóng bàn phím
                elif visible_texts[indexes[i]] == "Bạn có thể chọn nhiều đáp án":
                    for i in range(indexes[i] + 1, indexes[i + 1] - 1):
                        if visible_texts[i] in answer['answer']:
                            bounds = nodes[i].attrib.get("bounds")
                            bounds = toolfacebook_lib.parse_number(bounds)
                            driver.click((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
                elif visible_texts[indexes[i]] == "Bạn có thể chọn 1 đáp án":
                    for i in range(indexes[i] + 1, indexes[i + 1] - 1):
                        if visible_texts[i] == answer['answer']:
                            bounds = nodes[i].attrib.get("bounds")
                            bounds = toolfacebook_lib.parse_number(bounds)
                            driver.click((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
                            break
            else:
                all_questions_answered = False
    if all_questions_answered:
        driver(description="Gửi").click()
        result = await pymongo_management.update_temp_joined_accounts(user_id, group_link)
        log_message(f"{DEVICE_LIST_NAME[driver.serial]} - {result[0]['message']}", result[1])
    else:
        driver(resourceId="com.android.systemui:id/back").click()
        driver(resourceId="com.facebook.katana:id/(name removed)", text="THOÁT").click()
    await pymongo_management.execute_command(command_id, "Đã thực hiện")
    if back_to_facebook:
        await toolfacebook_lib.back_to_facebook(driver)
    
async def check_unapproved_groups(driver, user_id):
    unapproved_groups = await pymongo_management.get_unapproved_groups(user_id)
    for group in unapproved_groups:
        await join_group(driver, "", user_id, group['Link'], False)
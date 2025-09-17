import os
import re
import json
import random
import logging
import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from util.my_utils import my_find_element, my_find_elements
from util import log_message

# Optional imports from surf_fb for interactions
try:
    from module.surf_fb import like_post, comment_post, EMOTION, COMMENTS
    HAS_SURF_FB = True
except Exception:
    HAS_SURF_FB = False


# ---------------------- Persistence helpers ----------------------

async def get_facebook_account_name(driver) -> str:
    """
    Phiên bản cải tiến - ưu tiên tên người thật hơn text placeholder
    """
    print("🎯 Lấy tên Facebook từ profile - Phiên bản cải tiến...")
    
    try:
        # Bước 1: Đảm bảo ở trang chủ
        driver.press("home")
        driver.app_start("com.facebook.katana")
        await asyncio.sleep(3)
        
        # Bước 2: Click vào "Đi tới trang cá nhân"
        profile_locators = [
            ("desc", "Đi tới trang cá nhân"),
            ("desc", "Go to profile"),
            ("desc", "Your profile"),
            ("desc", "Trang cá nhân của bạn"),
            ("text", "Đi tới trang cá nhân"),
            ("text", "Go to profile"),
        ]
        
        profile_element = await my_find_element(driver, profile_locators)
        
        if not profile_element:
            print("❌ Không tìm thấy nút 'Đi tới trang cá nhân'")
            return "unknown_user"
        
        profile_element.click()
        print("✅ Đã click vào trang cá nhân")
        await asyncio.sleep(4)
        
        # Bước 3: Phân tích trang profile
        print("🔍 Phân tích trang profile...")
        xml_dump = driver.dump_hierarchy()
        
        # Debug: Lưu XML để xem
        with open("profile_debug.xml", "w", encoding="utf-8") as f:
            f.write(xml_dump)
        print("💾 Đã lưu XML debug vào profile_debug.xml")
        
        root = ET.fromstring(xml_dump)
        
        # Tìm tên với logic cải tiến
        name_candidates = []
        
        for node in root.iter():
            text = node.attrib.get("text", "").strip()
            class_name = node.attrib.get("class", "")
            bounds = node.attrib.get("bounds", "")
            resource_id = node.attrib.get("resource-id", "")
            
            if text and len(text) > 1:
                # Parse vị trí Y
                try:
                    import re
                    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
                    y_pos = int(m.groups()[1]) if m else 9999
                    x_pos = int(m.groups()[0]) if m else 9999
                except:
                    y_pos = 9999
                    x_pos = 9999
                
                words = text.split()
                word_count = len(words)
                
                # BLACKLIST: Loại bỏ hoàn toàn các text placeholder/UI
                blacklist_phrases = [
                    'đang nghĩ về', 'thinking about', 'what\'s on your mind',
                    'bài viết', 'posts', 'ảnh', 'photos', 'bạn bè', 'friends',
                    'theo dõi', 'follow', 'tin nhắn', 'message', 'giới thiệu', 'about',
                    'xem thêm', 'see more', 'chỉnh sửa', 'edit', 'cài đặt', 'settings',
                    'hoạt động', 'activity', 'video', 'story', 'reels', 'live',
                    'người bạn', 'mutual friends', 'bạn chung', 'common friends',
                    'thêm story', 'add story', 'tạo', 'create', 'chia sẻ', 'share'
                ]
                
                # Kiểm tra blacklist
                text_lower = text.lower()
                is_blacklisted = any(phrase in text_lower for phrase in blacklist_phrases)
                
                # Điều kiện cơ bản để là tên người
                if (not is_blacklisted and
                    word_count >= 1 and 
                    2 <= len(text) <= 50 and
                    any(c.isalpha() for c in text) and
                    not text.isdigit()):
                    
                    # Tính điểm ưu tiên THÔNG MINH
                    score = 0
                    
                    # ĐIỂM CAO CHO FORMAT TÊN NGƯỜI
                    if word_count >= 2:  # Họ và tên
                        # Kiểm tra format tên người (viết hoa đầu chữ)
                        is_proper_name = all(w[0].isupper() if w and w[0].isalpha() else True for w in words)
                        if is_proper_name:
                            score += 100  # Điểm rất cao cho tên người thật
                        else:
                            score += 50
                    elif word_count == 1 and len(text) >= 3:
                        if text[0].isupper():
                            score += 80  # Tên một từ viết hoa
                        else:
                            score += 30
                    
                    # ĐIỂM CHO VỊ TRÍ (ưu tiên header nhưng không quá cao)
                    if y_pos < 400: score += 20  # Khu vực header
                    elif y_pos < 800: score += 10
                    
                    # ĐIỂM CHO CLASS
                    if "TextView" in class_name: score += 10
                    
                    # ĐIỂM CHO ĐỘ DÀI HỢP LÝ
                    if 3 <= len(text) <= 30: score += 15
                    
                    # ĐIỂM CHO VỊ TRÍ X (không quá lệch)
                    if 10 <= x_pos <= 1000: score += 5
                    
                    # BONUS CHO RESOURCE-ID LIÊN QUAN
                    if any(keyword in resource_id.lower() for keyword in ['name', 'title', 'header', 'user']):
                        score += 25
                    
                    # PENALTY CHO CÁC PATTERN KHÔNG PHẢI TÊN
                    if any(pattern in text_lower for pattern in ['...', 'click', 'tap', 'button', 'tab']):
                        score -= 30
                    
                    # BONUS ĐẶC BIỆT CHO TÊN VIỆT NAM PATTERN
                    vietnamese_name_patterns = ['bùi', 'nguyễn', 'trần', 'lê', 'phạm', 'hoàng', 'phan', 'vũ', 'đặng', 'võ']
                    if any(pattern in text_lower for pattern in vietnamese_name_patterns):
                        score += 50  # Bonus cao cho họ Việt Nam
                    
                    name_candidates.append({
                        'text': text,
                        'score': score,
                        'y_pos': y_pos,
                        'x_pos': x_pos,
                        'class': class_name,
                        'resource_id': resource_id,
                        'word_count': word_count
                    })
        
        # Sắp xếp theo điểm
        if name_candidates:
            name_candidates.sort(key=lambda x: -x['score'])
            
            # Lọc thêm các candidate có điểm cao
            high_score_candidates = [c for c in name_candidates if c['score'] >= 70]
            
            if high_score_candidates:
                best_candidate = high_score_candidates[0]
                best_name = best_candidate['text']
                
                # Clean name
                clean_name = best_name.strip()
                clean_name = ''.join(c if c.isalnum() or c == ' ' else '' for c in clean_name)
                clean_name = clean_name.replace(' ', '_')
                while '__' in clean_name:
                    clean_name = clean_name.replace('__', '_')
                clean_name = clean_name.strip('_')
                
                # Quay lại trang chủ
                driver.press("back")
                await asyncio.sleep(2)
                
                if clean_name and len(clean_name) >= 2:
                    print(f"\n✅ THÀNH CÔNG: {clean_name}")
                    return clean_name
                else:
                    print(f"\n❌ Tên không hợp lệ sau khi clean: '{clean_name}'")
            else:
                print("\n❌ Không có candidate nào đạt điểm cao (>=70)")
        else:
            print("\n❌ Không tìm thấy candidate nào trong profile")
        
        # Quay lại nếu thất bại
        driver.press("back")
        await asyncio.sleep(2)
        return "unknown_user"
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        try:
            driver.press("back")
            await asyncio.sleep(2)
        except:
            pass
        return "unknown_user"

async def get_facebook_username(driver, device_id: str) -> str:
    """Trả về tên user thực tế từ device_id + account_name."""
    account_name = await get_facebook_account_name(driver)
    return f"{device_id}_{account_name}"


def load_friends_data(username: str) -> Dict[str, bool]:
    # Tạo folder base_banbe nếu chưa có
    base_folder = "base_banbe"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    filename = os.path.join(base_folder, f"{username}_banbe.json")
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_friends_data(username: str, friends_data: Dict[str, bool]) -> bool:
    # Tạo folder base_banbe nếu chưa có
    base_folder = "base_banbe"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    filename = os.path.join(base_folder, f"{username}_banbe.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(friends_data, f, ensure_ascii=False, indent=2)
        log_message(f"✅ Đã lưu dữ liệu {len(friends_data)} bạn bè vào {filename}")
        return True
    except Exception as e:
        log_message(f"❌ Lỗi khi lưu file: {e}", logging.ERROR)
        return False


# ---------------------- Screen parsing ----------------------
def extract_friends_from_screen(driver) -> List[str]:
    friends_found: List[str] = []
    try:
        xml_dump = driver.dump_hierarchy()
        root = ET.fromstring(xml_dump)

        # Collect potential names
        potential_names = []
        for node in root.iter():
            class_name = node.attrib.get("class", "")
            text = node.attrib.get("text", "").strip()
            resource_id = node.attrib.get("resource-id", "")
            if text and len(text) > 1:
                excluded_keywords = [
                    "bạn bè", "friends", "tab", "tìm kiếm", "search", "menu",
                    "thêm", "gợi ý", "xem", "tìm", "online", "active", "home",
                    "bạn chung", "thêm bạn", "chấp nhận", "từ chối", "tin nhắn",
                    "theo dõi", "đã theo dõi", "bỏ theo dõi", "kết bạn", "đã kết bạn",
                    "phút", "giờ", "ngày", "tuần", "tháng", "năm", "trước", "giây",
                    "hoạt động", "trực tuyến", "offline", "đang hoạt động",
                ]
                text_lower = text.lower()
                if not any(keyword in text_lower for keyword in excluded_keywords):
                    if (
                        2 <= len(text) <= 50
                        and any(c.isalpha() for c in text)
                        and not text.isdigit()
                        and not all(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in text)
                    ):
                        potential_names.append(
                            {
                                "text": text,
                                "class": class_name,
                                "resource_id": resource_id,
                                "bounds": node.attrib.get("bounds", ""),
                            }
                        )

        # Heuristic filtering
        for item in potential_names:
            text = item["text"]
            words = text.split()
            if len(words) >= 2:
                is_name_format = all(w[0].isupper() if w and w[0].isalpha() else True for w in words)
                if is_name_format:
                    friends_found.append(text)
                    continue
            if len(words) == 1 and len(text) >= 3 and text[0].isupper():
                friends_found.append(text)

        if not friends_found:
            # Fallback: detect friend card
            for node in root.iter():
                class_name = node.attrib.get("class", "")
                bounds = node.attrib.get("bounds", "")
                if bounds and "ViewGroup" in class_name:
                    try:
                        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
                        if m:
                            left, top, right, bottom = map(int, m.groups())
                            width = right - left
                            height = bottom - top
                            if 200 <= width <= 500 and 40 <= height <= 150:
                                for child in node.iter():
                                    child_text = child.attrib.get("text", "").strip()
                                    child_class = child.attrib.get("class", "")
                                    if (
                                        "TextView" in child_class
                                        and child_text
                                        and 3 <= len(child_text) <= 50
                                        and any(c.isalpha() for c in child_text)
                                    ):
                                        excluded_in_card = [
                                            "bạn chung",
                                            "thêm bạn",
                                            "tin nhắn",
                                            "theo dõi",
                                            "phút",
                                            "giờ",
                                            "hoạt động",
                                        ]
                                        if not any(
                                            kw in child_text.lower() for kw in excluded_in_card
                                        ):
                                            friends_found.append(child_text)
                                            break
                    except Exception:
                        continue

        unique = sorted(set(friends_found))
        return unique
    except Exception as e:
        log_message(f"❌ Lỗi khi trích xuất tên bạn bè: {e}", logging.ERROR)
        return []


# ---------------------- Interactions on profile ----------------------
async def surf_friend_profile_with_interactions_v2(driver, scroll_count: Optional[int] = None):
    if scroll_count is None:
        scroll_count = random.randint(10, 20)
    log_message(f"📜 Lướt tường với {scroll_count} lần và tương tác")
    try:
        for i in range(scroll_count):
            driver.swipe_ext("up", scale=random.uniform(0.5, 0.7))
            await asyncio.sleep(random.uniform(1.5, 3))

            if HAS_SURF_FB:
                # React chỉ mỗi lần lướt chia hết cho 11, bỏ qua nếu lỗi
                if (i + 1) % 11 == 0:
                    try:
                        emotion = random.choice(EMOTION)
                        await like_post(driver, emotion)
                        await asyncio.sleep(random.uniform(2, 3))
                    except Exception:
                        # Bỏ qua nếu không react được, không log lỗi
                        pass
    except Exception as e:
        log_message(f"❌ Lỗi khi lướt tường: {e}", logging.ERROR)


async def _search_and_click_friend(driver, friend_name: str):
    friend_locators = [
        ("text", friend_name),
        ("xpath", f"//*[@text='{friend_name}']"),
        ("xpath", f"//*[contains(@text, '{friend_name}')]"),
    ]

    friend_el = await my_find_element(driver, friend_locators)
    if friend_el:
        friend_el.click()
        return True

    log_message(f"🔍 Không thấy {friend_name} trên màn hình, bắt đầu lướt tìm kiếm...")
    found = False
    # Scroll down up to 7 times
    for _ in range(7):
        friend_el = await my_find_element(driver, friend_locators)
        if friend_el:
            friend_el.click()
            found = True
            break
        driver.swipe_ext("up", scale=random.uniform(0.6, 0.8))
        await asyncio.sleep(random.uniform(1, 1.5))
    # Scroll up up to 8 times
    if not found:
        for _ in range(8):
            friend_el = await my_find_element(driver, friend_locators)
            if friend_el:
                friend_el.click()
                found = True
                break
            driver.swipe_ext("down", scale=random.uniform(0.6, 0.8))
            await asyncio.sleep(random.uniform(1, 1.5))
    return found


async def visit_friend_profile_v2(driver, friend_name: str, device_id: str, username: Optional[str] = None, friends_data: Optional[Dict[str, bool]] = None) -> bool:
    try:
        log_message(f"👀 Đang thăm tường: {friend_name}")
        if not await _search_and_click_friend(driver, friend_name):
            log_message(f"❌ Không tìm thấy {friend_name}", logging.WARNING)
            return False

        await asyncio.sleep(random.uniform(3, 5))

        # Mark visited immediately
        if username and friends_data is not None:
            friends_data[friend_name] = True
            save_friends_data(username, friends_data)

        # Scroll and interact 10-20 times
        scroll_times = random.randint(10, 20)
        try:
            await surf_friend_profile_with_interactions_v2(driver, scroll_times)
        except Exception as e:
            log_message(f"⚠️ Lỗi khi chạy tương tác: {e}")
            for _ in range(scroll_times):
                driver.swipe_ext("up", scale=random.uniform(0.5, 0.7))
                await asyncio.sleep(random.uniform(1, 2))

        # Go back to list
        driver.press("back")
        await asyncio.sleep(random.uniform(2, 3))
        log_message(f"✅ Đã thăm xong: {friend_name}")
        return True
    except Exception as e:
        log_message(f"❌ Lỗi khi thăm tường {friend_name}: {e}", logging.ERROR)
        return False


async def load_facebook_friends_list_advanced(driver, device_id: str, visit_friends: bool = True) -> bool:
    """Thu thập danh sách bạn bè và thăm ngẫu nhiên, đánh dấu ngay."""
    username = await get_facebook_username(driver, device_id)
    friends_data = load_friends_data(username)

    try:
        # 1) Mở tab bạn bè
        friends_tab_locators = [
            ("desc", "Bạn bè, Tab 2/6"),
            ("desc", "Friends, Tab 2/6"),
            ("xpath", "//android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]"),
            ("text", "Bạn bè"),
            ("text", "Friends"),
            ("desc", "Bạn bè"),
            ("desc", "Friends"),
            ("resourceId", "com.facebook.katana:id/bookmarks_tab"),
            ("xpath", "//*[contains(@content-desc, 'Bạn bè') and contains(@content-desc, 'Tab')]"),
            ("xpath", "//*[contains(@content-desc, 'Friends') and contains(@content-desc, 'Tab')]")
        ]
        tab = await my_find_element(driver, friends_tab_locators)
        if not tab:
            log_message("❌ Không tìm thấy tab bạn bè", logging.ERROR)
            return False
        tab.click()
        await asyncio.sleep(3)

        # 2) Mở danh sách bạn bè
        friends_list_locators = [
            ("xpath", "//androidx.viewpager.widget.ViewPager/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.Button[2]"),
            ("text", "Bạn bè"),
            ("text", "All friends"),
            ("text", "Tất cả bạn bè"),
            ("text", "Danh sách bạn bè"),
            ("desc", "Bạn bè"),
            ("desc", "All friends"),
            ("desc", "Tất cả bạn bè"),
            ("xpath", "//android.widget.Button[contains(@text, 'bạn')]"),
            ("xpath", "//android.widget.Button[contains(@text, 'friend')]"),
            ("xpath", "//android.widget.Button[contains(@content-desc, 'bạn')]"),
            ("xpath", "//android.widget.Button[contains(@content-desc, 'friend')]")
        ]
        btn = await my_find_element(driver, friends_list_locators)
        if not btn:
            log_message("❌ Không tìm thấy nút danh sách bạn bè", logging.ERROR)
            return False
        btn.click()
        await asyncio.sleep(3)

        # 3) Thu thập danh sách bạn bè bằng cách lướt
        all_friends = set()
        no_new = 0
        for _ in range(50):
            names = extract_friends_from_screen(driver) 
            before = len(all_friends)
            all_friends.update(names)
            after = len(all_friends)
            if after == before:
                no_new += 1
            else:
                no_new = 0
            if no_new >= 3:
                break
            driver.swipe_ext("up", scale=random.uniform(0.6, 0.8))
            await asyncio.sleep(random.uniform(1.5, 2.5))

        # 4) Cập nhật và lưu file
        for name in all_friends:
            friends_data.setdefault(name, False)
        save_friends_data(username, friends_data)

        if not visit_friends or not friends_data:
            return True

        # 5) Chọn bạn bè để thăm
        unvisited = [n for n, v in friends_data.items() if not v]
        if not unvisited:
            for k in list(friends_data.keys()):
                friends_data[k] = False
            unvisited = list(friends_data.keys())

        # Ưu tiên bạn hiển thị màn hình hiện tại
        visible = []
        for _ in range(min(5, max(1, len(unvisited) // 2 + 1))):
            onscreen = extract_friends_from_screen(driver)
            for n in onscreen:
                if n in unvisited and n not in visible:
                    visible.append(n)
            if len(visible) >= 8:
                break
            driver.swipe_ext("up", scale=random.uniform(0.4, 0.6))
            await asyncio.sleep(1)

        to_visit: List[str] = []
        if visible:
            to_visit.extend(random.sample(visible, min(6, len(visible))))
        remaining = [n for n in unvisited if n not in to_visit]
        if remaining and len(to_visit) < 10:
            to_visit.extend(random.sample(remaining, min(4, len(remaining), 10 - len(to_visit))))
        if not to_visit:
            count = random.randint(min(3, len(unvisited)), min(8, len(unvisited)))
            to_visit = random.sample(unvisited, count)

        # 6) Thăm từng bạn và lưu ngay
        success = 0
        for idx, name in enumerate(to_visit, 1):
            log_message(f"🔄 Thăm bạn {idx}/{len(to_visit)}: {name}")
            try:
                result = await visit_friend_profile_v2(driver, name, device_id, username, friends_data)
                if result:
                    success += 1
                    save_friends_data(username, friends_data)
            except Exception as e:
                log_message(f"❌ Lỗi khi thăm {name}: {e}", logging.ERROR)
            await asyncio.sleep(random.uniform(3, 6))

        log_message(f"📈 Kết quả: Thăm thành công {success}/{len(to_visit)} bạn")
        return True
    except Exception as e:
        log_message(f"❌ Lỗi tổng quát: {e}", logging.ERROR)
        return False


__all__ = [
    "get_facebook_account_name",
    "get_facebook_username",
    "load_friends_data",
    "save_friends_data",
    "extract_friends_from_screen",
    "surf_friend_profile_with_interactions_v2",
    "visit_friend_profile_v2",
    "load_facebook_friends_list_advanced",
]

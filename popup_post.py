import threading
import tkinter as tk
from tkinter import messagebox, ttk

# === STYLE CẢI TIẾN ===
def style_button(btn: ttk.Button):
    """Tạo style đẹp cho button"""
    style = ttk.Style()
    style.configure(
        "Accent.TButton",
        foreground="white",
        background="#0078D7",
        font=("Segoe UI", 10, "bold"),
        padding=8,
        relief="flat"
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#005a9e")]
    )
    btn.configure(style="Accent.TButton")


def start_post_popup(on_post_callback, get_devices_callback):
    def refresh_devices():
        """Cập nhật danh sách thiết bị"""
        devices = get_devices_callback()
        menu = device_menu["menu"]
        menu.delete(0, "end")
        for did in devices:
            menu.add_command(label=did, command=lambda v=did: device_var.set(v))
        if devices:
            device_var.set(devices[0])
        else:
            device_var.set("Không có thiết bị")

    def toggle_all_devices():
        """Ẩn/hiện dropdown khi chọn 'Đăng trên tất cả thiết bị'"""
        if all_devices_var.get():
            device_menu.config(state="disabled")
        else:
            device_menu.config(state="normal")

    def toggle_image_input():
        """Ẩn/hiện textbox nhập ảnh"""
        if include_image_var.get():
            image_frame.pack(fill="x", padx=10, pady=5)
        else:
            image_frame.pack_forget()

    def submit():
        """Xử lý khi bấm nút 'Đăng bài ngay'"""
        content = post_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Thiếu nội dung", "Vui lòng nhập nội dung bài viết!")
            return

        target_device = None if all_devices_var.get() else device_var.get()
        images = []
        if include_image_var.get():
            img_text = image_entry.get().strip()
            if img_text:
                images = [x.strip() for x in img_text.split(",")]

        messagebox.showinfo("Đang xử lý", "Đang gửi yêu cầu đăng bài...")
        on_post_callback(content, target_device, images)
        post_text.delete("1.0", tk.END)
        image_entry.delete(0, tk.END)

    # --- Giao diện chính ---
    root = tk.Tk()
    root.title("📱 Auto Poster Control")
    root.geometry("460x530")
    root.resizable(False, False)
    root.configure(bg="#f4f6fa")

    # --- Tiêu đề ---
    title = tk.Label(
        root,
        text="Auto Facebook/Zalo Poster",
        font=("Segoe UI Semibold", 14),
        bg="#0078D7",
        fg="white",
        pady=10
    )
    title.pack(fill="x")

    # --- Khung nhập nội dung ---
    post_frame = tk.LabelFrame(root, text="📝 Nội dung bài viết", font=("Segoe UI", 10, "bold"), bg="#f4f6fa")
    post_frame.pack(fill="x", padx=10, pady=(15, 10))

    post_text = tk.Text(post_frame, wrap=tk.WORD, height=6, width=52, font=("Segoe UI", 10))
    post_text.pack(padx=10, pady=10)

    # --- Khung chọn thiết bị ---
    device_frame = tk.LabelFrame(root, text="📱 Thiết bị", font=("Segoe UI", 10, "bold"), bg="#f4f6fa")
    device_frame.pack(fill="x", padx=10, pady=10)

    all_devices_var = tk.BooleanVar(value=True)
    tk.Checkbutton(device_frame, text="Đăng trên tất cả thiết bị",
                   variable=all_devices_var, bg="#f4f6fa",
                   font=("Segoe UI", 10), command=toggle_all_devices).pack(anchor="w", padx=10, pady=3)

    tk.Label(device_frame, text="Hoặc chọn thiết bị cụ thể:", bg="#f4f6fa",
             font=("Segoe UI", 9, "italic")).pack(anchor="w", padx=10)
    device_var = tk.StringVar(value="Không có thiết bị")
    device_menu = ttk.OptionMenu(device_frame, device_var, "Không có thiết bị")
    device_menu.pack(padx=10, pady=(5, 5), fill="x")

    refresh_btn = ttk.Button(device_frame, text="🔄 Làm mới danh sách", command=refresh_devices)
    style_button(refresh_btn)
    refresh_btn.pack(padx=10, pady=5)

    # --- Khung ảnh ---
    image_frame = tk.LabelFrame(root, text="📷 Ảnh đính kèm", font=("Segoe UI", 10, "bold"), bg="#f4f6fa")
    include_image_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Kèm ảnh", variable=include_image_var,
                   command=toggle_image_input, bg="#f4f6fa",
                   font=("Segoe UI", 10)).pack(anchor="w", padx=15, pady=(5, 0))

    image_label = tk.Label(image_frame, text="Nhập tên ảnh (cách nhau bằng dấu phẩy):", bg="#f4f6fa")
    image_label.pack(anchor="w", padx=10, pady=(5, 0))
    image_entry = tk.Entry(image_frame, width=45)
    image_entry.pack(padx=10, pady=(0, 8))

    # --- Nút hành động ---
    btn_frame = tk.Frame(root, bg="#f4f6fa")
    btn_frame.pack(pady=20)

    post_btn = ttk.Button(btn_frame, text="🚀 Đăng bài ngay", command=submit)
    style_button(post_btn)
    post_btn.pack(ipadx=10, ipady=3)

    # --- Khởi tạo ---
    root.after(1000, refresh_devices)
    root.mainloop()


def launch_post_popup(on_post_callback, get_devices_callback):
    """Chạy popup trong thread riêng để không chặn asyncio"""
    thread = threading.Thread(
        target=start_post_popup,
        args=(on_post_callback, get_devices_callback),
        daemon=True
    )
    thread.start()

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import shutil
import os
import threading
from concurrent.futures import ThreadPoolExecutor

class UltimateCopyPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Tiện ích Copy Multi Folder/File")
        x=(root.winfo_screenwidth() - 600) // 2
        y=(root.winfo_screenheight() - 550) // 2
        self.root.geometry(f'600x550+{x}+{y}')
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
        
        # --- STYLE ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", background="#2bec11")
        self.style.configure("TLabelframe", background="#f0f0f0")
        self.style.configure("TLabelframe.Label", background="#f0f0f0")

        # --- HEADER ---
        header_frame = tk.Frame(root, bg="#2c3e50", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="HỆ THỐNG SAO CHÉP ĐA LUỒNG", font=("Segoe UI", 12, "bold"), 
                 bg="#2c3e50", fg="white").pack(pady=5)

        # --- MAIN CONTAINER ---
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- KHU VỰC NGUỒN ---
        src_label = tk.Label(main_frame, text="📁 Danh sách nguồn (Kéo thả hoặc chọn file/thư mục):", 
                 font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg="#2c3e50")
        src_label.pack(anchor="w", pady=(0, 5))
        
        # Scrollbar for text widget
        src_frame = tk.Frame(main_frame, bg="#f0f0f0")
        src_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        scrollbar = tk.Scrollbar(src_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.src_text = tk.Text(src_frame, height=8, relief="solid", font=("Consolas", 9),
                                highlightthickness=1, highlightbackground="#bdc3c7", padx=8, pady=8,
                                yscrollcommand=scrollbar.set, bg="white")
        self.src_text.pack(fill="both", expand=True, side=tk.LEFT)
        scrollbar.config(command=self.src_text.yview)
        
        self.src_text.drop_target_register(DND_FILES)
        self.src_text.dnd_bind('<<Drop>>', self.handle_src_drop)
        self.tooltip(self.src_text, "Kéo thả nhiều file hoặc thư mục từ máy tính vào đây.\nMỗi mục sẽ nằm trên một dòng.")
       
        # --- BUTTONS FOR SOURCE ---
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(fill="x", pady=(0, 5))
        
        self.btn_add = tk.Button(btn_frame, text="📂 Thêm thư mục", command=self.Select_folders,
                                 bg="#3498db", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), 
                                 cursor="hand2", padx=15, pady=5)
        self.btn_add.pack(side='left', padx=(40,20))
        self.tooltip(self.btn_add, "Nhấn để thêm thư mục thủ công.")

        self.btn_add_file = tk.Button(btn_frame, text="📄 Thêm file", command=self.Select_files,
                                 bg="#3498db", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), 
                                 cursor="hand2", padx=15, pady=5)
        self.btn_add_file.pack(side='left', padx=(20, 20))
        self.tooltip(self.btn_add_file, "Nhấn để thêm file thủ công.")
      
        btn_clear = tk.Button(btn_frame, text="🗑️ Dọn dẹp danh sách", command=self.src_text.delete('1.0', tk.END),
                              bg="#e74c3c", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), 
                              cursor="hand2", padx=15, pady=5)
        btn_clear.pack(side='left', padx=(20, 5))
        self.tooltip(btn_clear, "Xóa toàn bộ đường dẫn trong khung nguồn.")

        # --- KHU VỰC ĐÍCH ---
        dest_label = tk.Label(main_frame, text="📂 Thư mục đích:", font=("Segoe UI", 10, "bold"), 
                              bg="#f0f0f0", fg="#2c3e50")
        dest_label.pack(anchor="w", pady=(5, 5))
        
        dest_inner_frame = tk.Frame(main_frame, bg="#f0f0f0")
        dest_inner_frame.pack(fill="x", pady=(0, 5))
        
        self.dest_var = tk.StringVar()
        self.dest_entry = tk.Entry(dest_inner_frame, textvariable=self.dest_var, font=("Segoe UI", 10),
                                   relief="solid", highlightthickness=1, highlightbackground="#bdc3c7",
                                   bg="white")
        self.dest_entry.pack(fill="x")
        self.dest_entry.drop_target_register(DND_FILES)
        self.dest_entry.dnd_bind('<<Drop>>', self.handle_dest_drop)
        self.tooltip(self.dest_entry, "Kéo duy nhất 1 thư mục đích vào đây để lưu trữ dữ liệu.")

        # --- TÙY CHỌN (OPTIONS) ---
        opt_frame = ttk.LabelFrame(main_frame, text=" ⚙️  Cấu hình thực thi ", padding=5)
        opt_frame.pack(fill="x", pady=(0, 5))

        self.overwrite_var = tk.BooleanVar(value=True)
        self.move_var = tk.BooleanVar(value=False)
        self.multi_var = tk.BooleanVar(value=False)

        # Grid options
        cb_ovr = tk.Checkbutton(opt_frame, text="Ghi đè nếu file hoặc thư mục đã tồn tại.", variable=self.overwrite_var, 
                                bg="#f0f0f0", activebackground="#f0f0f0", font=("Segoe UI", 9))
        cb_ovr.grid(row=0, column=0, sticky="w", padx=10, pady=3)
        self.tooltip(cb_ovr, "Nếu trùng tên tại đích, dữ liệu cũ sẽ bị xóa để thay thế bằng dữ liệu mới.")

        cb_move = tk.Checkbutton(opt_frame, text="Di chuyển và xóa nguồn sau khi sao chép.", variable=self.move_var, 
                                 bg="#f0f0f0", activebackground="#f0f0f0", font=("Segoe UI", 9))
        cb_move.grid(row=0, column=1, sticky="w", padx=10, pady=3)
        self.tooltip(cb_move, "⚠️  LƯU Ý: File/Thư mục gốc sẽ bị xóa sau khi sao chép thành công sang đích.")

        cb_multi = tk.Checkbutton(opt_frame, text="Chế độ Multi-Copy (Copy Song song).", variable=self.multi_var, 
                                  bg="#f0f0f0", activebackground="#f0f0f0", font=("Segoe UI", 9))
        cb_multi.grid(row=1, column=0, sticky="w", padx=10, pady=3)
        self.tooltip(cb_multi, "BẬT: Sao chép nhiều file cùng lúc (Nhanh cho file nhỏ).\nTẮT: Sao chép lần lượt từng mục (Ổn định hơn).")

        # --- STATUS & PROGRESS ---
        self.status_label = tk.Label(main_frame, text="Trạng thái: Sẵn sàng", font=("Segoe UI", 9, "italic"), 
                                     fg="#7f8c8d", bg="#f0f0f0")
        self.status_label.pack(pady=(5, 3))
        
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress.pack(side="left",expand=True, fill="x", padx=5, pady=(0, 10))
        self.label_percent = tk.Label(main_frame, text="0%", font=("Segoe UI", 9), bg="#f0f0f0")
        self.label_percent.pack(side="right", padx=5, pady=(0, 10))

        # --- NÚT CHẠY ---
        self.btn_run = tk.Button(root, text="▶️  BẮT ĐẦU XỬ LÝ", command=self.start_threading,
                                 bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"),
                                 relief="flat", height=1, cursor="hand2", activebackground="#229954")
        self.btn_run.pack(fill="x", padx=5, pady=(5, 15))
        self.tooltip(self.btn_run, "Nhấn để bắt đầu quá trình sao chép/di chuyển dữ liệu.")


    def tooltip(self, widget, text):
        tooltip_window = [None]
        def show_tooltip(event):
            if tooltip_window[0] is not None: return
            tooltip_window[0] = tk.Toplevel(widget)
            tooltip_window[0].wm_overrideredirect(True)
            x = event.x_root + 15
            y = event.y_root + 15
            # Giới hạn tooltip không vượt quá màn hình
            if x + 200 > self.root.winfo_screenwidth():
                x = event.x_root - 215
            tooltip_window[0].wm_geometry(f"+{x}+{y}")
            label = tk.Label(tooltip_window[0], text=text, background="#fffacd", foreground="#2c2c2c", 
                             relief="solid", borderwidth=1, font=("Arial", 8, 'italic'), justify="left", padx=10, pady=6)
            label.pack()
        def hide_tooltip(event):
            if tooltip_window[0] is not None:
                tooltip_window[0].destroy()
                tooltip_window[0] = None
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    # --- XỬ LÝ KÉO THẢ ---
    def handle_src_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        for p in paths:
            self.src_text.insert(tk.END, p + "\n")

    def handle_dest_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        if paths and os.path.isdir(paths[0]):
            self.dest_var.set(paths[0])
        else:
            messagebox.showwarning("Cảnh báo", "Thư mục đích phải là một đường dẫn Folder hợp lệ!")

    # --- LOGIC SAO CHÉP ---
    def copy_engine(self, src, dest):
        try:
            if not os.path.exists(src): return False
            target = os.path.join(dest, os.path.basename(src))

            # Xử lý ghi đè
            if os.path.exists(target) and self.overwrite_var.get():
                if os.path.isdir(target): shutil.rmtree(target)
                else: os.remove(target)

            if self.move_var.get():
                shutil.move(src, target)
            else:
                if os.path.isdir(src):
                    shutil.copytree(src, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, target)
            return True
        except Exception as e:
            print(f"Lỗi khi xử lý {src}: {e}")
            return False
        
    def Select_files(self):
        paths = filedialog.askopenfilenames(title="Chọn file.", filetypes=[("Tất cả file", "*.*")], multiple=True)
        for p in paths:
            # Kiểm tra nếu là thư mục thì add vào src_text
            if os.path.isdir(p):
                self.src_text.insert(tk.END, p + "\n")

    def Select_folders(self):
        path = filedialog.askdirectory(title="Chọn thư mục.",mustexist=True)
        if path:
            self.src_text.insert(tk.END, path + "\n")

    def start_threading(self):
        # Chạy trong Thread để không bị Not Responding
        t = threading.Thread(target=self.execute_task, daemon=True)
        t.start()

    def execute_task(self):
        sources = [s.strip() for s in self.src_text.get("1.0", tk.END).split('\n') if s.strip()]
        dest = self.dest_var.get().strip()

        if not sources or not dest:
            messagebox.showwarning("⚠️  Thông tin", "Vui lòng nhập đầy đủ Nguồn và Đích!")
            return

        if not os.path.exists(dest):
            messagebox.showerror("❌ Lỗi", "Thư mục đích không tồn tại!\nVui lòng chọn một thư mục hợp lệ.")
            return

        self.btn_run.config(state=tk.DISABLED, bg="#95a5a6")
        self.progress["value"] = 0
        self.progress["maximum"] = len(sources)
        
        success_count = 0
        error_count = 0
        
        try:
            if self.multi_var.get():
                self.status_label.config(text="Trạng thái: Đang sao chép song song...")
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(self.copy_engine, s, dest) for s in sources]
                    for i, f in enumerate(futures):
                        if f.result(): 
                            success_count += 1
                        else:
                            error_count += 1
                        self.progress["value"] = i + 1
                        percent = int((i + 1) / len(sources) * 100)
                        self.label_percent.config(text=f"{percent}%")
                        self.root.update_idletasks()
            else:
                self.status_label.config(text="Trạng thái: Đang sao chép...")
                for i, src in enumerate(sources):
                    name = os.path.basename(src)
                    self.status_label.config(text=f"Đang sao chép tệp: {name} ({i+1}/{len(sources)})")
                    if self.copy_engine(src, dest):
                        success_count += 1
                    else:
                        error_count += 1
                    self.progress["value"] = i + 1
                    percent = int((i + 1) / len(sources) * 100)
                    self.label_percent.config(text=f"{percent}%")
                    self.root.update_idletasks()

            self.status_label.config(text=f"✓ Hoàn thành! Thành công: {success_count} | Lỗi: {error_count}")
            self.btn_run.config(state=tk.NORMAL, bg="#27ae60")
            
            if self.move_var.get() and success_count > 0:
                self.src_text.delete('1.0', tk.END)
            self.progress["value"] = 100
            self.label_percent.config(text="100%")
            result_msg = f"Xử lý hoàn tất!\n\n✓ Thành công: {success_count} mục\n❌ Lỗi: {error_count} mục"
            messagebox.showinfo("✓ Kết quả", result_msg)
        except Exception as e:
            messagebox.showerror("❌ Lỗi", f"Đã xảy ra lỗi: {str(e)}")
            self.btn_run.config(state=tk.NORMAL, bg="#27ae60")
            self.status_label.config(text="Trạng thái: Lỗi trong quá trình xử lý")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = UltimateCopyPro(root)
    root.mainloop()
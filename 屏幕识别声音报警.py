import tkinter as tk
from tkinter import messagebox
import time
import winsound
import threading
import random

class ReactionTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("声音反应速度测试")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # 设置颜色主题
        self.bg_color = "#f0f8ff"
        self.button_color = "#4CAF50"
        self.reaction_button_color = "#FF5252"
        self.text_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
        
        # 初始化变量
        self.start_time = None
        self.test_running = False
        self.test_count = 0
        self.timer_running = False
        
        # 创建界面元素
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="声音反应速度测试", 
                              font=("Arial", 20, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=20)
        
        # 说明文字
        instruction_text = (
            "测试说明：\n"
            "1. 点击'开始测试'按钮\n"
            "2. 等待声音播放（1-3秒随机延迟）\n"
            "3. 听到440Hz声音后立即按下'反应'按钮\n"
            "4. 查看您的反应时间\n"
            "注意：按下按钮瞬间即停止计时"
        )
        instruction_label = tk.Label(main_frame, text=instruction_text,
                                    font=("Arial", 10),
                                    justify=tk.LEFT,
                                    bg=self.bg_color, fg=self.text_color)
        instruction_label.pack(pady=10)
        
        # 状态显示区域
        status_frame = tk.Frame(main_frame, bg=self.bg_color)
        status_frame.pack(pady=15)
        
        self.status_label = tk.Label(status_frame, text="准备开始测试", 
                                    font=("Arial", 12, "bold"), 
                                    fg="blue", bg=self.bg_color)
        self.status_label.pack()
        
        # 反应时间显示
        self.time_label = tk.Label(status_frame, text="反应时间: -- ms", 
                                  font=("Arial", 16, "bold"),
                                  bg=self.bg_color, fg="#2E7D32")
        self.time_label.pack(pady=10)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        # 开始测试按钮
        self.start_button = tk.Button(button_frame, text="开始测试", 
                                     font=("Arial", 14, "bold"), 
                                     command=self.start_test,
                                     bg=self.button_color,
                                     fg="white",
                                     width=12, height=2,
                                     relief="raised",
                                     bd=3)
        self.start_button.pack(pady=10)
        
        # 反应按钮 - 更大更显眼
        self.reaction_button = tk.Button(button_frame, text="反 应", 
                                        font=("Arial", 16, "bold"), 
                                        command=self.react,  # 保留原有的command
                                        state=tk.DISABLED,
                                        bg="#CCCCCC",  # 禁用时的颜色
                                        fg="white",
                                        width=12, height=2,
                                        relief="raised",
                                        bd=3)
        self.reaction_button.pack(pady=10)
        
        # 绑定鼠标按下事件 - 这是关键修改
        self.reaction_button.bind('<ButtonPress-1>', self.on_reaction_button_press)
        
        # 实时计时器区域
        timer_frame = tk.Frame(main_frame, bg=self.bg_color)
        timer_frame.pack(pady=15, fill='x')
        
        timer_title = tk.Label(timer_frame, text="实时计时器", 
                             font=("Arial", 12, "bold"),
                             bg=self.bg_color, fg=self.text_color)
        timer_title.pack()
        
        # 实时计时器显示框
        self.timer_text = tk.Text(timer_frame, height=4, width=50,
                                 font=("Consolas", 10),
                                 wrap=tk.WORD,
                                 bg="#000000",
                                 fg="#00FF00",
                                 relief="sunken",
                                 bd=2)
        self.timer_text.pack(pady=5, fill='x')
        
        # 在计时器文本框中添加初始提示
        self.timer_text.insert(tk.END, "计时器准备就绪...\n")
        self.timer_text.insert(tk.END, "点击'开始测试'后，此处将显示实时计时数据\n")
        self.timer_text.config(state=tk.DISABLED)
        
        # 历史记录区域
        history_frame = tk.Frame(main_frame, bg=self.bg_color)
        history_frame.pack(pady=10, fill='both', expand=True)
        
        history_title = tk.Label(history_frame, text="测试历史记录", 
                               font=("Arial", 12, "bold"),
                               bg=self.bg_color, fg=self.text_color)
        history_title.pack()
        
        # 创建带滚动条的文本框
        text_frame = tk.Frame(history_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.history_text = tk.Text(text_frame, height=5, width=50,
                                   font=("Arial", 9),
                                   wrap=tk.WORD)
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始提示
        self.history_text.insert(tk.END, "欢迎使用声音反应速度测试！\n")
        self.history_text.insert(tk.END, "点击'开始测试'按钮开始第一次测试。\n\n")
        self.history_text.config(state=tk.DISABLED)
        
    def enable_reaction_button(self):
        """启用反应按钮并改变颜色"""
        self.reaction_button.config(state=tk.NORMAL, 
                                  bg=self.reaction_button_color,
                                  cursor="hand2")
        
    def disable_reaction_button(self):
        """禁用反应按钮并改变颜色"""
        self.reaction_button.config(state=tk.DISABLED, 
                                  bg="#CCCCCC",
                                  cursor="arrow")
        
    def update_timer_display(self):
        """更新实时计时器显示"""
        if self.timer_running and self.start_time is not None:
            current_time = time.time()
            elapsed_ms = int((current_time - self.start_time) * 1000)
            
            # 更新计时器文本框
            self.timer_text.config(state=tk.NORMAL)
            # 保留最近10条记录
            content = self.timer_text.get(1.0, tk.END)
            lines = content.split('\n')
            if len(lines) > 10:
                self.timer_text.delete(1.0, tk.END)
                self.timer_text.insert(tk.END, '\n'.join(lines[-10:]) + '\n')
            
            self.timer_text.insert(tk.END, f"+{elapsed_ms:4d} ms\n")
            self.timer_text.see(tk.END)
            self.timer_text.config(state=tk.DISABLED)
            
            # 每50毫秒更新一次
            if self.timer_running:
                self.root.after(50, self.update_timer_display)
        
    def start_test(self):
        # 重置状态
        self.test_running = False
        self.disable_reaction_button()
        self.start_button.config(state=tk.DISABLED)
        
        # 清空计时器显示
        self.timer_text.config(state=tk.NORMAL)
        self.timer_text.delete(1.0, tk.END)
        self.timer_text.insert(tk.END, "计时器启动准备...\n")
        self.timer_text.insert(tk.END, "等待声音播放...\n")
        self.timer_text.config(state=tk.DISABLED)
        self.timer_text.see(tk.END)
        
        # 更新状态
        self.status_label.config(text="准备中...请等待声音", fg="orange")
        self.time_label.config(text="反应时间: -- ms")
        self.root.update()
        
        # 在历史记录中添加新测试标记
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"\n--- 测试 #{self.test_count + 1} ---\n")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
        
        # 随机延迟1-3秒
        delay = random.uniform(1.0, 3.0)
        self.root.after(int(delay * 1000), self.play_sound_and_start_timer)
        
    def play_sound_and_start_timer(self):
        # 启用反应按钮
        self.enable_reaction_button()
        
        # 播放声音
        threading.Thread(target=self.play_sound, daemon=True).start()
        
        # 开始计时
        self.start_time = time.time()
        self.test_running = True
        self.timer_running = True
        self.test_count += 1
        
        # 更新计时器显示
        self.timer_text.config(state=tk.NORMAL)
        self.timer_text.insert(tk.END, "声音播放！开始计时...\n")
        self.timer_text.insert(tk.END, "0 ms - 开始\n")
        self.timer_text.config(state=tk.DISABLED)
        self.timer_text.see(tk.END)
        
        # 启动实时计时器更新
        self.update_timer_display()
        
        # 更新状态
        self.status_label.config(text="声音已播放！立即按下反应按钮", fg="red")
        
    def play_sound(self):
        try:
            # 播放440Hz，0.5秒的声音
            winsound.Beep(440, 500)
        except Exception as e:
            messagebox.showerror("错误", f"无法播放声音: {e}")
    
    def on_reaction_button_press(self, event):
        """鼠标按下时的反应处理"""
        self.react()
        
    def react(self):
        if not self.test_running or self.start_time is None:
            messagebox.showwarning("警告", "请先点击'开始测试'按钮！")
            return
            
        # 停止计时
        self.timer_running = False
        end_time = time.time()
        reaction_time = int((end_time - self.start_time) * 1000)  # 转换为毫秒
        
        # 在计时器中显示最终结果
        self.timer_text.config(state=tk.NORMAL)
        self.timer_text.insert(tk.END, f"=== 最终结果: {reaction_time} ms ===\n")
        self.timer_text.config(state=tk.DISABLED)
        self.timer_text.see(tk.END)
        
        # 更新显示
        evaluation = self.get_evaluation(reaction_time)
        self.time_label.config(text=f"反应时间: {reaction_time} ms\n({evaluation})")
        
        # 添加到历史记录
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"反应时间: {reaction_time} ms - {evaluation}\n")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
        
        # 重置状态
        self.test_running = False
        self.start_time = None
        self.disable_reaction_button()
        self.start_button.config(state=tk.NORMAL)
        self.status_label.config(text="测试完成！点击'开始测试'再次测试", fg="green")
        
    def get_evaluation(self, reaction_time):
        """根据反应时间给出评价"""
        if reaction_time < 180:
            return "⚡ 超人的反应！"
        elif reaction_time < 220:
            return "🎯 非常出色！"
        elif reaction_time < 280:
            return "👍 反应很快"
        elif reaction_time < 350:
            return "✅ 良好水平"
        elif reaction_time < 450:
            return "📊 平均水平"
        else:
            return "🐢 需要练习"

if __name__ == "__main__":
    root = tk.Tk()
    app = ReactionTestApp(root)
    root.mainloop()
import json
import math
from pathlib import Path
import queue
import socket
import threading
import time
import sys
import uuid
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import chess
import chess.pgn
from PIL import Image, ImageTk

from .client import NetworkClient, PracticeBot, discover
from .server import GameServer

ROOT=Path(__file__).resolve().parents[1]
BG='#101512'
PANEL='#19211c'
CARD='#202b24'
LINE='#334238'
TEXT='#edf1e6'
MUTED='#99aa9b'
GREEN='#b5dc86'
INK='#1c2b1a'
GOLD='#e1b77a'
LIGHT='#d8d2b6'
DARK='#758b70'


def label(parent,text='',size=11,color=TEXT,bg=None,bold=False,**kwargs):
    return tk.Label(parent,text=text,font=('Segoe UI',size,'bold' if bold else 'normal'),
                    fg=color,bg=bg or parent.cget('bg'),**kwargs)


def button(parent,text,command,primary=False,small=False,**kwargs):
    return tk.Button(parent,text=text,command=command,font=('Segoe UI',10 if small else 11,'bold'),
                     bg=GREEN if primary else CARD,fg=INK if primary else TEXT,
                     activebackground='#cae9a7' if primary else LINE,activeforeground=INK if primary else TEXT,
                     relief='flat',bd=0,cursor='hand2',padx=14,pady=8 if small else 11,
                     highlightthickness=0,**kwargs)


def entry(parent,variable=None,show=None):
    return tk.Entry(parent,textvariable=variable,show=show,font=('Segoe UI',11),
                    bg=BG,fg=TEXT,insertbackground=GREEN,relief='flat',bd=0,
                    highlightbackground=LINE,highlightcolor=GREEN,highlightthickness=1)


class ChessApp:
    def __init__(self, root, show_login=True):
        self.root=root
        root.title('Pixel Chess • Cờ vua kết nối')
        root.geometry('1280x860')
        root.minsize(1100,760)
        root.configure(bg=BG)
        self.events=queue.Queue()
        self.client=None
        self.server=None
        self.bot=None
        self.pending_bot=False
        self.guest_pending=False
        self.state=None
        self.board=chess.Board()
        self.selected=None
        self.drag=None
        self.flipped=False
        self.name=''
        self.elo=1200
        self.rooms=[]
        self.clock_base=[300,300]
        self.clock_at=time.monotonic()
        self.last_udp=None
        self.last_ping=0
        self.latency=None
        self.modal=None
        self.closing=False
        self.images={}
        self.base_images={k:Image.open(ROOT/f'assets/{k}.png').convert('RGBA') for k in
                          [c+p for c in ('w','b') for p in 'rnbqkp']}
        self.prefs_path=ROOT/'.local/client.json'
        try:
            self.prefs=json.loads(self.prefs_path.read_text(encoding='utf-8'))
        except (OSError,ValueError):
            self.prefs={}
        self.host=self.prefs.get('host','127.0.0.1')
        self.port=int(self.prefs.get('port',8765))
        self.configure_style()
        self.build()
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.bind('<Escape>',lambda e:self.clear_selection())
        root.bind('<Control-f>',lambda e:self.flip())
        root.after(80,self.pump)
        root.after(120,self.animate_clock)
        if show_login:
            root.after(250,self.login_dialog)

    def configure_style(self):
        style=ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',fieldbackground=BG,background=CARD,foreground=TEXT,
                        arrowcolor=GREEN,bordercolor=LINE,selectbackground=CARD,selectforeground=TEXT,padding=5)
        style.map('TCombobox',fieldbackground=[('readonly',BG)],selectbackground=[('readonly',BG)],foreground=[('readonly',TEXT)])
        style.configure('Treeview',background=PANEL,fieldbackground=PANEL,foreground=TEXT,
                        rowheight=30,borderwidth=0,font=('Segoe UI',10))
        style.configure('Treeview.Heading',background=CARD,foreground=MUTED,font=('Segoe UI',9,'bold'),relief='flat')
        style.map('Treeview',background=[('selected',LINE)],foreground=[('selected',GREEN)])
        style.configure('Vertical.TScrollbar',background=LINE,troughcolor=PANEL,borderwidth=0,arrowcolor=MUTED)

    def build(self):
        header=tk.Frame(self.root,bg=BG,height=76)
        header.pack(fill='x',padx=26,pady=(18,12))
        logo=tk.Canvas(header,width=42,height=44,bg=BG,highlightthickness=0)
        logo.pack(side='left',padx=(0,12))
        logo.create_rectangle(0,0,42,42,fill=GREEN,outline='')
        logo.create_text(21,21,text='♞',fill=INK,font=('Segoe UI Symbol',29))
        title=tk.Frame(header,bg=BG)
        title.pack(side='left')
        label(title,'PIXEL CHESS',18,bold=True).pack(anchor='w')
        label(title,'Một bàn cờ. Mọi kết nối.',10,MUTED).pack(anchor='w')
        self.profile=button(header,'Kết nối server',self.login_dialog,small=True)
        self.profile.pack(side='right')
        self.connection=label(header,'●  Chưa kết nối',10,MUTED)
        self.connection.pack(side='right',padx=20)
        body=tk.Frame(self.root,bg=BG)
        body.pack(fill='both',expand=True,padx=24)
        body.columnconfigure(1,weight=1)
        body.rowconfigure(0,weight=1)
        self.left=tk.Frame(body,bg=PANEL,width=220)
        self.left.grid(row=0,column=0,sticky='nsew',padx=(0,18))
        self.left.grid_propagate(False)
        self.left.pack_propagate(False)
        self.build_left()
        self.middle=tk.Frame(body,bg=BG)
        self.middle.grid(row=0,column=1,sticky='nsew')
        self.middle.rowconfigure(2,weight=1)
        self.middle.columnconfigure(0,weight=1)
        line=tk.Frame(self.middle,bg=BG)
        line.grid(row=0,column=0,sticky='ew',pady=(0,10))
        self.room_title=label(line,'Bàn cờ của bạn',14,bold=True)
        self.room_title.pack(side='left')
        self.room_badge=label(line,'SẴN SÀNG',9,GREEN)
        self.room_badge.pack(side='right')
        self.top_player=self.player_card(self.middle,'Đối thủ','Đang chờ một kỳ thủ…')
        self.top_player['frame'].grid(row=1,column=0,sticky='ew',pady=(0,10))
        self.canvas=tk.Canvas(self.middle,bg=BG,highlightthickness=0)
        self.canvas.grid(row=2,column=0,sticky='nsew')
        self.canvas.bind('<Configure>',lambda e:self.draw_board())
        self.canvas.bind('<ButtonPress-1>',self.press)
        self.canvas.bind('<B1-Motion>',self.motion)
        self.canvas.bind('<ButtonRelease-1>',self.release)
        self.bottom_player=self.player_card(self.middle,'Bạn','Đăng nhập để bắt đầu')
        self.bottom_player['frame'].grid(row=3,column=0,sticky='ew',pady=(10,0))
        controls=tk.Frame(self.middle,bg=BG)
        controls.grid(row=4,column=0,sticky='ew',pady=(10,0))
        button(controls,'↻  Lật bàn',self.flip,small=True).pack(side='left')
        button(controls,'½  Hòa',lambda:self.send('DRAW'),small=True).pack(side='left',padx=6)
        button(controls,'⚑  Đầu hàng',self.resign,small=True).pack(side='left')
        button(controls,'PGN ↓',self.export_pgn,small=True).pack(side='right')
        self.right=tk.Frame(body,bg=PANEL,width=260)
        self.right.grid(row=0,column=2,sticky='nsew',padx=(18,0))
        self.right.pack_propagate(False)
        self.build_right()
        footer=tk.Frame(self.root,bg=BG)
        footer.pack(fill='x',padx=26,pady=(10,14))
        self.status=label(footer,'Chọn một quân để xem nước đi hợp lệ. Kéo thả hoặc bấm ô đích.',10,MUTED)
        self.status.pack(side='left')
        self.transport=label(footer,'TCP 8765  /  UDP 9999',9,MUTED)
        self.transport.pack(side='right')

    def build_left(self):
        pad=tk.Frame(self.left,bg=PANEL)
        pad.pack(fill='x',padx=16,pady=18)
        label(pad,'CÙNG VÀO VÁN',9,GREEN,bold=True).pack(anchor='w',pady=(0,12))
        label(pad,'Chơi một ván hay.',16,bold=True).pack(anchor='w')
        label(pad,'Tìm đối thủ, kết nối bạn bè.',9,MUTED).pack(anchor='w',pady=(4,16))
        self.control=tk.StringVar(value='5+0')
        self.time_select=ttk.Combobox(pad,textvariable=self.control,values=['3+0','5+0','10+5'],state='readonly',font=('Segoe UI',11))
        self.time_select.pack(fill='x',pady=(0,4))
        label(pad,'phút + giây cộng mỗi nước',8,MUTED).pack(anchor='w',pady=(0,12))
        self.match_button=button(pad,'Ghép trận ngẫu nhiên',self.match,primary=True)
        self.match_button.pack(fill='x',pady=(0,8))
        self.queued=False
        button(pad,'+  Tạo phòng',self.create_dialog).pack(fill='x',pady=(0,8))
        button(pad,'♟  Đấu với PixelBot',self.play_bot).pack(fill='x')
        row=tk.Frame(self.left,bg=PANEL)
        row.pack(fill='x',padx=16,pady=(4,8))
        label(row,'SẢNH CHỜ',9,MUTED,bold=True).pack(side='left')
        self.online=label(row,'0 online',9,GREEN)
        self.online.pack(side='right')
        self.room_list=tk.Listbox(self.left,bg=PANEL,fg=TEXT,selectbackground=LINE,selectforeground=GREEN,
                                 font=('Segoe UI',10),highlightthickness=0,bd=0,activestyle='none',height=5)
        self.room_list.pack(fill='both',expand=True,padx=12)
        self.room_list.bind('<Double-Button-1>',lambda e:self.join_selected())
        row=tk.Frame(self.left,bg=PANEL)
        row.pack(fill='x',padx=14,pady=8)
        button(row,'Vào đấu',self.join_selected,small=True).pack(side='left',expand=True,fill='x',padx=(0,5))
        button(row,'Vào xem',lambda:self.join_selected(True),small=True).pack(side='left',expand=True,fill='x')
        button(self.left,'Nhập mã phòng',self.code_dialog,small=True).pack(fill='x',padx=14,pady=(0,6))
        button(self.left,'Lịch sử & ELO',lambda:self.send('HISTORY'),small=True).pack(fill='x',padx=14,pady=(0,6))
        button(self.left,'Rời phòng',self.leave,small=True).pack(fill='x',padx=14,pady=(0,6))
        bottom=tk.Frame(self.left,bg=CARD)
        bottom.pack(fill='x',padx=14,pady=(8,14))
        label(bottom,'KẾT NỐI THỜI GIAN THỰC',8,MUTED,bg=CARD,bold=True).pack(anchor='w',padx=10,pady=(10,4))
        self.net_info=label(bottom,'●  TCP · nước đi & chat\n●  UDP · đồng hồ & biểu cảm',9,GREEN,bg=CARD,justify='left')
        self.net_info.pack(anchor='w',padx=10,pady=(0,10))

    def player_card(self,parent,name,detail):
        frame=tk.Frame(parent,bg=PANEL,height=65)
        frame.pack_propagate(False)
        avatar=label(frame,'♟',25,GREEN)
        avatar.pack(side='left',padx=(14,12))
        box=tk.Frame(frame,bg=PANEL)
        box.pack(side='left',pady=10)
        name_label=label(box,name,11,bold=True)
        name_label.pack(anchor='w')
        details=label(box,detail,9,MUTED)
        details.pack(anchor='w')
        clock=label(frame,'05:00',25,TEXT,bold=True,padx=14)
        clock.pack(side='right',fill='y')
        return dict(frame=frame,name=name_label,detail=details,clock=clock,avatar=avatar)

    def build_right(self):
        top=tk.Frame(self.right,bg=PANEL)
        top.pack(fill='x',padx=16,pady=18)
        label(top,'VÁN ĐẤU',9,GREEN,bold=True).pack(anchor='w')
        self.game_status=label(top,'Nước đầu tiên đang chờ.',13,bold=True,wraplength=230,justify='left')
        self.game_status.pack(anchor='w',pady=(10,4))
        self.game_detail=label(top,'Bắt đầu từ sảnh chờ bên trái.',9,MUTED,wraplength=230,justify='left')
        self.game_detail.pack(anchor='w')
        tk.Frame(self.right,bg=LINE,height=1).pack(fill='x',padx=16)
        moves_header=tk.Frame(self.right,bg=PANEL)
        moves_header.pack(fill='x',padx=16,pady=(14,10))
        label(moves_header,'NHẬT KÝ NƯỚC ĐI',9,MUTED,bold=True).pack(side='left')
        self.move_count=label(moves_header,'0',9,GREEN)
        self.move_count.pack(side='right')
        self.move_tree=ttk.Treeview(self.right,columns=('no','white','black'),show='headings',height=6,selectmode='none')
        for col,text,width in [('no','#',35),('white','TRẮNG',90),('black','ĐEN',90)]:
            self.move_tree.heading(col,text=text)
            self.move_tree.column(col,width=width,anchor='center',stretch=col!='no')
        self.move_tree.pack(fill='x',padx=12)
        button(self.right,'Yêu cầu hòa theo luật',lambda:self.send('CLAIM_DRAW'),small=True).pack(fill='x',padx=14,pady=10)
        chat_top=tk.Frame(self.right,bg=PANEL)
        chat_top.pack(fill='x',padx=16,pady=(8,10))
        label(chat_top,'TRÒ CHUYỆN',9,MUTED,bold=True).pack(side='left')
        self.spectators=label(chat_top,'0 đang xem',9,GREEN)
        self.spectators.pack(side='right')
        self.chat=tk.Text(self.right,bg=PANEL,fg=TEXT,font=('Segoe UI',10),relief='flat',bd=0,
                          wrap='word',state='disabled',height=6,padx=8,pady=6)
        self.chat.tag_configure('name',foreground=GREEN,font=('Segoe UI',9,'bold'))
        self.chat.tag_configure('system',foreground=MUTED,font=('Segoe UI',9))
        self.chat.pack(fill='both',expand=True,padx=10)
        self.chat_messages=[]
        self.append_chat('system','Chào mừng đến Pixel Chess.\nTin nhắn trong phòng sẽ hiện ở đây.')
        emojis=tk.Frame(self.right,bg=PANEL)
        emojis.pack(fill='x',padx=12,pady=(6,8))
        for emoji in ('👍','🔥','👏','🤔'):
            button(emojis,emoji,lambda e=emoji:self.emoji(e),small=True).pack(side='left',expand=True,fill='x',padx=2)
        chat_row=tk.Frame(self.right,bg=PANEL)
        chat_row.pack(fill='x',padx=14,pady=(0,16))
        self.chat_var=tk.StringVar()
        chat_entry=entry(chat_row,self.chat_var)
        chat_entry.pack(side='left',fill='x',expand=True,ipady=9)
        chat_entry.bind('<Return>',lambda e:self.send_chat())
        button(chat_row,'↑',self.send_chat,primary=True,small=True).pack(side='right',padx=(6,0))

    def new_modal(self,title,width=450):
        if self.modal and self.modal.winfo_exists():
            self.modal.destroy()
        win=tk.Toplevel(self.root)
        self.modal=win
        win.title(title)
        win.configure(bg=PANEL)
        win.resizable(False,False)
        win.transient(self.root)
        x=self.root.winfo_x()+(self.root.winfo_width()-width)//2
        win.geometry(f'{width}x460+{max(0,x)}+{max(0,self.root.winfo_y()+120)}')
        win.grab_set()
        wrap=tk.Frame(win,bg=PANEL)
        wrap.pack(fill='both',expand=True,padx=26,pady=24)
        label(wrap,title,18,bold=True).pack(anchor='w',pady=(0,14))
        return win,wrap

    def login_dialog(self):
        if self.client and self.client.connected:
            win,wrap=self.new_modal('Kết nối của bạn')
            label(wrap,f'{self.name} · {self.elo} ELO',13,GREEN).pack(anchor='w',pady=10)
            label(wrap,f'Server: {self.host}:{self.port}\nKhôi phục phiên trong 60 giây.\nĐồng hồ tiếp tục chạy khi mất mạng.',11,MUTED,justify='left').pack(anchor='w',pady=12)
            button(wrap,'Thử ngắt mạng & kết nối lại',lambda:(self.client.disconnect_transport(),win.destroy()),primary=True).pack(fill='x',pady=10)
            button(wrap,'Đăng xuất',lambda:(self.logout(),win.destroy())).pack(fill='x')
            return
        win,wrap=self.new_modal('Kết nối bàn cờ',490)
        win.geometry('490x700')
        label(wrap,'Đăng nhập hoặc tạo tài khoản trên server.',10,MUTED).pack(anchor='w',pady=(0,12))
        host_var=tk.StringVar(value=f'{self.host}:{self.port}')
        name_var=tk.StringVar(value=self.prefs.get('name',''))
        pw_var=tk.StringVar()
        label(wrap,'Địa chỉ server',10,MUTED).pack(anchor='w')
        entry(wrap,host_var).pack(fill='x',ipady=10,pady=(5,8))
        row=tk.Frame(wrap,bg=PANEL)
        row.pack(fill='x',pady=(0,10))
        discover_note=label(wrap,'Máy chủ cục bộ sẽ tự khởi động ở 127.0.0.1.',9,MUTED,wraplength=430,justify='left')
        def scan():
            discover_note.config(text='Đang tìm server trong LAN…')
            def worker():
                self.events.put({'type':'DISCOVERED','servers':discover(),'host_var':host_var,'note':discover_note,'parent':win})
            threading.Thread(target=worker,daemon=True).start()
        button(row,'⌕  Tìm server LAN',scan,small=True).pack(side='left')
        button(row,'Máy này',lambda:host_var.set('127.0.0.1:8765'),small=True).pack(side='right')
        discover_note.pack(anchor='w',pady=(0,16))
        label(wrap,'Tên tài khoản',10,MUTED).pack(anchor='w')
        name_entry=entry(wrap,name_var)
        name_entry.pack(fill='x',ipady=10,pady=(5,12))
        label(wrap,'Mật khẩu',10,MUTED).pack(anchor='w')
        password=entry(wrap,pw_var,show='●')
        password.pack(fill='x',ipady=10,pady=(5,12))
        self.auth_note=label(wrap,'',10,GOLD,wraplength=430,justify='left')
        self.auth_note.pack(anchor='w',pady=(0,8))
        def login(register=False,resume=False):
            try:
                raw=host_var.get().strip()
                host,p=raw.rsplit(':',1) if ':' in raw else (raw,'8765')
                port=int(p)
                if not host or not 1<=port<=65535:
                    raise ValueError()
            except ValueError:
                self.auth_note.config(text='Địa chỉ có dạng IP:8765.')
                return
            if not resume and (len(name_var.get().strip())<2 or len(pw_var.get())<4):
                self.auth_note.config(text='Nhập tên từ 2 ký tự và mật khẩu từ 4 ký tự.')
                return
            self.host,self.port=host,port
            if self.client:
                self.client.close()
            self.client=NetworkClient(self.events.put)
            self.auth_note.config(text='Đang kết nối…')
            # Read Tk variables on the GUI thread before starting networking.
            credentials=(name_var.get().strip(),pw_var.get(),register,self.prefs.get('token') if resume else None)
            def start_safe():
                if host in ('127.0.0.1','localhost'):
                    try:
                        with socket.create_connection((host,port),timeout=.5):
                            pass
                    except OSError:
                        try:
                            self.server=GameServer(port=port,db_path=ROOT/'data/chess.db').start()
                        except OSError as exc:
                            self.events.put({'type':'AUTH_ERROR','message':'Không khởi động được server: '+str(exc)})
                            return
                self.client.connect(host,port,*credentials)
            threading.Thread(target=start_safe,daemon=True).start()
        button(wrap,'Đăng nhập',login,primary=True).pack(fill='x',pady=(0,8))
        button(wrap,'Tạo tài khoản mới',lambda:login(True)).pack(fill='x',pady=(0,8))
        if self.prefs.get('token'):
            button(wrap,'Khôi phục phiên trước',lambda:login(resume=True),small=True).pack(fill='x')
        button(wrap,'Chơi thử ngay với máy',self.play_guest,small=True).pack(fill='x',pady=(8,0))
        password.bind('<Return>',lambda e:login())
        name_entry.focus_set()

    def play_guest(self):
        if self.modal and self.modal.winfo_exists():
            self.modal.destroy()
        self.host,self.port='127.0.0.1',8765
        self.guest_pending=True
        self.client=NetworkClient(self.events.put)
        self.toast('Đang chuẩn bị bàn luyện tập…')
        def worker():
            try:
                with socket.create_connection((self.host,self.port),timeout=.5):
                    pass
            except OSError:
                try:
                    self.server=GameServer(port=self.port,db_path=ROOT/'data/chess.db').start()
                except OSError as exc:
                    self.events.put({'type':'AUTH_ERROR','message':str(exc)})
                    return
            self.client.connect(self.host,self.port,'Khach_'+uuid.uuid4().hex[:6],uuid.uuid4().hex,True)
        threading.Thread(target=worker,daemon=True).start()

    def require_connection(self):
        if not self.client or not self.client.connected:
            self.login_dialog()
            return False
        return True

    def send(self,kind,**kwargs):
        if self.require_connection():
            if not self.client.send(kind,**kwargs):
                self.toast('Đang mất kết nối. Vui lòng chờ khôi phục phiên.')

    def create_dialog(self):
        if not self.require_connection():
            return
        if self.state:
            self.toast('Hãy rời phòng hiện tại trước khi tạo phòng mới.')
            return
        win,wrap=self.new_modal('Tạo một bàn cờ')
        win.geometry('450x350')
        title=tk.StringVar(value='Bàn của '+self.name)
        entry(wrap,title).pack(fill='x',ipady=10,pady=(0,16))
        private=tk.BooleanVar(value=False)
        tk.Checkbutton(wrap,text='Phòng riêng · chỉ vào bằng mã',variable=private,bg=PANEL,fg=TEXT,
                       activebackground=PANEL,activeforeground=TEXT,selectcolor=BG,font=('Segoe UI',10)).pack(anchor='w')
        label(wrap,'Thời gian: '+self.control.get()+'  •  Bạn cầm quân trắng',10,MUTED).pack(anchor='w',pady=14)
        button(wrap,'Mở phòng',lambda:(self.send('CREATE',title=title.get(),private=private.get(),control=self.control.get()),win.destroy()),primary=True).pack(fill='x')

    def code_dialog(self):
        if not self.require_connection():
            return
        win,wrap=self.new_modal('Vào phòng bằng mã')
        win.geometry('450x310')
        code=tk.StringVar()
        field=entry(wrap,code)
        field.pack(fill='x',ipady=12,pady=12)
        field.focus_set()
        row=tk.Frame(wrap,bg=PANEL)
        row.pack(fill='x',pady=14)
        button(row,'Vào đấu',lambda:(self.send('JOIN',id=code.get().strip().upper()),win.destroy()),primary=True).pack(side='left',expand=True,fill='x',padx=(0,8))
        button(row,'Vào xem',lambda:(self.send('SPECTATE',id=code.get().strip().upper()),win.destroy())).pack(side='left',expand=True,fill='x')

    def join_selected(self,spectate=False):
        selected=self.room_list.curselection()
        if not selected or not self.rooms:
            self.toast('Chọn một phòng trong sảnh chờ.')
            return
        room=self.rooms[selected[0]]
        self.send('SPECTATE' if spectate else 'JOIN',id=room['id'])

    def match(self):
        if not self.require_connection():
            return
        if self.queued:
            self.send('CANCEL_MATCH')
        else:
            self.send('MATCH',control=self.control.get())

    def play_bot(self):
        if not self.require_connection():
            return
        if self.state:
            self.toast('Hãy rời phòng hiện tại trước khi đấu với máy.')
            return
        self.pending_bot=True
        self.send('CREATE',title='Luyện tập · '+self.name,private=True,control=self.control.get())

    def resign(self):
        if not self.state or self.state['role']<0 or self.state['status']!='playing':
            self.toast('Chưa có ván đấu để đầu hàng.')
            return
        if messagebox.askyesno('Đầu hàng','Kết thúc ván đấu và nhận thua?',parent=self.root):
            self.send('RESIGN')

    def leave(self):
        if not self.state:
            return
        if self.state['status']=='playing' and self.state['role']>=0:
            if not messagebox.askyesno('Rời phòng','Rời phòng khi đang đấu sẽ được tính là thua. Tiếp tục?',parent=self.root):
                return
        self.send('LEAVE')
        if self.bot:
            self.bot.close()
            self.bot=None

    def logout(self):
        if self.bot:
            self.bot.close()
            self.bot=None
        if self.client:
            self.client.send('LEAVE')
            self.client.close()
            self.client=None
        self.prefs.pop('token',None)
        self.save_prefs()
        self.reset_board()
        self.name=''
        self.connection.config(text='●  Chưa kết nối',fg=MUTED)
        self.profile.config(text='Kết nối server')
        self.room_list.delete(0,'end')

    def save_prefs(self):
        self.prefs_path.parent.mkdir(parents=True,exist_ok=True)
        self.prefs_path.write_text(json.dumps(self.prefs,ensure_ascii=False,indent=2),encoding='utf-8')

    def clear_selection(self):
        self.selected=None
        self.drag=None
        self.draw_board()

    def reset_board(self):
        self.state=None
        self.board=chess.Board()
        self.selected=None
        self.chat_messages=[]
        self.chat.config(state='normal')
        self.chat.delete('1.0','end')
        self.chat.config(state='disabled')
        self.append_chat('system','Chọn một phòng để bắt đầu trò chuyện.')
        self.clock_base=[300,300]
        self.clock_at=time.monotonic()
        self.move_tree.delete(*self.move_tree.get_children())
        self.room_title.config(text='Bàn cờ của bạn')
        self.room_badge.config(text='SẴN SÀNG')
        self.game_status.config(text='Nước đầu tiên đang chờ.')
        self.game_detail.config(text='Bắt đầu từ sảnh chờ bên trái.')
        self.move_count.config(text='0')
        self.spectators.config(text='0 đang xem')
        self.update_players()
        self.draw_board()

    def square_xy(self,square):
        file,rank=chess.square_file(square),chess.square_rank(square)
        col,row=(7-file,rank) if self.flipped else (file,7-rank)
        return self.bx+col*self.cell,self.by+row*self.cell

    def event_square(self,event):
        col=int((event.x-self.bx)//self.cell)
        row=int((event.y-self.by)//self.cell)
        if not 0<=col<8 or not 0<=row<8:
            return None
        return chess.square(7-col,row) if self.flipped else chess.square(col,7-row)

    def draw_board(self):
        c=self.canvas
        width,height=c.winfo_width(),c.winfo_height()
        if width<20 or height<20:
            return
        self.cell=max(16,min((width-34)//8,(height-30)//8))
        size=self.cell*8
        self.bx=(width-size)//2
        self.by=(height-size)//2
        c.delete('all')
        c.create_rectangle(self.bx-4,self.by-4,self.bx+size+4,self.by+size+4,fill=LINE,outline='')
        last=set()
        if self.state and self.state['moves']:
            uci=self.state['moves'][-1]['uci']
            last={chess.parse_square(uci[:2]),chess.parse_square(uci[2:4])}
        legal=[]
        if self.selected is not None and self.state:
            legal=[chess.Move.from_uci(m).to_square for m in self.state['legal'] if m.startswith(chess.square_name(self.selected))]
        for square in chess.SQUARES:
            x,y=self.square_xy(square)
            dark=(chess.square_file(square)+chess.square_rank(square))%2==0
            color=DARK if dark else LIGHT
            if square in last:
                color='#a4b56b' if dark else '#c7d393'
            if square==self.selected:
                color='#c4d87b'
            if self.board.is_check() and self.board.piece_at(square)==chess.Piece(chess.KING,self.board.turn):
                color='#c87762'
            c.create_rectangle(x,y,x+self.cell,y+self.cell,fill=color,outline='')
            if square in legal:
                if self.board.piece_at(square):
                    c.create_oval(x+3,y+3,x+self.cell-3,y+self.cell-3,outline='#394e39',width=4)
                else:
                    radius=self.cell*.115
                    c.create_oval(x+self.cell/2-radius,y+self.cell/2-radius,x+self.cell/2+radius,y+self.cell/2+radius,fill='#526a4b',outline='')
            piece=self.board.piece_at(square)
            if piece and not (self.drag and self.drag.get('active') and square==self.selected):
                self.draw_piece(square,piece)
        files='hgfedcba' if self.flipped else 'abcdefgh'
        ranks='12345678' if self.flipped else '87654321'
        for i in range(8):
            c.create_text(self.bx+(i+.5)*self.cell,self.by+size+12,text=files[i],fill=MUTED,font=('Segoe UI',9))
            c.create_text(self.bx-13,self.by+(i+.5)*self.cell,text=ranks[i],fill=MUTED,font=('Segoe UI',9))
        if self.drag and self.drag.get('active') and self.selected is not None:
            self.draw_piece(self.selected,self.board.piece_at(self.selected),self.drag['x'],self.drag['y'],tag='drag')

    def draw_piece(self,square,piece,x=None,y=None,tag='piece'):
        if not piece:
            return
        key=('w' if piece.color else 'b')+piece.symbol().lower()
        image_key=(key,self.cell)
        if image_key not in self.images:
            # Preserve every original pixel with nearest-neighbor scaling.
            height=round(self.cell*.92)
            width=round(height*.8)
            self.images[image_key]=ImageTk.PhotoImage(self.base_images[key].resize((width,height),Image.Resampling.NEAREST))
        if x is None:
            sx,sy=self.square_xy(square)
            x,y=sx+self.cell/2,sy+self.cell/2
        self.canvas.create_image(x,y,image=self.images[image_key],tags=tag)

    def can_move(self):
        return self.state and self.state['status']=='playing' and self.state['role']==self.state['turn'] and self.client and self.client.connected

    def press(self,event):
        if not self.can_move():
            self.toast('Đợi lượt của bạn.' if self.state else 'Chọn “Đấu với PixelBot” hoặc vào một phòng để bắt đầu.')
            return
        square=self.event_square(event)
        if square is None:
            return
        piece=self.board.piece_at(square)
        own=piece and piece.color==(self.state['role']==0)
        if self.selected is not None and square!=self.selected and not own:
            self.try_move(square)
            return
        self.selected=square if own else None
        self.drag={'start':(event.x,event.y),'x':event.x,'y':event.y,'active':False} if own else None
        self.draw_board()

    def motion(self,event):
        if not self.drag:
            return
        if math.dist(self.drag['start'],(event.x,event.y))>5:
            self.drag.update(active=True,x=event.x,y=event.y)
            self.draw_board()

    def release(self,event):
        if self.drag and self.drag['active']:
            square=self.event_square(event)
            self.drag=None
            if square is not None and square!=self.selected:
                self.try_move(square)
            else:
                self.draw_board()
        else:
            self.drag=None

    def try_move(self,target):
        if self.selected is None or not self.can_move():
            return
        start=chess.square_name(self.selected)
        end=chess.square_name(target)
        choices=[m for m in self.state['legal'] if m.startswith(start+end)]
        if not choices:
            self.toast('Nước đi không hợp lệ. Chọn một ô có dấu gợi ý.')
            self.draw_board()
            return
        if len(choices)>1:
            win,wrap=self.new_modal('Chọn quân phong cấp',400)
            win.geometry('400x230')
            for symbol,title in [('q','Hậu'),('r','Xe'),('b','Tượng'),('n','Mã')]:
                button(wrap,title,lambda p=symbol:(self.send_move(start,end,p),win.destroy()),small=True).pack(side='left',expand=True,fill='x',padx=3)
        else:
            self.send_move(start,end,choices[0][4:])

    def send_move(self,start,end,promotion=''):
        self.client.send('MOVE',**{'from':start,'to':end,'promotion':promotion})
        self.selected=None
        self.drag=None
        self.draw_board()

    def flip(self):
        self.flipped=not self.flipped
        self.update_players()
        self.draw_board()

    def update_players(self):
        state=self.state
        players=state['players'] if state else []
        top_side,bottom_side=(0,1) if self.flipped else (1,0)
        for card,side in ((self.top_player,top_side),(self.bottom_player,bottom_side)):
            color='Trắng' if side==0 else 'Đen'
            if side<len(players):
                p=players[side]
                you=' · Bạn' if state['role']==side else ''
                card['name'].config(text=('PixelBot' if p['name'].startswith('PixelBot_') else p['name'])+you)
                status='Đã kết nối' if p['connected'] else 'Mất mạng · chờ 60 giây'
                card['detail'].config(text=f'{color} · {p["elo"]} ELO · {status}')
            else:
                card['name'].config(text='Đang chờ đối thủ' if side==1 else self.name or 'Bạn')
                card['detail'].config(text=color+' · '+('Mời bạn bè bằng mã phòng' if state else 'Sẵn sàng cho ván mới'))
            card['avatar'].config(fg=GOLD if side==0 else '#9c9bdb')

    def apply_state(self,state):
        previous=self.state
        new_room=not previous or previous['id']!=state['id']
        board_changed=new_room or previous['fen']!=state['fen']
        self.state=state
        self.board=chess.Board(state['fen'])
        self.clock_base=list(state['clocks'])
        self.clock_at=time.monotonic()
        if new_room:
            self.flipped=state['role']==1
            self.selected=None
            self.chat_messages=[]
            self.chat.config(state='normal')
            self.chat.delete('1.0','end')
            self.chat.config(state='disabled')
        if board_changed:
            self.selected=None
            self.drag=None
        self.room_title.config(text=state['title'][:30])
        self.room_badge.config(text=state['control']+'  •  #'+state['id'])
        phase=state['status']
        if phase=='waiting':
            title='Đang chờ đối thủ'
            detail='Mã phòng: '+state['id']+' · Gửi mã này cho bạn bè.'
        elif phase=='finished':
            title={'1-0':'Trắng thắng','0-1':'Đen thắng','1/2-1/2':'Ván đấu hòa'}.get(state['result'],'Ván đấu kết thúc')
            detail=state['reason']+' · '+state['result']
        else:
            title=('Lượt của bạn' if state['role']==state['turn'] else ('Lượt Trắng' if state['turn']==0 else 'Lượt Đen'))
            if state['check']:
                title+=' · Chiếu!'
            detail='Bạn đang xem trực tiếp.' if state['role']==-1 else 'Server xác nhận mọi nước đi.'
            if state['offer']:
                detail=state['offer']+' đề nghị hòa. Bấm “Hòa” để đồng ý.'
        self.game_status.config(text=title,fg=GOLD if state['check'] or phase=='finished' else TEXT)
        self.game_detail.config(text=detail)
        self.spectators.config(text=str(state['watchers'])+' đang xem')
        self.move_count.config(text=str(len(state['moves'])))
        if new_room or not previous or state['moves']!=previous['moves']:
            self.move_tree.delete(*self.move_tree.get_children())
            for i in range(0,len(state['moves']),2):
                self.move_tree.insert('','end',values=(i//2+1,state['moves'][i]['san'],state['moves'][i+1]['san'] if i+1<len(state['moves']) else ''))
            children=self.move_tree.get_children()
            if children:
                self.move_tree.see(children[-1])
        if state['messages']!=self.chat_messages:
            self.chat_messages=state['messages']
            self.chat.config(state='normal')
            self.chat.delete('1.0','end')
            self.chat.config(state='disabled')
            for msg in state['messages']:
                self.append_chat(msg['name'],msg['text'])
        self.queued=False
        self.match_button.config(text='Ghép trận ngẫu nhiên')
        self.update_players()
        if board_changed or new_room:
            self.draw_board()
        if self.pending_bot and phase=='waiting':
            self.pending_bot=False
            self.bot=PracticeBot(self.host,self.port,state['id'])
        if phase=='finished' and (not previous or previous['status']!='finished'):
            self.toast(title+' · '+state['reason'])

    def append_chat(self,name,text):
        self.chat.config(state='normal')
        if name=='system':
            self.chat.insert('end',text+'\n','system')
        else:
            self.chat.insert('end',name+'  ','name')
            self.chat.insert('end',text+'\n')
        self.chat.see('end')
        self.chat.config(state='disabled')

    def send_chat(self):
        text=self.chat_var.get().strip()
        if text and self.state:
            self.send('CHAT',text=text)
            self.chat_var.set('')

    def emoji(self,emoji):
        if self.state and self.client and self.client.connected:
            if not self.client.send_udp('EMOJI',emoji=emoji):
                self.toast('Chưa gửi được biểu cảm qua UDP.')

    def export_pgn(self):
        if not self.state or not self.state['moves']:
            self.toast('Chưa có nước đi để xuất PGN.')
            return
        board=chess.Board()
        for move in self.state['moves']:
            board.push_uci(move['uci'])
        game=chess.pgn.Game.from_board(board)
        players=self.state['players']
        game.headers.update({'Event':'Pixel Chess','White':players[0]['name'],'Black':players[1]['name'] if len(players)>1 else '?','Result':self.state['result']})
        self.save_pgn(str(game))

    def save_pgn(self,pgn):
        path=filedialog.asksaveasfilename(parent=self.root,title='Lưu ván đấu PGN',defaultextension='.pgn',initialfile='pixel-chess.pgn',filetypes=[('Portable Game Notation','*.pgn')])
        if path:
            Path(path).write_text(pgn+'\n',encoding='utf-8')
            self.toast('Đã lưu ván đấu: '+Path(path).name)

    def history_dialog(self,event):
        self.elo=event['elo']
        self.profile.config(text=f'{self.name} · {self.elo}')
        win,wrap=self.new_modal('Lịch sử ván đấu',650)
        win.geometry('650x500')
        label(wrap,f'{self.name} · {self.elo} ELO  |  30 ván gần nhất',11,GREEN).pack(anchor='w',pady=(0,12))
        tree=ttk.Treeview(wrap,columns=('players','result','reason'),show='headings',height=10)
        for key,title,width in [('players','TRẮNG / ĐEN',220),('result','KẾT QUẢ',80),('reason','KẾT THÚC',230)]:
            tree.heading(key,text=title)
            tree.column(key,width=width)
        tree.pack(fill='both',expand=True)
        for game in event['games']:
            tree.insert('','end',iid=str(game['id']),values=(game['white']+' / '+game['black'],game['result'],game['reason']))
        def export():
            if tree.selection():
                self.send('PGN',id=int(tree.selection()[0]))
        button(wrap,'Tải PGN của ván đã chọn',export,primary=True).pack(fill='x',pady=(14,0))

    def toast(self,text):
        self.status.config(text=text,fg=GOLD)

    def pump(self):
        if self.closing:
            return
        try:
            for _ in range(150):
                event=self.events.get_nowait()
                kind=event['type']
                if kind=='WELCOME':
                    self.name,self.elo=event['name'],event['elo']
                    self.profile.config(text=f'{self.name} · {self.elo}')
                    self.connection.config(text='●  Đã kết nối',fg=GREEN)
                    self.prefs.update(host=self.host,port=self.port,name=self.name,token=event['token'])
                    self.save_prefs()
                    if self.modal and self.modal.winfo_exists():
                        self.modal.destroy()
                    self.toast('Đã kết nối. Tạo phòng, ghép trận hoặc thử đấu với PixelBot.')
                    self.update_players()
                    if self.guest_pending:
                        self.guest_pending=False
                        self.play_bot()
                elif kind=='AUTH_ERROR':
                    if self.modal and self.modal.winfo_exists() and hasattr(self,'auth_note') and self.auth_note.winfo_exists():
                        self.auth_note.config(text=event['message'])
                    self.connection.config(text='●  Chưa kết nối',fg=GOLD)
                    self.toast(event['message'])
                elif kind=='ERROR':
                    self.pending_bot=False
                    self.toast(event['message'])
                elif kind=='RECONNECTING':
                    self.connection.config(text='●  Đang kết nối lại…',fg=GOLD)
                    self.toast(f'Mất mạng · đang khôi phục phiên · còn {event["remaining"]} giây.')
                elif kind=='LOBBY':
                    self.online.config(text=str(event['online'])+' online')
                    old=self.room_list.curselection()
                    rid=self.rooms[old[0]]['id'] if old and self.rooms and old[0]<len(self.rooms) else None
                    self.rooms=event['rooms']
                    self.room_list.delete(0,'end')
                    for i,r in enumerate(self.rooms):
                        status={'waiting':'Chờ','playing':'Đang đấu','finished':'Đã xong'}[r['status']]
                        self.room_list.insert('end',f'{r["control"]}  {r["title"][:17]} · {status}')
                        if r['id']==rid:
                            self.room_list.selection_set(i)
                    if not self.rooms:
                        self.room_list.insert('end','Chưa có phòng công khai')
                elif kind=='STATE':
                    self.apply_state(event)
                elif kind=='CLOCK':
                    if self.state and event['id']==self.state['id'] and event['revision']==self.state['revision']:
                        self.clock_base=list(event['clocks'])
                        self.clock_at=time.monotonic()
                        self.state['turn']=event['turn']
                        self.last_udp=time.monotonic()
                elif kind=='EMOJI':
                    if self.state and event['id']==self.state['id']:
                        self.append_chat(event['name'],event['emoji'])
                        self.toast(event['name']+'  '+event['emoji'])
                elif kind=='PONG':
                    if isinstance(event.get('at'),(int,float)):
                        self.latency=round((time.monotonic()-event['at'])*1000)
                        self.transport.config(text=f'TCP {self.latency} ms  /  UDP {self.client.udp_port}')
                elif kind=='QUEUED':
                    self.queued=True
                    self.match_button.config(text='Hủy tìm đối thủ')
                    self.toast('Đang tìm đối thủ cùng mức thời gian…')
                elif kind=='QUEUE_CANCELLED':
                    self.queued=False
                    self.match_button.config(text='Ghép trận ngẫu nhiên')
                    self.toast('Đã hủy ghép trận.')
                elif kind=='LEFT':
                    self.reset_board()
                elif kind=='HISTORY':
                    self.history_dialog(event)
                elif kind=='PGN':
                    if event['pgn']:
                        self.save_pgn(event['pgn'])
                elif kind=='DISCOVERED':
                    if event['parent'].winfo_exists():
                        servers=event['servers']
                        if servers:
                            event['host_var'].set(f'{servers[0]["host"]}:{servers[0]["port"]}')
                            event['note'].config(text='Tìm thấy: '+', '.join(f'{s["name"]} ({s["host"]}:{s["port"]})' for s in servers))
                        else:
                            event['note'].config(text='Chưa thấy server. Kiểm tra cùng mạng LAN và cổng UDP 9999.')
        except queue.Empty:
            pass
        self.root.after(40,self.pump)

    def animate_clock(self):
        if self.closing:
            return
        clocks=list(self.clock_base)
        if self.state and self.state['status']=='playing' and self.client and self.client.connected:
            side=self.state['turn']
            clocks[side]=max(0,clocks[side]-(time.monotonic()-self.clock_at))
        for card,side in ((self.top_player,0 if self.flipped else 1),(self.bottom_player,1 if self.flipped else 0)):
            sec=max(0,math.ceil(clocks[side]))
            active=self.state and self.state['status']=='playing' and self.state['turn']==side
            card['clock'].config(text=f'{sec//60:02d}:{sec%60:02d}',bg=GREEN if active else PANEL,
                                 fg=INK if active else MUTED)
        self.root.after(100,self.animate_clock)

    def close(self):
        if self.state and self.state['status']=='playing' and self.state['role']>=0:
            if not messagebox.askyesno('Đóng Pixel Chess','Đóng ứng dụng? Phiên được giữ tối đa 60 giây nếu server vẫn chạy.',parent=self.root):
                return
        self.closing=True
        if self.bot:
            self.bot.close()
        if self.client:
            self.client.close()
        self.root.destroy()
        if self.server:
            self.server.stop()


def main():
    root=tk.Tk()
    try:
        root.tk.call('tk','scaling',1.15)
    except tk.TclError:
        pass
    demo='--demo' in sys.argv
    app=ChessApp(root,show_login=not demo)
    if demo:
        root.after(250,app.play_guest)
    root.mainloop()

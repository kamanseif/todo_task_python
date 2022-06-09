import tkinter as tk
import sqlite3
from tkinter import messagebox
class App:
    
    def __init__(self):
        # ウィンドウを初期化
        self.master = tk.Tk()
        self.master.title('タスク管理アプリ')
        self.master.geometry('500x400')
        self.master.configure(padx = 16, pady = 16)

        # TODO入力エリアを作成
        self.input_area = InputArea(self.master)
        self.input_area.pack(side = 'top', fill = 'x')
        self.input_area.add_task = self.add_task
        self.input_area.change_task = self.change_task
        
        # TODOリストの表示エリアを作成
        self.list_area = ListArea(self.master)
        self.list_area.pack(side = 'top', expand = True, fill = 'both')
        self.list_area.edit_task = self.edit_task
        
        #ボタンの表示エリアを作成
        self.button_area = ButtonArea(self.master)
        self.button_area.pack(side = 'bottom',anchor = tk.CENTER)
        self.button_area.click_del_btn = self.click_del_btn
        self.button_area.click_save_btn = self.click_save_btn
        
    def mainloop(self):
        # masterに処理を委譲
        self.master.mainloop()

    #入力エリアの入力値をリストエリアに追加する
    def add_task(self):
        print('add')
     
        todo = self.input_area.entry.get() # 入力値を取得
        self.input_area.entry.delete(0, 'end') # 入力行に残ったテキストを削除
        self.list_area.listbox.insert('end', todo) # リストにtodoを追加

    #選択されたリストの内容を編集エリアに表示
    def edit_task(self):
        print('change')
        self.input_area.edit.delete(0,'end')
        #現在選択されている項目のインデックスを取得
        self.indices = self.list_area.listbox.curselection()
        
        """
        if len(self.indices) != 1:
            #2つ以上選択されているor1つも選択されていない
            return
            """
        #項目を取得
        self.index = self.indices[0]
        self.task = self.list_area.listbox.get(self.index)
        
        #取得した項目をeditに表示
        self.input_area.edit.insert(0,self.task)


    #リストエリアのタスクを編集エリアのタスクに変更
    def change_task(self):
        print('change!!')
        #現在選択されている項目のインデックスを取得
        sel = self.list_area.listbox.curselection()
        #リストを削除
        for i in sel[::-1]:
            self.list_area.listbox.delete(i)

        #編集エリアの文字を取得
        todo_2 = self.input_area.edit.get()
        #編集エリアに残ったテキストを削除
        self.input_area.edit.delete(0,'end')
        #リストにtodo2を追加
        self.list_area.listbox.insert(sel,todo_2)

    #タスクを削除する
    def click_del_btn(self):

        global index_del
        global del_data
        #クリックしたリストのタスクをSQLテーブルから削除する関数
        def delete_db(task_data):
            con = sqlite3.connect('todo.db')
            cur = con.cursor()
            sql = "DELETE FROM todo WHERE event = ?"
            cur.execute(sql,(task_data,))
            con.commit()
            con.close()
        
        print('del')

        #現在選択されている項目のインデックスを取得
        sel = self.list_area.listbox.curselection()
     
        #項目を取得
        index_del = sel[0]
        del_data = self.list_area.listbox.get(index_del)

        delete_db(del_data)

        
        #リストを削除
        for i in sel[::-1]:
            self.list_area.listbox.delete(i)

        self.input_area.edit.delete(0,'end')
        (messagebox.showinfo('メッセージ','タスクを削除しました。'))

    #タスクを保存する     
    def click_save_btn(self):
        def replace_db(task_data):      
            con = sqlite3.connect('todo.db',isolation_level = None,)
            cur = con.cursor()
            sql = "REPLACE INTO todo VALUES (?,?) "
            cur.execute(sql,task_data)
            con.commit()
            con.close()
        global index_save
        global content
        print('save')
        #現在選択されている項目のインデックスを取得
        self.indicies_2 = self.list_area.listbox.curselection()
        #項目を取得
        index_save = self.indices[0]
        content = self.list_area.listbox.get(index_save)

        replace_db([index_save,content])

        messagebox.showinfo('メッセージ','タスクを保存しました。')

      #TODOの入力エリア ユーザーの入力を処理する 
class InputArea(tk.Frame):

    def __init__(self, master):
        super(InputArea, self).__init__(master)

        # ハンドル
        self.add_task = None
        self.change_task = None

        #説明
        self.label_exp = tk.Label(self,text = 'タスク入力')
        self.label_exp.pack(side = 'top',pady = 10)

        # 入力行の作成
        self.entry = tk.Entry(self)
        self.entry.bind('<Return>',self._add_task)
        self.entry.pack(side = 'top', fill = 'x')

        #説明
        self.label_exp2 = tk.Label(self,text = 'タスク編集')
        self.label_exp2.pack(side = 'top')
        
        #編集用の行
        self.edit = tk.Entry(self)
        self.edit.bind('<Return>',self._change_task)
        self.edit.pack(side = "bottom",fill = 'x',pady = 10)

    def _add_task(self,event = None):
        if self.add_task:
            self.add_task()

    def _change_task(self,event = None):
        if self.change_task:
            self.change_task()

      #TODOリストの表示エリア
class ListArea(tk.Frame):

    def __init__(self, master):
        super(ListArea, self).__init__(master)
        
        # ハンドル
        self.edit_task = None  

        # リストの作成
        self.listbox = tk.Listbox(self, height = 5)
        self.listbox.pack(side = 'top',fill = 'both',expand = True)
        
        #項目選択時の処理
        self.listbox.bind("<ButtonRelease-1>",self._edit_task)
        
        def select_db(sql):
            con = sqlite3.connect('todo.db')
            cur = con.cursor()
            cur.execute(sql)
            row = cur.fetchall()
            con.close()
            return row

        #データベースのデータを呼び出す
        row = select_db("SELECT * FROM todo")
        for sel in row:
            self.listbox.insert(sel[0],sel[1])  
        
    def _edit_task(self,event = None):
        if self.edit_task:
            self.edit_task()

     #削除ボタン、保存ボタンを表示するエリア
class ButtonArea(tk.Frame):
    
    def __init__(self,master):
        super(ButtonArea,self).__init__(master)

        #ハンドル
        self.click_del_btn = None
        self.click_save_btn = None

        # 保存ボタンの作成
        self.save_btn = tk.Button(self,text = '保存',command = self._click_save_btn)
        self.save_btn.pack(side = 'left',padx = 30,pady = 30)

        # 削除ボタンの作成
        self.del_btn = tk.Button(self,text = '削除',command = self._click_del_btn)
        self.del_btn.pack(padx = 30,pady = 30)

    def _click_save_btn(self):
        if self.click_save_btn:
            self.click_save_btn()

    def _click_del_btn(self):
        if self.click_del_btn:
            self.click_del_btn()


def main():
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()



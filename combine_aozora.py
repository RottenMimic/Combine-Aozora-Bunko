# -*- coding: utf-8 -*-

#-----------------------------------
#combine_aozora
#
#copyright: RottenMimic
#marvel.bunny@gmail.com
#-----------------------------------

import Tkinter as tk, ttk, codecs
import tkFileDialog
import zipfile, StringIO
import urllib2,re

file_dic={}


#-------------- common --------------
BOMS={
   codecs.BOM_UTF8: 'utf_8', 
   codecs.BOM_UTF16: 'utf_16',
   codecs.BOM_UTF16_BE: 'utf_16_be', 
   codecs.BOM_UTF16_LE: 'utf_16_le', 
   codecs.BOM_UTF32: 'utf_32', 
   codecs.BOM_UTF32_BE: 'utf_32_be', 
   codecs.BOM_UTF32_LE: 'utf_32_le'
}

def encode_tx(tx):
   #return utf8
   for b in BOMS:
      if tx.startswith(b):
         tx=tx[len(b):]
         return tx.decode(BOMS[b])
   try:
      return unicode(tx, 'shift_jis')
   except:
      #no BOM
      try:
         return tx.decode('utf-8')
      except:
         return ''

def extract_zip_data(data):
   z=zipfile.ZipFile(StringIO.StringIO(data))
   dic={}
   for item in z.namelist():
      dic[item]=z.read(item)
   return dic

def analyse_html(url, patterns):
   html=urllib2.urlopen(url).read()
   try:
      html=unicode(html, 'euc_jp')
   except:
      pass
   
   arr=[]
   for p in patterns:
      arr+=[re.findall(p, html)]
   return arr
#-------------- GUI --------------
def load_file_box():
   return tkFileDialog.askopenfilenames()

def save_text_box(tx):
   path=tkFileDialog.asksaveasfilename()
   if path:
      with codecs.open(path, 'wb', encoding='utf-8') as f:
         f.write(tx)
   
def cb_select_all(cb_items):
   for item in cb_items:
      item.state(['selected'])

def cb_deselect_all(cb_items):
   for item in cb_items:
      item.state(['!selected'])
      
def create_scroll_frame(root):
   mother_frame=tk.Frame(root)
   canvas=tk.Canvas(mother_frame)
   canvas.pack(side=tk.LEFT, fill='x')
   scrollbar=tk.Scrollbar(mother_frame, command=canvas.yview)
   scrollbar.pack(side=tk.RIGHT, fill='y')
   canvas.configure(yscrollcommand=scrollbar.set)
   def on_configure(e):
      canvas.configure(scrollregion=canvas.bbox('all'))
   canvas.bind('<Configure>', on_configure)
   frame=tk.Frame(canvas)
   canvas.create_window((0,0), window=frame, anchor='nw')
   mother_frame.pack()
   
   return frame
   
#-------------- core --------------

def extract_zip(data):
   dic=extract_zip_data(data)
   for item in dic:
      if item.lower().endswith('.txt'):
         analyse_text(encode_tx(dic[item]))
      else:
         file_dic[item]=dic[item]
   
def analyse_text(tx):
   arr=tx.splitlines()
   
   if len(arr)<3:
      return
      
   title=arr[0]
   author=arr[1]

   date=''
   c=len(arr)-1
   while c>0:
      if arr[c].startswith((u'初出：', u'底本：')):
         date=arr[c+1].strip()
         break
      c-=1
   
   tree.insert('', 'end', text=title, values=(title, author, date, u'\r\n'.join(x for x in arr[2:])))
   
def load_local_file():
   #file dialog
   tmp=load_file_box()
   if(not(tmp)): return
   file_list=root.tk.splitlist(tmp)
   
   for path in file_list:
      if path.lower().endswith('.zip'):
         with open(path, 'rb') as f:
            extract_zip(f.read())
      elif path.lower().endswith('.txt'):
         with open(path, 'r') as f:
            tx=f.read()
         tx=encode_tx(tx)
         analyse_text(tx)
      else:
         print 'not supported file format: '+path
         continue
      
def export_file():
   total_tx=''
   t=tree.get_children()
   
   for i in t:
      if total_tx: total_tx+=u'\r\n［＃改ページ］\r\n'
      total_tx+=u'%1［＃「%1」は大見出し］\r\n［＃地から１字上げ］%2\r\n\r\n'.replace('%1', tree.item(i)['values'][0],2).replace('%2', tree.item(i)['values'][1])+tree.item(i)['values'][3]
   
   if ens[0].get():
      title=ens[0].get()
   else:
      title='title'
   if ens[1].get():
      author=ens[1].get()
   else:
      author='author'
   
   total_tx=u'\r\n'.join([
      title, 
      author,
      '',
      total_tx
      ])
   #save
   save_text_box(total_tx)

#-------------- GUI --------------

def get_author_id():
   t = tk.Toplevel(root)
   t.wm_title("input author id")

   def call_back(tx):
      t.destroy()
      get_author(tx)
   
   frame=tk.Frame(t)
   frame.pack()
   tk.Label(frame, text="https://www.aozora.gr.jp/index_pages/person").pack(side=tk.LEFT)
   entry=tk.Entry(frame)
   entry.pack(side=tk.LEFT)
   tk.Label(frame, text=".html").pack(side=tk.LEFT)
   
   tk.Button(t, text="OK", command=lambda: call_back(entry.get())).pack()

   
def get_author(id):
   #get data
   author_url='https://www.aozora.gr.jp/index_pages/person'+id+'.html'
   print 'loading: ' + author_url
   try:
      arr=analyse_html(author_url,['<font size="\+2">(.*?)</font>','<li><a href="(.*?)">(.*?)</a>(.*?)</li>'])
      author_name=arr[0][0]
      print 'loaded, analysing...'
   except:
      print 'page not found'
      return
   
   work_list=arr[1]
   
   #create window
   t=tk.Toplevel(root)
   t.wm_title("author")
   
   #top frame
   tk.Label(t, text=author_name, font = "Arial 16 bold").pack()
   top_frame=tk.Frame(t)
   top_frame.pack()
   
   sel_but=tk.Button(top_frame, text="Select All", command=lambda: cb_select_all(c)).pack(side=tk.LEFT)
   desel_but=tk.Button(top_frame, text="Deselect All", command=lambda: cb_deselect_all(c)).pack(side=tk.LEFT)
   
   #center frame
   frame=create_scroll_frame(t)
   
   c=[]
   title_list=[]
   
   for i, item in enumerate(work_list):
      c+=[ttk.Checkbutton(frame, text=item[1]+item[2])]
      if item[1] in title_list:
         c[i].state(['!selected', '!alternate'])
      else:
         c[i].state(['selected', '!alternate'])
         title_list+=[item[1]]
         
      c[i].pack(anchor="w")

   #bottom frame
   def ok():
      #https://www.aozora.gr.jp/cards/000244/card1329.html
      #https://www.aozora.gr.jp/cards/000244/files/1329_ruby_27366.zip
      for index, item in enumerate(c):
         if 'selected' in item.state():
            #../cards/000074/card419.html"
            try:
               url_split=work_list[index][0].split('/')
               arr=analyse_html('https://www.aozora.gr.jp/cards/'+url_split[2]+'/'+url_split[3], ['<a href="./files/(.*?).zip">'])
               zip_url='https://www.aozora.gr.jp/cards/'+url_split[2]+'/files/'+arr[0][0]+'.zip'
               print item['text'] +' '+ zip_url
               zip_file=urllib2.urlopen(zip_url).read()
               extract_zip(zip_file)
            except:
               print "error while loading "+item['text']
      print 'load done.'
      t.destroy()
      
   but_ok=tk.Button(t, text='ok', command=ok).pack()

 
#base
root=tk.Tk()
root.title("Combine Aozora Bunko")

ens=[]
column_headings=("title", "author", "date", "novel")

for c, i in enumerate(["Title", "Author"]):
   tk.Label(root, text=i).grid(row=c, column=0)
   ens+=[tk.Entry(root)]
   ens[c].grid(row=c, column=1, sticky="nsew")

#treeview
tree=ttk.Treeview(root)
tree.grid(row=2, column=0, columnspan=2, sticky="nsew")
vsb=ttk.Scrollbar(root, orient="vertical", command=tree.yview)
vsb.grid(row=2, column=2, sticky="ns")
tree.configure(yscrollcommand=vsb.set)

tree['show']='headings'
tree["columns"]=column_headings
tree['displaycolumns']=(0, 1, 2)

def tree_sort(col, reverse):
   arr=[]
   for k in tree.get_children(''):
      arr+=[(tree.set(k, col), k)]
      
   arr.sort(reverse=reverse)
   
   for index, (val, id) in enumerate(arr):
      tree.move(id, '', index)
   
   tree.heading(col, command=lambda: tree_sort(col, not reverse))
   
for col in column_headings[:3]:
   tree.heading(col, text=col, command=lambda: tree_sort(col, False) )


def tree_delete(e):
   cur_item=tree.selection() #return triple
   if cur_item:
      for i in cur_item:
         tree.delete(i)
         
def tree_up(e):
   items=tree.selection()
   min_len=0
   
   for i in items:
      if tree.index(i)<=min_len:
         min_len+=1
         continue
      else:
         tree.move(i, '', tree.index(i)-1)

def tree_down(e):
   items=reversed(tree.selection())
   max_len=len(tree.get_children())-1
   
   for i in items:
      if tree.index(i)>=max_len:
         max_len-=1
         continue
      else:
         tree.move(i, '', tree.index(i)+1)
         
tree.bind("<Delete>", tree_delete)
tree.bind("<Prior>", tree_up)
tree.bind("<Next>", tree_down)

#buttons
tk.Button(root, text="load file", command=load_local_file).grid(row=3, column=0, sticky="w")
tk.Button(root, text="load by author", command=get_author_id).grid(row=3, column=1, sticky="w")
tk.Button(root, text="export", command=export_file).grid(row=3, column=1, sticky="e")

root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=0)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=0)

root.mainloop()

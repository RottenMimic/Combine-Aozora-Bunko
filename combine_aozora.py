# -*- coding: utf-8 -*-

#-----------------------------------
#Combine Aozora Bunko
#
#copyright: RottenMimic
#email: marvel.bunny@gmail.com
#-----------------------------------

import Tkinter as tk, ttk, ScrolledText
import urllib2, re
import locale, ctypes
import json
import os
import zipfile, StringIO
import codecs
import tkFileDialog

#-----------values setting--------------
DEFAULT_LANG='' #zh_tw, zh_cn, jp

#-----------values global--------------
name_dic={
         'author': 'Author',
         'title': 'Title',
         'date': 'Date',
         'app_name': 'Combine Aozora Bunko',
         'add_file': 'Add File',
         'load_by_author': 'Load By Author',
         'load_from_url': 'Load From URL',
         'export': 'Export',
         "select_all": "Select All",
         "deselect_all": "Deselect All",
         "web_descri": "full zip or text url. Ctrl+V to past."
      }
file_dic={}
column_headings=('title', 'author', 'date', 'novel')
BOMS={
   codecs.BOM_UTF8: 'utf_8', 
   codecs.BOM_UTF16: 'utf_16',
   codecs.BOM_UTF16_BE: 'utf_16_be', 
   codecs.BOM_UTF16_LE: 'utf_16_le', 
   codecs.BOM_UTF32: 'utf_32', 
   codecs.BOM_UTF32_BE: 'utf_32_be', 
   codecs.BOM_UTF32_LE: 'utf_32_le'
}
ens=[] #title, author

#-----------locale-----------
if DEFAULT_LANG:
   code=DEFAULT_LANG.lower()
else:
   windll = ctypes.windll.kernel32
   code=locale.windows_locale[windll.GetUserDefaultUILanguage()].lower()

if os.path.exists(code+'.json'):
   try:
      dic=json.load(open(code+'.json'))
      for item in dic:
         name_dic[item]=dic[item]
   except:
      pass

   
      
#-------------common-----------
def extract_zip_data(data):
   z=zipfile.ZipFile(StringIO.StringIO(data))
   dic={}
   for item in z.namelist():
      dic[item]=z.read(item)
   return dic
   
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
   
#-------------core-----------
def analyse_text(tx):
   tmp=tx.splitlines()
   if len(tmp)<3:return
   
   #remove note
   arr=[]
   note_flag=False
   for i in tmp:
      if i.startswith('-------------'):
         note_flag=not note_flag
         continue
         
      if note_flag==False:
         arr+=[i]
  
   title=arr[0]
   author=arr[1]
   
      
   date=''
   c=len(arr)-1
   while c>0:
      if arr[c].startswith((u'初出：', u'底本：')):
         date=arr[c+1].strip()
         break
      c-=1
   
   tree.insert('', 'end', text=title, values=(title, author, date, u'\r\n'.join(x for x in arr[3:])))
   
def analyse_zip(data):
   dic=extract_zip_data(data)
   for item in dic:
      if item.lower().endswith('.txt'):
         analyse_text(encode_tx(dic[item]))
      else:
         file_dic[item]=dic[item]

def load_local_file():
   file_list=tkFileDialog.askopenfilenames()
   if(not(file_list)): return
   
   for path in file_list:
      if path.lower().endswith('.zip'):
         with open(path, 'rb') as f:
            analyse_zip(f.read())
      elif path.lower().endswith('.txt'):
         with open(path, 'r') as f:
            tx=f.read()
         analyse_text(encode_tx(tx))
      else:
         print 'not supported file format: '+path

def load_from_web():
   t=tk.Toplevel(root)
   t.wm_title("url")
   tk.Label(t, text=name_dic['web_descri']).pack()
   p=ScrolledText.ScrolledText(t)
   p.pack()
   
   #popup
   def call_back():
      arr=p.get(1.0, tk.END).splitlines()
      for url in arr:
         try:
            if url.lower().endswith('.zip'):
               zip_file=urllib2.urlopen(url).read()
               analyse_zip(zip_file)
            elif url.lower().endswith('.txt'):
               tx=urllib2.urlopen(url).read()
               analyse_text(encode_tx(tx))
            else:
               print 'not suport format: '+url
         except:
            print 'error in loading: '+url
      t.destroy()
   tk.Button(t, text="ok", command=call_back).pack()
   

def export_file():
   path=tkFileDialog.asksaveasfilename(defaultextension='.txt', filetypes=(("Plain Text", ".txt"), ("All Files", "*.*")))

   if not(path):
      return
      
   total_tx=''
   t=tree.get_children()
   
   for i in t:
      if total_tx: total_tx+=u'\r\n［＃改ページ］\r\n'
      total_tx+=u'%1［＃「%1」は大見出し］\r\n［＃地から１字上げ］%2\r\n\r\n'.replace('%1', tree.item(i)['values'][0],2).replace('%2', tree.item(i)['values'][1])+tree.item(i)['values'][3]
   
   title=ens[0].get() if ens[0].get() else 'title'
   author=ens[1].get() if ens[1].get() else 'author'

   total_tx=u'\r\n'.join([title, author,'',total_tx])
   
   with codecs.open(path, 'wb', encoding='utf-8') as f:
      f.write(total_tx)

   #file_dic   
   dirname=os.path.dirname(path)
   for item in file_dic:
      with open(os.path.join(dirname, item), 'wb') as f:
         f.write(file_dic[item])

def msg_box():
   t=tk.Toplevel(root)
   t.wm_title("author")
   frame=tk.Frame(t)
   frame.pack()
   tk.Label(frame, text="https://www.aozora.gr.jp/index_pages/person").pack(side=tk.LEFT)
   entry=tk.Entry(frame)
   entry.pack(side=tk.LEFT)
   tk.Label(frame, text=".html").pack(side=tk.LEFT)
   
   def call_back():
      tx=entry.get()
      t.destroy()
      load_author(tx)
      
   
   tk.Button(t, text="OK", command=call_back).pack()

def load_author(id):
   #get data
   author_url='https://www.aozora.gr.jp/index_pages/person'+id+'.html'
   print 'loading: ' + author_url
   try:
      arr=analyse_html(author_url,['<font size="\+2">(.*?)</font>','<li><a href="(.*?)">(.*?)</a>(.*?)</li>'])
      author_name=arr[0][0]
      work_list=arr[1]
      print 'loaded, analysing...'
   except:
      print 'author not found'
      return
   
   #values
   cbs=[] #checkbox
   title_list=[]
   
   t=tk.Toplevel(root)
   t.wm_title("author")
   
   tk.Label(t, text=author_name, font = "Arial 16 bold").pack()
   def select_all():
      for item in cbs:
         item.state(['selected'])
   def deselect_all():
      for item in cbs:
         item.state(['!selected'])
   top_frame=tk.Frame(t)
   top_frame.pack()
   tk.Button(top_frame, text=name_dic['select_all'], command=select_all).pack(side=tk.LEFT)
   tk.Button(top_frame, text=name_dic['deselect_all'], command=deselect_all).pack(side=tk.LEFT)
   
   #center frame
   frame=create_scroll_frame(t)
   for i, item in enumerate(work_list):
      cbs+=[ttk.Checkbutton(frame, text=item[1]+item[2])]
      if item[1] in title_list:
         cbs[i].state(['!selected', '!alternate'])
      else:
         cbs[i].state(['selected', '!alternate'])
         title_list+=[item[1]]
         
      cbs[i].pack(anchor="w")

   #bottom frame
   def ok():
      for index, item in enumerate(cbs):
         if 'selected' in item.state():
            try:
               url_split=work_list[index][0].split('/')
               arr=analyse_html('https://www.aozora.gr.jp/cards/'+url_split[2]+'/'+url_split[3], ['<a href="./files/(.*?).zip">'])
               zip_url='https://www.aozora.gr.jp/cards/'+url_split[2]+'/files/'+arr[0][0]+'.zip'
               try:
                  print item['text'] +' '+ zip_url
               except:
                  print zip_url
               zip_file=urllib2.urlopen(zip_url).read()
               analyse_zip(zip_file)
            except:
               try:
                  print "error while loading "+item['text']
               except:
                  print 'error happened'
      print 'load done.'
      t.destroy()
      
   but_ok=tk.Button(t, text='ok', command=ok).pack()
   
#-------------gui-----------
def create_scroll_frame(root):
   mother_frame=tk.Frame(root)
   canvas=tk.Canvas(mother_frame)
   canvas.pack(side=tk.LEFT, fill='both', expand=True)
   add_scrollbar(root, mother_frame, canvas, True)
  
   frame=tk.Frame(canvas)
   canvas.create_window((0,0), window=frame, anchor='nw')
   mother_frame.pack(expand=True, fill='both')
   
   return frame
   
def add_scrollbar(root, container, target, bol_canvas=False):
   vsb=tk.Scrollbar(container, orient="vertical", command=target.yview)
   vsb.pack(side=tk.RIGHT, fill='y')
   
   def on_configure(e):
      target.configure(scrollregion=target.bbox('all'))
   def on_mousewheel(e):
      if abs(e.delta)>=120:
         target.yview_scroll(-1*(e.delta/120), "units")
      else:
         target.yview_scroll(-1*e.delta, "units")
         
   target.configure(yscrollcommand=vsb.set)
   if bol_canvas:
      target.bind('<Configure>', on_configure)
   root.bind('<MouseWheel>', on_mousewheel)

def tree_delete(e):
   cur_item=tree.selection() #return triple
   if not(cur_item): return
   for i in cur_item:
      tree.delete(i)

def tree_up(e):
   cur_item=tree.selection()
   if not(cur_item): return
   min_len=0
   for i in cur_item:
      if tree.index(i)<=min_len:
         min_len+=1
         continue
      else:
         tree.move(i, '', tree.index(i)-1)

def tree_down(e):
   cur_item=reversed(tree.selection())
   if not(cur_item): return
   max_len=len(tree.get_children())-1
   for i in cur_item:
      if tree.index(i)>=max_len:
         max_len-=1
         continue
      else:
         tree.move(i, '', tree.index(i)+1)

def tree_sort(col, reverse):
   arr=[]
   for k in tree.get_children(''):
      arr+=[(tree.set(k, col), k)]
   arr.sort(reverse=reverse)
   for index, (val, id) in enumerate(arr):
      tree.move(id, '', index)
   tree.heading(col, command=lambda: tree_sort(col, not reverse))

#-------------main-----------
root=tk.Tk()
root.title(name_dic['app_name'])

#title author

for index, text in enumerate([name_dic['title'], name_dic['author']]):
   frame=tk.Frame(root)
   tk.Label(frame, text=text, width=10).pack(side=tk.LEFT)
   ens+=[tk.Entry(frame)]
   ens[index].pack(expand=False, fill='x')
   frame.pack(expand=False, fill='x')

#tree
frame=tk.Frame(root)
frame.pack(expand=True, fill='both')
tree=ttk.Treeview(frame)
tree.pack(side=tk.LEFT, fill='both', expand=True)
add_scrollbar(root, frame, tree)
tree.bind("<Delete>", tree_delete)
tree.bind("<Prior>", tree_up)
tree.bind("<Next>", tree_down)
tree['show']='headings'
tree["columns"]=column_headings
tree['displaycolumns']=(0,1,2)

tree.heading('title', text=name_dic['title'], command=lambda: tree_sort('title', False))
tree.heading('author', text=name_dic['author'], command=lambda: tree_sort('author', False))
tree.heading('date', text=name_dic['date'], command=lambda: tree_sort('date', False))

tk.Button(root, text=name_dic['add_file'], command=load_local_file).pack(side=tk.LEFT)
tk.Button(root, text=name_dic['load_by_author'], command=msg_box).pack(side=tk.LEFT)
tk.Button(root, text=name_dic['load_from_url'], command=load_from_web).pack(side=tk.LEFT)
tk.Button(root, text=name_dic['export'], command=export_file).pack(side=tk.RIGHT)

root.mainloop()

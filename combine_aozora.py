# -*- coding: utf-8 -*-

#-----------------------------------
#combine_aozora
#
#copyright: RottenMimic
#marvel.bunny@gmail.com
#-----------------------------------

import Tkinter as tk, tkFileDialog, ttk, zipfile, io, codecs

#base
root=tk.Tk()
root.title("Combine Aozora Bunko")

lbs=[]
ens=[]
file_dic={}
column_headings=("title", "author", "date")

#label
for c, i in enumerate(["Title", "Author"]):
   lbs+=[tk.Label(root, text=i)]
   lbs[c].grid(row=c, column=0, sticky="nsew")

#input box
for i in range(2):
   ens+=[tk.Entry(root)]
   ens[i].grid(row=i, column=1, sticky="nsew")


#treeview
def tree_sort(col, reverse):
   arr=[]
   for k in tree.get_children(''):
      arr+=[(tree.set(k, col), k)]
      
   arr.sort(reverse=reverse)
   
   for index, (val, id) in enumerate(arr):
      tree.move(id, '', index)
      
   tree.heading(col, command=lambda: tree_sort(col, not reverse))

tree=ttk.Treeview(root)
tree.grid(row=2, column=0, columnspan=2, sticky="nsew")
tree['show']='headings'
tree["columns"]=column_headings
for i in column_headings:
   tree.heading(i, text=i, command=lambda: tree_sort(i, False) )


#load file

def encode_tx(tx):
   #input: only unicode and shift-jis
   #return unicode
   BOMS={
      codecs.BOM_UTF8: 'utf_8', 
      codecs.BOM_UTF16: 'utf_16',
      codecs.BOM_UTF16_BE: 'utf_16_be', 
      codecs.BOM_UTF16_LE: 'utf_16_le', 
      codecs.BOM_UTF32: 'utf_32', 
      codecs.BOM_UTF32_BE: 'utf_32_be', 
      codecs.BOM_UTF32_LE: 'utf_32_le'
   }
   
   #decode
   for b in BOMS:
      if tx.startswith(b):
         print 'in'
         tx=tx[len(b):]
         return tx.decode(BOMS[b])
   
   try:
      return unicode(tx, 'shift_jis')
   except:
      #no BOM
      try:
         return tx.decode('utf-8')
      except:
         return False

def load_file():
   #format title/author title/subtitle/author title/subtitle(...)/author/publisher 
   #file list
   tmp=tkFileDialog.askopenfilenames()
   if(not(tmp)): return
   file_list=root.tk.splitlist(tmp)
   
   #load file: zip or txt
   #txt: encode
   for path in file_list:
      if path.lower().endswith('.zip'):
         myzip=zipfile.ZipFile(path, 'r')
         #only one txt file
         for t in myzip.namelist():
            if t.lower().endswith('.txt'):
               tx=myzip.read(t)
               tx=encode_tx(tx)
               break
         myzip.close()
      elif path.lower().endswith('.txt'):
         with open(path, 'r') as f:
            tx=f.read()
            f.close()
         tx=encode_tx(tx)
      else:
         print "not supoort format: " + path
         continue
      
      try:
         #analyse
         arr=tx.splitlines()
      except:
         print "error happened:" + path
         continue
      
      title=arr[0]
      author=arr[1]
      arr=arr[2:]

      date=''
      c=len(arr)-1
      while c>0:
         if arr[c].startswith((u'初出：', u'底本：')):
            date=arr[c+1].strip()
            break
         c-=1
      
      #add to treeview
      tree.insert('', 'end', text=path, values=(title, author, date), tags=u'\r\n'.join(x for x in arr))
      
      
def export_file():
   total_tx=''
   t=tree.get_children()
   
   for i in t:
      if len(total_tx)>0:
         total_tx+=u'\r\n\r\n［＃改ページ］\r\n'
      total_tx+=''.join([
         tree.item(i)['values'][0],
         u'［＃「', 
         tree.item(i)['values'][0],
         u'」は大見出し］\r\n［＃地から１字上げ］',
         tree.item(i)['values'][1],
         u'\r\n\r\n',
         u'\r\n'.join(x for x in tree.item(i)['tags'])
         ])
   
   total_tx=u'\r\n'.join([
      ens[0].get(),
      ens[1].get(),
      '',
      total_tx
      ])
   #save
   path=tkFileDialog.asksaveasfilename()
   if path:
      with codecs.open(path, 'wb', encoding='utf-8') as f:
         f.write(total_tx)
      
def tree_delete(event):
   cur_item=tree.selection() #return triple
   if cur_item:
      for i in cur_item:
         tree.delete(i)

def tree_up(event):
   items=tree.selection()
   min_len=0
   
   for i in items:
      if tree.index(i)<=min_len:
         min_len+=1
         continue
      else:
         tree.move(i, '', tree.index(i)-1)

def tree_down(event):
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
   
but_load=tk.Button(root, text="load file", command=load_file)
but_load.grid(row=3, column=0, stick="w")

but_export=tk.Button(root, text="export", command=export_file)
but_export.grid(row=3, column=1, stick="e")

root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=0)

root.mainloop()

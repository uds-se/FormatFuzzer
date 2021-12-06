import os
import copy

indentChar=' ' #globally set to space or tab
#preprocessor
class comment:
   def __init__(self,text,line=False):
      self.text=text
      if line==True:
         self.lineComment=True
      else:
         self.lineComment=False
   def __str__(self):
      if self.lineComment == True:
         return '//%s'%self.text
      else:
         return '/*%s*/'%self.text

def linecomment(text):
   return comment(text,True)

class include:
   def __init__(self,filename,sys=False):
      self.filename=filename
      self.sys=True if sys==True else False
   def __str__(self):
      if self.sys == True:
         return '#include <%s>'%self.filename
      else:
         return '#include "%s"'%self.filename

class define:
   def __init__(self,left,right=None, align=None):
      self.left=left
      self.right=right
      self.align=align
   def __str__(self):
      if self.right is not None:
         if self.align is None:
            return "#define %s %s"%(self.left,self.right)
         else:
            assert(isinstance(self.align, int))
            fmt = "#define {0:<%s} {1}"%(str(self.align))
            return fmt.format(self.left,self.right)            
      else:
         return "#define %s"%(self.left)

class ifndef:
   def __init__(self,text):
      self.text=text
   def __str__(self):
      return "#ifndef %s"%(self.text)

class endif:
   def __str__(self):
      return "#endif"


#helper function
def sysinclude(filename):
   return include(filename,sys=True)

#C Language

class statement:
   def __init__(self,val,indent=None):
      self.val=val
      self.indent=indent
   def __str__(self):
      if not self.indent:
         return str(self.val)+';'
      else:
         return indentChar*self.indent+str(self.val)+';'

class line:
   def __init__(self,val,indent=None):
      self.val=val
      self.indent=indent
   def __str__(self):
      if not self.indent:
         return str(self.val)
      else:
         return indentChar*self.indent+str(self.val)

class blank:
   def __init__(self,lines=1):
      self.numLines=lines
   def __str__(self):
      return '\n'*self.numLines   
   def lines(self):
      return ['' for x in range(self.numLines)]

class sequence:
   def __init__(self):
      self.elements=[]      
   
   def __str__(self):
      result = []
      for elem in self.elements:
         if elem is None:
            result.append('')
         elif isinstance(elem,str):
            result.append(elem)
         else:
            result.append(str(elem))
         if not isinstance(elem,blank):            
            result.append('\n')
      return ''.join(result)
   
   def __len__(self):
      return len(self.elements)
   
   def append(self,elem):
      self.elements.append(elem)
      return self
   
   def extend(self,seq):
      if isinstance(seq, sequence):
         self.elements.extend(seq.elements)
      else:
         self.elements.extend(seq)
      return self
   
   def lines(self):
      lines=[]
      for elem in self.elements:
         if hasattr(elem, 'lines') and callable(elem.lines):
            lines.extend(elem.lines())
         else:
            lines.extend(str(elem).split('\n'))
      return lines

class block:
   def __init__(self, indent=None, innerIndent=0, head=None, tail=None):
      self.code=sequence()
      self.indent=indent
      self.innerIndent=innerIndent
      self.head=head
      self.tail=tail

   def append(self,elem):
      self.code.append(elem)

   def extend(self,sequence):
      self.code.extend(sequence)

   def __str__(self):
      head=str(self.head)+' ' if self.head is not None else ''
      tail=' '+str(self.tail) if self.tail is not None else ''
      if (self.indent is not None) and (self.indent > 0):
         indentStr = indentChar*self.indent
         text=indentStr+'%s{\n' % head
         lines=[]
         for item in self.code.elements:
            if hasattr(item, 'indent') and item.indent is None:
               item.indent = self.indent+self.innerIndent
            lines.append(str(item))
         text+='\n'.join(lines)+'\n'
         text+=indentStr+'} %s' % tail
      else:         
         text='%s{\n' % head
         lines=[]
         for item in self.code.elements:
            if hasattr(item, 'indent') and item.indent is None:
               item.indent = self.innerIndent
            lines.append(str(item))
         text+='\n'.join(lines)+'\n'
         text+='}%s' % tail
      return text
   
   def lines(self):
      lines=[]
      head=str(self.head)+' ' if self.head is not None else ''
      tail=' '+str(self.tail) if self.tail is not None else ''         
      lines.append('%s{'%(head))
      for item in self.code.elements:
         indent=0
         if (self.indent is not None) and (self.indent > 0):
            indent=self.indent
         if hasattr(item, 'indent') and item.indent is None:               
            item.indent = indent+self.innerIndent
            lines.append(str(item))
         else:
            lines.append(str(item))
      lines.append('}%s'%(tail))
      return lines
   

class variable:

   def __init__(self, name, typename='int', static=0, const=0, pointer=0, alias=0, extern=0, array=None):
      self.name=name
      self.typename=typename      
      self.array=array
      if isinstance(pointer,int):
         self.pointer=pointer
      elif isinstance(pointer,bool):
         self.pointer=1 if pointer==True else 0
      else:
         raise ValueError(pointer)
      if isinstance(alias,int):
         self.alias=alias
      elif isinstance(alias,bool):
         self.alias=1 if alias==True else 0
      else:
         raise ValueError(alias)
      if isinstance(const,int):
         self.const=const
      elif isinstance(const,bool):
         self.const=1 if const==True else 0
      else:
         raise ValueError(const)
      if isinstance(static,int):
         self.static=static
      elif isinstance(static,bool):
         self.static=1 if static==True else 0
      else:
         raise ValueError(static)
      if isinstance(extern,int):
         self.extern=extern
      elif isinstance(extern,bool):
         self.extern=1 if extern==True else 0
      else:
         raise ValueError(static)
   def __str__(self):
      result=[]
      #static
      if self.static>0:
         result.append('static')
      #exteren
      if self.extern>0:
         result.append('extern')
      #const
      if self.const & 1: #first bit of self.const activates first (lefmost) const declaration
         result.append('const')
      result.append(self.typename)
      if self.const & 2: #second bit of self.const activates second const declaration
         result.append(self.pointer*'*')
         result.append('const')
         result.append(self.name)         
      else: #special case: if second const is not declared, merge '*' and variable name together
         if self.alias>0:
            result.append(self.alias*'&'+self.name)
         else:
            result.append(self.pointer*'*'+self.name)
      #array
      text=' '.join(result)
      if self.array is not None:
         text+='[%s]'%str(self.array)
      return text


class function:
   """
   Creates a function
   """
   def __init__(self, name, typename='int', static=0, const=0, pointer=0, classname="", params=None):
      self.name=name
      self.typename=typename
      self.classname=classname
      self.params=[] if params is None else list(params)
      if isinstance(pointer,int):
         self.pointer=pointer
      elif isinstance(pointer,bool):
         self.pointer=1 if pointer==True else 0
      else:
         raise ValueError('invalid pointer argument')    
      if isinstance(const,int):
         self.const=const
      elif isinstance(const,bool):
         self.const=1 if const==True else 0
      else:
         raise ValueError('invalid const argument')
      if isinstance(static,int):
         self.static=static
      elif isinstance(const,bool):
         self.static=1 if static==True else 0
      else:
         raise ValueError('invalid static argument')
   def add_param(self, param):
      if not isinstance(param,(variable, fptr)):
         raise ValueError('expected variable or fptr object')
      self.params.append(param)
      return self
   def __str__(self):
      static1='static ' if self.static else ''
      const1='const ' if self.const & 1 else ''
      pointer1='*'*self.pointer+' ' if self.pointer>0 else ''
      classname='%s::'%self.classname if len(self.classname)>0 else ""
      if len (self.params)>0:
         s='%s%s%s %s%s%s(%s)'%(static1, const1,self.typename,pointer1,classname,self.name,', '.join([str(x) for x in self.params]))
      else:
         s='%s%s%s %s%s%s(%s)'%(static1, const1,self.typename,pointer1,classname,self.name,'void')
      return s
   def set_class(self, classname):
      self.classname=classname

class fptr(function):
   def __init__(self, name, typename='int', static=0, const=0, pointer=0, classname="", params=None):
      super().__init__(name, typename, static, const, pointer, classname, params)
   
   @classmethod
   def from_func(cls, other, name=None):
      if name is None:
         name = other.name
      func = cls(name, other.typename, other.static, other.const, other.pointer)
      for param in other.params:
         func.add_param(copy.deepcopy(param))
      return func
         
   def __str__(self):
      const1='const ' if self.const & 1 else ''
      pointer1='*'*self.pointer+' ' if self.pointer>0 else ''
      
      if len (self.params)>0:
         s='%s%s (%s%s)(%s)'%(const1,self.typename,pointer1,self.name,', '.join([str(x) for x in self.param]))
      else:
         s='%s%s (%s%s*)(%s)'%(const1,self.typename,pointer1,self.name,'void')
      return s
   

class fcall(object):
   """
   Creates a function call
   """
   def __init__(self,name, args=None):
      self.name=name
      self.args=[] if args is None else list(args)
   def add_arg(self, arg):
      if not isinstance(arg,str):
         raise ValueError('expected string object')
      self.args.append(arg)
      return self
   def __str__(self):
      s='%s(%s)'%(self.name,', '.join([str(x) for x in self.args]))
      return s

class _file(object):
   def __init__(self,path):
      self.path=path
      self.code=sequence()
   
class cfile(_file):
   def __init__(self,path):
      super().__init__(path)
   def __str__(self):
      text=''
      for elem in self.code.elements:
         text+=str(elem)
         if isinstance(elem,blank):            
            newLine=False
         else:
            newLine=True
         if newLine == True:
            text+='\n'      
      return text
   
   def lines(self):
      return self.code.lines()
      
            
class hfile(_file):
   def __init__(self,path,guard=None):
      super().__init__(path)
      if guard is None:
         basename=os.path.basename(path)
         self.guard=os.path.splitext(basename)[0].upper()+'_H'
      else:
         self.guard=guard
   def __str__(self):
      text=str(ifndef(self.guard))+'\n'
      text+=str(define(self.guard))+'\n'
      for elem in self.code.elements:
         text+=str(elem)
         if isinstance(elem,blank):            
            newLine=False
         else:
            newLine=True
         if newLine == True:
            text+='\n'      
      text+="\n%s %s\n"%(str(endif()),str(linecomment(self.guard)))
      return text
   
   def lines(self):
      lines=[]
      lines.append(str(ifndef(self.guard)))
      lines.append(str(define(self.guard)))
      lines.append('')
      lines.extend(self.code.lines())
      lines.append("\n%s %s\n"%(str(endif()),str(linecomment(self.guard))))
      return lines

class initializer:
   def __init__(self,typeref,expression):
      self.typeref=typeref
      self.expression=expression
   def __str__(self):
      if isinstance(self.expression,list):
         return '{'+', '.join([str(x) for x in self.expression]) +'}'
      else:
         return str(self.expression)

class typedef:
   def __init__(self, basetype, name):
      self.basetype=basetype
      self.name=str(name)
   
   def __str__(self):
      return 'typedef %s %s'%(str(self.basetype),self.name)
   
class struct:
   def __init__(self, name=None, block=None, typedef=None):
      self.block=block if block is not None else block()
      self.name=name
      self.typedef=typedef         
   
   def lines(self, indent=0):
      lines=[]
      if self.typedef is not None:
         self.block.tail=self.typedef
         typedefStr='typedef '
      else:
         typedefStr=''
      indentStr=indentChar*indent if indent>0 else ''
      if self.name is None:
         lines.append(indentStr+'%sstruct'%(typedefStr))
      else:
         lines.append('%s%sstruct %s'%(indentStr, typedefStr, self.name))
      lines.extend(self.block.lines())
      return lines
   
   def __str__(self):
      return '\n'.join(self.lines())

if __name__ == '__main__':
   test = cfile('test.c')
   

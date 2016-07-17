# -*- encoding: utf-8 -*-
import json
import web
web.config.debug = True  

_DEBUG_ = False

if _DEBUG_ == False:
    import sae.kvdb
    kv = sae.kvdb.Client()

def datecheck(data,vch):
    if vch[0] == '=':
        if data == vch[1]:
            return True
        else:
            return False
    elif vch[0] == '>':
        if data > vch[1]:
            return True
        else:
            return False
    elif vch[0] == '>=':
        if data >= vch[1]:
            return True
        else:
            return False
    elif vch[0] == '<':
        if data < vch[1]:
            return True
        else:
            return False
    elif vch[0] == '<=':
        if data <= vch[1]:
            return True
        else:
            return False
    elif vch[0] == 'LIKE':
        sch = vch[1].split('%')
        isub = 0
        ifind = 0
        strlen = len(data)
        index = 0
        for sub in sch:
            if isub == 0 and vch[0][0] != '%':
                isub = len(sub)
                if isub < len(data):
                    if data[:isub] != sub:
                        # print("False")
                        return False
                    else:
                        continue
                else:
                    return False
            ifind = data.find(sub,isub)
            if ifind != -1:
                isub = ifind
            else:
                return False
        return True
def select(filename,where):

    if _DEBUG_:
        try:
            fjs=open(filename,'r')
        except OSError:
            return []
        djs=fjs.read()
        fjs.close()
    else:
        djs = kv.get(filename)
        if djs == None:
            return []
    js = json.loads(djs,"utf-8")
    wpairs = where.items()
    result = []
    for d in js:
        # try:
            for k,v in wpairs:
                if not datecheck(d[k],v):
                    #if d[k] != v:
                    break
            else:
                result.append(d)
        # except:
            # return []
    return result
    
def update(filename,data,where):
    dbchgcounter = kv.get("kvdbchg")
    if dbchgcounter == None:
        dbchgcounter = 1
    else:
        dbchgcounter += 1
    kv.set("kvdbchg",dbchgcounter)
    counter = 0
    if _DEBUG_:
        try:
            fjs=open(filename,'r')
            djs=fjs.read()
            fjs.close()
        except OSError:
            fjs=open(filename,'w')
            djs = []
            djs.append(data)
            dstr=json.dumps(djs)
            fjs.write(dstr)
            fjs.close()
            return 1
    else:
        djs = kv.get(filename)
        if djs == None:
            djs = []
            djs.append(data)
            dstr=json.dumps(djs)
            kv.set(filename,dstr)
            return 1
    if where == None:
        js = json.loads(djs,"utf-8")
        for d in js:
            try:
                dpairs = data.items()
                for k,v in dpairs:
                    d[k] = v
                counter = counter+1
            except OSError:
                return 0
    else:
        js = json.loads(djs,"utf-8")
        wpairs = where.items()
        for d in js:
            try:
                for k,v in wpairs:
                    if not datecheck(d[k],v):
                    # if d[k] != v:
                        break
                else:
                    dpairs = data.items()
                    for k,v in dpairs:
                        d[k] = v
                    counter = counter+1
            except OSError:
                return 0
    # else:
        # js.append(data)
    dstr=json.dumps(js)
    if _DEBUG_:
        fjs=open(filename,'w')
        fjs.write(dstr)
        fjs.close()
    else:
        kv.set(filename,dstr)
    return counter
def insert(filename,data,unique=None):
    dbchgcounter = kv.get("kvdbchg")
    if dbchgcounter == None:
        dbchgcounter = 1
    else:
        dbchgcounter += 1
    kv.set("kvdbchg",dbchgcounter)
    counter = 0
    if _DEBUG_:
        try:
            fjs=open(filename,'r')
            djs=fjs.read()
            fjs.close()
        except OSError:
            fjs=open(filename,'w')
            djs = []
            djs.append(data)
            dstr=json.dumps(djs)
            fjs.write(dstr)
            fjs.close()
            return 1
    else:
        djs = kv.get(filename)
        if djs == None:
            djs = []
            djs.append(data)
            dstr=json.dumps(djs)
            kv.set(filename,dstr)
            return 1
    js = json.loads(djs,"utf-8")
    if unique:
        jslen = len(js)
        index = 0
        dataunique = data[unique]
        while index < jslen:
            d = js[index]
            if d[unique] == dataunique:
                # print ("item delet")
                js.remove(d)
                index -= 1
                jslen -= 1
                counter += 1
            index += 1
            
    js.append(data)
    dstr=json.dumps(js)
    if _DEBUG_:
        fjs=open(filename,'w')
        fjs.write(dstr)
        fjs.close()
    else:
        kv.set(filename,dstr)
    if counter == 0:
        counter = 1
    return counter
def delete(filename,where=None):
    dbchgcounter = kv.get("kvdbchg")
    if dbchgcounter == None:
        dbchgcounter = 1
    else:
        dbchgcounter += 1
    kv.set("kvdbchg",dbchgcounter)
    counter = 0;
    
    if _DEBUG_:
        try:
            fjs=open(filename,'r')
            djs=fjs.read()
            fjs.close()
        except OSError:
            return 0
    else:
        djs = kv.get(filename)
        if djs == None:
            return 0
    js = json.loads(djs,"utf-8")
    if where == None:
        counter = len(js)
        if _DEBUG_:
            fjs=open(filename,'w')
            fjs.write("[]")
            fjs.close()
        else:
            kv.set(filename,"[]")
        return counter
    else:
        jslen = len(js)
        index = 0
        dpairs = where.items()
        # print(where)
        while index < jslen:
            d = js[index]
            for k,v in dpairs:
                if not datecheck(d[k],v):
                #if d[k] != v:
                    break
            else:
                js.pop(index)
                index -= 1
                jslen -= 1
                counter += 1
            index += 1
    dstr=json.dumps(js)
    
    if _DEBUG_:
        fjs=open(filename,'w')
        fjs.write(dstr)
        fjs.close()
    else:
        kv.set(filename,dstr)
    return counter
    
    
if __name__ == "__main__":
    instr = input()
    if len(instr) == 0:
        d = get("znn")
        print(d)
    spinstr = instr.split(';')
    d = {}
    d2= {}
    # for sstr in spinstr:
        # index = sstr.find('=')
        # d[sstr[:index]]=sstr[index+1:]
    d["sc"]=['=','5']
    # d2["sd"]="9"
    result = select("test.json",d)
    print(result)

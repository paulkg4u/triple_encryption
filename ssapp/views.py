from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import QueryDict
import ast

from Crypto.Cipher import AES   
import base64
import Crypto
import os
from ssapp.models import TableData,GroupData,GroupAdminInfo,TableOwnerInfo
from django.contrib.auth.models import User
import json


def about_us(request):
   return render(request,'app/about-us.html')

def how_it_works(request):
   return render(request,'app/how-it-works.html')

@login_required
def index(request):
    context_di={}
    userName=request.user.username
    userObject=User.objects.get(username=userName)
    sheetList=TableData.objects.filter(table_owner=userObject)
    context_di['sheetList']=sheetList
    groupList=GroupData.objects.all().filter(group_members=userObject)
    context_di['groupList']=groupList

    return render(request,'app/index.html',context_di)

@login_required
def new_sheet(request):
    return render(request,'app/new_table.html')

@login_required
def new_group(request):
    return render(request,'app/new_group.html')


def  create_new_group(request):
    if request.POST:
        group_name=request.POST['group-name']
        group_desc = request.POST['group-desc']
        groupObject=GroupData(group_name=group_name,group_desc=group_desc)
        groupObject.save()

        group_admin=User.objects.get(username=request.user.username)
        groupObject.group_members.add(group_admin)
        groupAdminInfo=GroupAdminInfo(group_name=groupObject,group_admin=group_admin)
        groupAdminInfo.save()

        return HttpResponseRedirect('/app/')
@login_required
def new_sheet_group(request,group_id):
    context_di={}
    groupPointer=GroupData.objects.get(id=group_id)
    context_di['groupID']=group_id
    context_di['groupName']=groupPointer.group_name
    return render(request,'app/new_sheet_group.html',context_di)

@login_required
def save_new_group_table(request):
    if request.POST:
        
        
        sheet_data=request.POST
        dataDictionary={}
        for each in request.POST:
            private_key=str(request.POST[each])[:8]
            private_key=private_key+((8-len(private_key))*"\0")
            public_key="CrIpTaTo_PuBlIC"[:-1]
            private_key=rearr(private_key)
            MASTER_KEY=mix(private_key,public_key)

            if(request.POST[each]!=""):
                try:

                    encrypted_item=encrypt_val(request.POST[each],MASTER_KEY)


                    mixed_item=mod_mix(encrypted_item,MASTER_KEY,ord(list(encrypted_item)[2])%5)
                    dataDictionary[each]=mixed_item
                except:
                    pass


        tableName=request.POST['sheet-title']
        tableDesc=request.POST['sheet-desc']
        
        tableOwner=User.objects.get(username=request.user.username)
        
        tableData=str(dataDictionary)
        
        tableObject=TableData(table_name=tableName,table_desc=tableDesc,table_owner=tableOwner,table_data=tableData)
        tableObject.save()
        groupID=request.POST['groupID']
        groupObject=GroupData.objects.get(id=groupID)
        tableOwnerInfoObject=TableOwnerInfo(group_name=groupObject,table_name=tableObject,table_owner=tableOwner)
        tableOwnerInfoObject.save()
    return HttpResponseRedirect('/app/')


@login_required
def add_member(request,group_id):
    groupPointer=GroupData.objects.get(id=group_id)
    groupName=groupPointer.group_name
    context_di={}
    context_di['groupName']=groupName
    context_di['groupID']=group_id
    return render(request,'app/add_member_form.html',context_di)


@login_required
def add_new_member(request):
    if request.POST:
        username=request.POST['username']
        group=request.POST['groupID']
        userObject=User.objects.get(username=username)
        groupObject=GroupData.objects.get(id=group)
        groupObject.group_members.add(userObject)



    return HttpResponseRedirect('/app/')


@login_required
def manage_group(request,group_id):
    groupPointer=GroupData.objects.get(id=group_id)
    groupTablePointer=TableOwnerInfo.objects.filter(group_name=groupPointer)
    groupAdminPointer=GroupAdminInfo.objects.get(group_name=groupPointer)
    context_di={}
    context_di['groupID']=group_id
    context_di['groupName']=groupPointer.group_name
    context_di['tables']=groupTablePointer
    context_di['admin']=groupAdminPointer.group_admin
    return render(request,'app/manage-group.html',context_di)


@login_required
def save_new_table(request):
    if request.POST:
        
        
        sheet_data=request.POST
        dataDictionary={}
        for each in request.POST:
  	    
	
            private_key=str(request.POST[each])[:8]
            private_key=private_key+((8-len(private_key))*"\0")
            public_key="CrIpTaTo_PuBlIC"[:-1]
            private_key=rearr(private_key)
            MASTER_KEY=mix(private_key,public_key)
	    
            if(request.POST[each]!=""):
                try:
		    
		    if(each != 'csrfmiddlewaretoken' and each != 'sheet-title' and each != 'sheet-desc'):
			context_elem={}
		        context_elem['title']=each
	   	        context_elem['from_client']=request.POST[each]
	    	        context_elem['key1']=private_key
	                context_elem['key2']=public_key
	    	        context_elem['master_key']=MASTER_KEY
                        encrypted_item=encrypt_val(request.POST[each],MASTER_KEY)
		        context_elem['cipher']=encrypted_item

                        mixed_item=mod_mix(encrypted_item,MASTER_KEY,ord(list(encrypted_item)[2])%5)
		        context_elem['final_cipher']=str(mixed_item)
		        context_elem['mod_val']=ord(list(encrypted_item)[2])%5
                        dataDictionary[each]=mixed_item
		    endif 
                except:
                    pass
		
		


        tableName=request.POST['sheet-title']
        tableDesc=request.POST['sheet-desc']
        
        tableOwner=User.objects.get(username=request.user.username)
        
        tableData=str(dataDictionary)
        
        tableObject=TableData(table_name=tableName,table_desc=tableDesc,table_owner=tableOwner,table_data=tableData)
        tableObject.save()
	
        
        return render(request,'app/details.html',context_elem)


@login_required
def save_edited_table(request,t_id):
    tablePointer=TableData.objects.get(id=t_id)
    if request.POST:
        
        sheet_data=request.POST
        dataDictionary={}
        for each in request.POST:
            private_key=str(request.POST[each])[:8]
            private_key=private_key+((8-len(private_key))*"\0")
            public_key="CrIpTaTo_PuBlIC"[:-1]
            private_key=rearr(private_key)
            
            
            
            if(request.POST[each]!=""):

                try:
                    
                    encrypted_item=encrypt_val(request.POST[each],MASTER_KEY)
                    
                    mixed_item=mod_mix(encrypted_item,MASTER_KEY,ord(list(encrypted_item)[2])%5)
                    
                    dataDictionary[each]=mixed_item

                except:
                    pass


        tableName=request.POST['sheet-title']
        tableDesc=request.POST['sheet-desc']
        
        
        
        tableData=str(dataDictionary)
        tablePointer.table_name=tableName
        tablePointer.table_desc=tableDesc
        tablePointer.table_data=tableData
        
        tablePointer.save()

        
        return HttpResponseRedirect('/app/')

@login_required
def edit_sheet(request,t_id):
    tablePointer=TableData.objects.get(id=t_id)
    context_di={}
    sheetName=tablePointer.table_name
    sheetDesc=tablePointer.table_desc
    encryptedSheetData=tablePointer.table_data
    
    decryptedSheetData={}
    encryptedSheetData=ast.literal_eval(encryptedSheetData)
    for each in encryptedSheetData:
        encryptedItem=encryptedSheetData[each]
        decryptedSheetData[each]=encryptSheetData(encryptedItem)

    
    context_di['sheetName']=sheetName
    context_di['sheetDesc']=sheetDesc
    context_di['tablePointer']=t_id
    
    context_di['data']=decryptedSheetData
    

    
    


    return render(request,'app/edit_table.html',context_di)



@login_required
def delete_table(request,table_id):
    
    tablePointer=TableData.objects.get(id=table_id)
    tablePointer.delete()
    
    return HttpResponseRedirect('/app/index')

@login_required
def delete_group_table(request,table_id):
    tablePointer=TableData.objects.get(id=table_id)
    tablePointer.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




def encryptSheetData(rawText):
    (key,encryptedSheet)=demix(rawText).split("-CRIPTATO-")
    decryptedSheet=decrypt_val(encryptedSheet,key)
    return decryptedSheet


def encrypt_val(clear_text,MASTER_KEY):
    enc_secret = AES.new(MASTER_KEY[:32])
    tag_string = (str(clear_text) +
                  (AES.block_size -
                   len(str(clear_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
   
    return cipher_text
def decrypt_val(cipher_text,MASTER_KEY):
    dec_secret = AES.new(MASTER_KEY[:32])
    raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
    clear_val = raw_decrypted.rstrip("\0")
    return clear_val




def check(key):
    x=len(key)
    
    if x<8:
        y=8-x
        
        str_arr="3$%###%!8"
        list_str=list(str_arr)
        for p in range(0,y):
            key=key+list_str[p]
        

    return key
    
def mix(private,public):
    

    list_private=list(private)
    list_public=list(public)
    key=list_public[4]+list_private[7]+list_private[5]+list_public[7]
    key=key+list_private[6]+list_private[4]+list_public[6]+list_private[0]
    key=key+list_public[0]+list_private[2]+list_public[1]+list_public[5]
    key=key+list_public[2]+list_private[3]+list_private[1]+list_public[3]
    
    return key

def rearr(key):
    list_key=list(key)
    key=list_key[5]+list_key[2]+list_key[0]+list_key[4]+list_key[7]+list_key[1]+list_key[6]+list_key[3]
    return key 

def mod_mix(post,key,mod):
    
    list_post=list(post)
    list_key=list(key)
    data=""
    key_pointer=0
    data_pointer=0
    if mod==0:

        for x in range(0,len(post)+len(key)+1):
            
            

            if(x==2or x==4 or x==5 or x==6 or x==8 or x==10 or x==12 or x==14 or x==15 or x==16 or x==18 or x==20 or x==22 or x==24 or x==26 or x==28):
                data=data+list_key[key_pointer]
                key_pointer=key_pointer+1
            elif(x==3):
                data=data+str(mod)    
                
            else:
                data=data+list_post[data_pointer]
                data_pointer=data_pointer+1
    if mod==1:
                
        for x in range(0,len(post)+len(key)+1):
        
        

            if(x==1or x==5 or x==7 or x==9 or x==11 or x==13 or x==15 or x==17 or x==19 or x==21 or x==23 or x==25 or x==27 or x==29 or x==31 or x==33):
                data=data+list_key[key_pointer]
                key_pointer=key_pointer+1
            elif(x==3):
                data=data+str(mod)    
                
            else:
                data=data+list_post[data_pointer]
                data_pointer=data_pointer+1
    if mod==2:
                
        for x in range(0,len(post)+len(key)+1):
        
        

            if(x==1or x==2 or x==4 or x==5 or x==6 or x==7 or x==8 or x==9 or x==10 or x==11 or x==12 or x==13 or x==14 or x==15 or x==16 or x==17):
                data=data+list_key[key_pointer]
                key_pointer=key_pointer+1
            elif(x==3):
                data=data+str(mod)    
                
            else:
                data=data+list_post[data_pointer]
                data_pointer=data_pointer+1     

    if mod==3:
                
        for x in range(0,len(post)+len(key)+1):
        
        

            if(x==2 or x==5 or x==8 or x==11 or x==14 or x==17 or x==20 or x==23 or x==26 or x==29 or x==32 or x==35 or x==38 or x==41 or x==44 or x==47):
                data=data+list_key[key_pointer]
                key_pointer=key_pointer+1
            elif(x==3):
                data=data+str(mod)    
                
            else:
                data=data+list_post[data_pointer]
                data_pointer=data_pointer+1

    if mod==4:
                
        for x in range(0,len(post)+len(key)+1):
        
        

            if(x==2or x==4 or x==5 or x==6 or x==8 or x==10 or x==12 or x==14 or x==15 or x==16 or x==18 or x==20 or x==22 or x==24 or x==26 or x==28):
                data=data+list_key[key_pointer]
                key_pointer=key_pointer+1
            elif(x==3):
                data=data+str(mod)    
                
            else:
                data=data+list_post[data_pointer]
                data_pointer=data_pointer+1
    
    return data

def demix(value):
    list_value=list(value)
    data=""
    key=""
    
    if list_value[3]=='0':
    
        for x in range(0,len(value)):
            
            

            if(x==2 or x==4 or x==5 or x==6 or x==8 or x==10 or x==12 or x==14 or x==15 or x==16 or x==18 or x==20 or x==22 or x==24 or x==26 or x==28):
                key=key+list_value[x]
                
            elif(x==3):
                pass    
                
            else:
                data=data+list_value[x]

    if list_value[3]=='1':
    
        for x in range(0,len(value)):
            
            

            if(x==1 or x==5 or x==7 or x==9 or x==11 or x==13 or x==15 or x==17 or x==19 or x==21 or x==23 or x==25 or x==27 or x==29 or x==31 or x==33):
                key=key+list_value[x]
                
            elif(x==3):
                pass    
                
            else:
                data=data+list_value[x]

    if list_value[3]=='2':
    
        for x in range(0,len(value)):
            
            

            if(x==1 or x==2 or x==4 or x==5 or x==6 or x==7 or x==8 or x==9 or x==10 or x==11 or x==12 or x==13 or x==14 or x==15 or x==16 or x==17):
                key=key+list_value[x]
                
            elif(x==3):
                pass    
                
            else:
                data=data+list_value[x]

    if list_value[3]=='3':
    
        for x in range(0,len(value)):
            
            

            if(x==2 or x==5 or x==8 or x==11 or x==14 or x==17 or x==20 or x==23 or x==26 or x==29 or x==32 or x==35 or x==38 or x==41 or x==44 or x==47):
                key=key+list_value[x]
                
            elif(x==3):
                pass    
                
            else:
                data=data+list_value[x]

    if list_value[3]=='4':
    
        for x in range(0,len(value)):
            
            

            if(x==2or x==4 or x==5 or x==6 or x==8 or x==10 or x==12 or x==14 or x==15 or x==16 or x==18 or x==20 or x==22 or x==24 or x==26 or x==28):
                key=key+list_value[x]
                
            elif(x==3):
                pass    
                
            else:
                data=data+list_value[x]
            
   
    return key+"-CRIPTATO-"+data
    ##for x in range(0,len(value):


###  encryption and decryption area ###

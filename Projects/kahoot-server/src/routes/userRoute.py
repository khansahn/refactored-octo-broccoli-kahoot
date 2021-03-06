from flask import Flask, request, json, jsonify
import os
from pathlib import Path

from ..utils.crypt import encrypt, decrypt
from ..utils.authorisation import generateToken
from ..utils.file import readFile, createFile, writeFile
from . import router, baseLocation

# ngambil alamat file 
registeredUserFileLocation = baseLocation / "data" / "registered-user-file.json"

print(os.getenv("SECRET_KEY"))

@router.route('/alaala')
def alaala():
    return "HOY"
#####################################################################################################
# REGISTER USER
#####################################################################################################
@router.route('/user', methods=['POST'])
def registerUser():
    body = request.json

    if body["todo"] == "encrypt":
        body["password"] = encrypt(body["password"])
    elif body["todo"] == "decrypt":
        body["password"] = decrypt(body["password"])

    registeredUserData = {
        "registeredUsers" : []
    }

    if os.path.exists(registeredUserFileLocation):
        registeredUserData = readFile(registeredUserFileLocation)

         # cek username nya udah pernah dipake belum
        res = ''
        position = -1
        for i in range(len(registeredUserData["registeredUsers"])) :
            registeredUser = registeredUserData["registeredUsers"][i]
            if (registeredUser["username"] == body["username"]) :
                res = "Username nya udah dipake maz"
                position = i
                break
            if (registeredUser["email"] == body["email"]):
                res = "Km udah pernah daftar pake email ini loh"
                position = i
                break
        if (position == -1):
            registeredUserData["registeredUsers"].append(body) 
            toBeWritten = str(json.dumps(registeredUserData))
            writeFile(registeredUserFileLocation,toBeWritten)
            
            res = jsonify(registeredUserData)
        else : 
            res = res
    else:
        registeredUserData["registeredUsers"].append(body) 
        toBeWritten = str(json.dumps(registeredUserData))
        writeFile(registeredUserFileLocation,toBeWritten)
        res = jsonify(registeredUserData)

    return res

#####################################################################################################
# LOGIN USER
#####################################################################################################
@router.route('/user/login', methods = ['POST'])
def loginUser():
    body = request.json

    # ngebuka file yang udah pernah regist
    registeredUserData = readFile(registeredUserFileLocation)

    # nyari yang di-login udah ada di regist atau belum
    position = -1
    for i in range(len(registeredUserData["registeredUsers"])) :
        registeredUser = registeredUserData["registeredUsers"][i]
        if (registeredUser["username"] == body["username"]) :
            position = i
            if (decrypt(registeredUser["password"]) == body["password"]) :
                body["message"] = "Login berhasssil"
                body["status"] = True
                body["token"] = generateToken(body["username"])
                break
            else:
                body["message"] = "Passwordnya salah ih"
                body["status"] = False
    
    # kalau user yang di login ga ada di registered user
    if (position == -1) :
        body["message"] = "Regist dl ah"
        body["status"] = False
    
    return jsonify(body)

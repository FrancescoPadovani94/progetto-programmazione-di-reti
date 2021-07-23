# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 19:23:18 2021

@author: Francesco Padovani
"""

import tkinter as tk
from tkinter import messagebox
import socket
from time import sleep
import threading
from random import randrange

# FINESTRA DI GIOCO PRINCIPALE
window_main = tk.Tk()
window_main.title("Game Client")
your_name = ""
opponent_name = ""
game_round = 0
game_timer = 30
your_choice = ""
opponent_choice = ""
your_score = 0
opponent_score = 0
mode="scelta"
Q=[]
over=False
# client di rete
client = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8081


top_welcome_frame= tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda : connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line = tk.Label(top_message_frame, text="***********************************************************").pack()
lbl_welcome = tk.Label(top_message_frame, text="")
lbl_welcome.pack()
lbl_line_server = tk.Label(top_message_frame, text="***********************************************************")
lbl_line_server.pack_forget()
top_message_frame.pack(side=tk.TOP)


top_frame = tk.Frame(window_main)
top_left_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_your_name = tk.Label(top_left_frame, text="You: " + your_name, font = "Helvetica 13 bold")
lbl_opponent_name = tk.Label(top_left_frame, text="Opponent: " + opponent_name)
lbl_your_name.grid(row=0, column=0, padx=5, pady=8)
lbl_opponent_name.grid(row=1, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))


top_right_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_game_round = tk.Label(top_right_frame, text="Time left", foreground="blue", font = "Helvetica 14 bold")
lbl_timer = tk.Label(top_right_frame, text="20", font = "Helvetica 24 bold", foreground="blue")
lbl_game_round.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))

top_frame.pack_forget()

middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()
lbl_line = tk.Label(middle_frame, text="Scegli una domanda,poi scegli una risposta", font = "Helvetica 13 bold", foreground="blue").pack()
lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()

round_frame = tk.Frame(middle_frame)
lbl_round = tk.Label(round_frame, text="Question")
lbl_round.pack()
lbl_domanda = tk.Label(round_frame, text="")
lbl_domanda.pack()
lbl_ansbox1 = tk.Label(round_frame, text="1)" , font = "Helvetica 13 bold")
lbl_ansbox1.pack()
lbl_ansbox2 = tk.Label(round_frame, text="2)" , font = "Helvetica 13 bold")
lbl_ansbox2.pack()
lbl_ansbox3 = tk.Label(round_frame, text="3)" , font = "Helvetica 13 bold")
lbl_ansbox3.pack()
lbl_result = tk.Label(round_frame, text=" ", foreground="blue", font = "Helvetica 14 bold")
lbl_result.pack()
round_frame.pack(side=tk.TOP)

final_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text=" ", font = "Helvetica 13 bold", foreground="blue")
lbl_final_result.pack()
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack_forget()

button_frame = tk.Frame(window_main)


btn_1= tk.Button(button_frame, text="1", command=lambda : choice("1"), state=tk.DISABLED, font = "Helvetica 13 bold")
btn_2 = tk.Button(button_frame, text="2", command=lambda : choice("2"), state=tk.DISABLED, font = "Helvetica 13 bold")
btn_3 = tk.Button(button_frame, text="3", command=lambda : choice("3"), state=tk.DISABLED, font = "Helvetica 13 bold")
btn_1.grid(row=0, column=1)
btn_2.grid(row=0, column=2)
btn_3.grid(row=0, column=3)
button_frame.pack(side=tk.BOTTOM)



def enable_disable_buttons(todo):
    if todo == "disable":
        btn_1.config(state=tk.DISABLED)
        btn_2.config(state=tk.DISABLED)
        btn_3.config(state=tk.DISABLED)
    else:
        btn_1.config(state=tk.NORMAL)
        btn_2.config(state=tk.NORMAL)
        btn_3.config(state=tk.NORMAL)


def connect():
    global your_name
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        your_name = ent_name.get()
        lbl_your_name["text"] = "Your name: " + your_name
        connect_to_server(your_name)

#implements the timer for the game. when time is over notify server and other clients and disable other actions
def count_down(my_timer, nothing):
    global game_round,client,over
    enable_disable_buttons("enable")
    while my_timer > 0 :
        my_timer = my_timer - 1
        print("game timer is: " + str(my_timer))
        lbl_timer["text"] = my_timer
        sleep(1)
    if not over:
        final_result = ""
        color = ""

        if your_score > opponent_score:
            final_result = "(You Won!!!)"
            color = "green"
        elif your_score < opponent_score:
            final_result = "(You Lost!!!)"
            color = "red"
        else:
            final_result = "(Draw!!!)"
            color = "black"

        lbl_final_result["text"] = "FINAL RESULT: " + str(your_score) + " - " + str(opponent_score) + " " + final_result
        lbl_final_result.config(foreground=color)
        over=True
        enable_disable_buttons("disable")           
        client.send("time is up".encode())

#if mode is "scelta" picks a random question or trap. if trap is chosen send msg to server to notify other clients. if mode is "domanda" choose the corresponding answer. switches between modes after action.
def choice(arg):
    global your_choice, client, game_round,mode,your_score,Q,over
    your_choice = arg
    if mode=="scelta":
        r=randrange(3)
        c=r+1
        #choose a random number between 1 and 3. if that number corresponds to our choice we chose the trap. if trap is chosen we lose the game and notify server to inform the opponent that they won.
        if(your_choice==str(c)):
            your_choice="trappola"
        if your_choice=="trappola":
            lbl_round["text"]= "You chose the trap!!!!"
            client.send(("Game_Round"+str(game_round)+your_choice).encode())
            enable_disable_buttons("disable")
            final_result = "(You Lost!!!)"
            lbl_final_result["text"] = "FINAL RESULT: " + str(your_score) + " - " + str(opponent_score) + " " + final_result
            over=True
        else:
            game_round+=1
            Q=getquestions()
            lbl_domanda["text"]=Q[0]
            lbl_ansbox1["text"]="1)"+Q[1]
            lbl_ansbox2["text"]="2)"+Q[2]
            lbl_ansbox3["text"]="3)"+Q[3]
            mode="domanda"
    elif mode=="domanda":
        if your_choice==Q[4]:
            your_score+=1
            client.send(("Game_Round"+str(game_round)+"right").encode())
        else :
            your_score-=1
            client.send(("Game_Round"+str(game_round)+"wrong").encode())
        mode="scelta"
        
#contains possible questions and returns a random one when invoked
def getquestions():
    arraydomande=[
        ["23*2?","46","49","56","1"],
        ["Chi uccise Giulio Cesare?","Caio","Nerone","Bruto","3"],
        ["Quanti stati compongono gli USA?","40","48","50","3"],
        ["Chi dipinse Guernica?","Dalì","Picasso","Pizarro","2"],
        ["Quale è la capitale del Giappone?","Tokyo","Kyoto","Osaka","1"],
        ["Lo zio di Gianni ha tre nipoti: Qui,Quo e?","Qua","Gianni","Paperoga","2"],
        ["Montezuma era l'imperatore di quale civiltà?","Atzechi","Maya","Entrambe","1"],
        ["Il Tarrasque è un mostro leggendario di quale universo?","World of Warcraft","Genshin Impact","Dungeons and Dragons","3"],
        ["Di quale band faceva parte Phil Collins?","ABBA","Duran Duran","Genesis","3"],
        ["Chi segnò l'ultimo rigore nella finale dei mondiali di calcio 2006?","Grosso","Del Piero","Materazzi","1"],
        ["Mulder e Scully sono i protagonisti di quale serie tv?","Mulder e Scully","Law and Order","X-files","3"],
        ["In quale data si celebra il giorno dell'indipendenza nelle Filippine?","24 Aprile","12 Giugno","13 Maggio","2"],
        ["3^3=?","9","27","18","2"],
        ["Come si chiama il cane della famiglia Griffin?","Brian","Snoopy","Scooby","1"],
        ["Quale è il simbolo del berillio sulla tavola periodica?","Be","B","Bi","1"],
        ["a+b=5, b+b=4, a^a=?","12","9","27","3"],
        ["Di chi è la canzone 'should i stay or should i go'?","The Clash","The Ramones","The Killers","1"],
        ["Come si chiama al giorno d'oggi la nazione dove nacque Buddha?","Nepal","India","Tibet","1"],
        ["Chi dipinse la creazione di Adamo nella cappella Sistina?","Raffaello","Michelangelo","Leonardo Da Vinci","2"]
        ]
    return arraydomande[randrange(start=0,stop=len(arraydomande)-1)]
    
def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR, your_name
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Invia il nome al server dopo la connessione

        # disable widgets
        btn_connect.config(state=tk.DISABLED)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)
        enable_disable_buttons("disable")

        # avvia un thread per continuare a ricevere messaggi dal server
        # non bloccare il thread principale :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


    
    
def receive_message_from_server(sck, m):
    global your_name, opponent_name, game_round
    global your_choice, opponent_choice, your_score, opponent_score,over

    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        if from_server.startswith("welcome".encode()):
            if from_server == "welcome1":
                lbl_welcome["text"] = "Server says: Welcome " + your_name + "! Waiting for player 2"
            elif from_server == "welcome2":
                lbl_welcome["text"] = "Server says: Welcome " + your_name + "! Game will start soon"
            lbl_line_server.pack()

        elif from_server.startswith("opponent_name$".encode()):
            opponent_name = from_server.replace("opponent_name$".encode(), "".encode())
            lbl_opponent_name["text"] = "Opponent: " + opponent_name.decode()
            top_frame.pack()
            middle_frame.pack()

            # sappiamo che due utenti sono connessi, quindi il gioco Ã¨ pronto per iniziare
            threading._start_new_thread(count_down, (game_timer, ""))
            lbl_welcome.config(state=tk.DISABLED)
            lbl_line_server.config(state=tk.DISABLED)
            
        #server notifies we won cause opponent chose the trap
        elif  from_server.startswith("win".encode()):
              enable_disable_buttons("disable")
              final_result = "(You Won!!!)"
              lbl_final_result["text"] = "FINAL RESULT: " + str(your_score) + " - " + str(opponent_score) + " " + final_result
              over=True
              break
          #server notifies that the time is up so we should compute the final score
        elif  from_server.startswith("time".encode()) and not over:
                # calcola il risultato finale
                final_result = ""
                color = ""

                if your_score > opponent_score:
                    final_result = "(You Won!!!)"
                    color = "green"
                elif your_score < opponent_score:
                    final_result = "(You Lost!!!)"
                    color = "red"
                else:
                    final_result = "(Draw!!!)"
                    color = "black"

                lbl_final_result["text"] = "FINAL RESULT: " + str(your_score) + " - " + str(opponent_score) + " " + final_result
                lbl_final_result.config(foreground=color)
                over=True
                enable_disable_buttons("disable")
    #updates the opponent score when notified by the server
        elif from_server.startswith("$opponent_choice".encode()):
            # ottieni la scelta dell'avversario dal server
            opponent_choice = from_server.replace("$opponent_choice".encode(), "".encode())
       
            #updates opponent score upon receiving communication of their choice from the server
            
            if opponent_choice == "right".encode():
                opponent_score = opponent_score+ 1
                
            elif opponent_choice == "wrong".encode():
                opponent_score = opponent_score- 1
                
                #if the opponent choice was the trap we won!
            elif opponent_choice== "trappola".encode():
                 final_result = "(You Won!!!)"
                 lbl_final_result["text"] = "FINAL RESULT: " + str(your_score) + " - " + str(opponent_score) + " " + final_result
                 enable_disable_buttons("disable")
                 break

            
           
           

           



    sck.close()


window_main.mainloop()
import socket
import pickle
import customtkinter as ctk
from functools import partial
from datetime import datetime




def windowSize_animation():
    widNow = root.winfo_width()
    speed = 15

    
    newWid = widNow + speed
    root.geometry(f"{newWid}x{400}")

   
    if newWid < 600:
        root.after(10, windowSize_animation)


def clear_theWindow():
    for widget in root.winfo_children():
        widget.destroy()



def on_enter(button, event=None):
    button.configure(text_color="gray")

def on_leave(button, event=None):
    button.configure(text_color="white")


def sign_up(username, password, password_confirm):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5000))

    message = pickle.dumps((username, password, password_confirm))
    client_socket.sendall(message)

    response = client_socket.recv(1024).decode('utf-8')

    if response == "T":
        print("Username taken")
    else:
        logIn_Ui()
    client_socket.close()

def log_in(username, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5000))

    message = pickle.dumps((username, password))
    client_socket.sendall(message)

    
    response = client_socket.recv(1024).decode('utf-8')

    
    client_socket.close()
    if response == "F":
        print("Error!")
        return False
    elif response == "T":
        app_ui(username)
        return True
        
    else:
        print("Error!")
        return False
    
    
def update_scrollable_frame(search_term, scrollable_frame, entry, name_label, now_using, messages_frame):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5000))

   
    
    message = pickle.dumps("upload")
    client_socket.send(message)
   


    
    pickle_response = client_socket.recv(1024)
    response = pickle.loads(pickle_response)
    
    client_socket.close()
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    
    
    for user in response:
        if search_term.lower() in user.lower() and user != now_using:
            button = ctk.CTkButton(scrollable_frame, text=user, width=400, corner_radius=0, fg_color="grey19", hover_color="grey20")
            button.pack(pady=3, padx=(15,0))
            button.bind("<Button-1>", lambda event, name=user: (on_label_click(name, scrollable_frame, entry, name_label, messages_frame), display_messages(messages_frame, now_using, name)))
            
    

def on_label_click(name, scrollable_frame, entry, name_label, messages_frame):
    
    global current_receiver
    current_receiver = name
    
    for widget in messages_frame.winfo_children():
        widget.destroy()
    

    name_label.configure(text=name)

    
    
    

def save_to_db(entry, user, receiver):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5000))
    
    message = entry.get()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message.strip():
        entry.delete(0, ctk.END)
        message = pickle.dumps((user, message, receiver, time))
        client_socket.sendall(message)
    client_socket.close()


def display_messages(messages_frame, user, receiver, last_update_time=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5000))

    request = ("fetch_messages", user, receiver, last_update_time, 1, 2, 3)
    request = pickle.dumps(request)
    client_socket.sendall(request)

    try:
        data = []
        while True:
            # Receive data from the server
            chunk = client_socket.recv(1024)
            unpickled_chunk = pickle.loads(chunk)

          
            if unpickled_chunk == "end":
                break

            data.append(unpickled_chunk)

            
            ack = pickle.dumps("c")
            client_socket.sendall(ack)

      
        messages = [item for sublist in data for item in sublist]

        if len(messages) > 0:
            last_update_time = messages[-1][3]

            for message in messages:
                sender = message[1]
                text = message[2]
                if sender == user:
                    label = ctk.CTkLabel(messages_frame, text=text, font=font2, wraplength=150, justify="left")
                    label.pack(padx=15, pady=5, anchor="w")
                else:
                    label = ctk.CTkLabel(messages_frame, text=text, font=font2, wraplength=150, justify="right")
                    label.pack(padx=15, pady=5, anchor="e")

            messages_frame.after(10, messages_frame._parent_canvas.yview_moveto, 1.0)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()

    if current_receiver == receiver:
        messages_frame.after(1000, lambda: display_messages(messages_frame, user, receiver, last_update_time))


    


def logIn_Ui():

    clear_theWindow()

    label = ctk.CTkLabel(root, text="LOG IN", font=font1)
    label.pack(pady=30, padx=(0,135))

    name = ctk.CTkEntry(root, width=200, placeholder_text="username",font=font3)
    name.pack(pady=15)

    password = ctk.CTkEntry(root, width=200, placeholder_text="password", font=font3, show="*")
    password.pack(pady=20)

    button = ctk.CTkButton(root, text="Continue", font=font2, width=200)
    button.pack(pady=(40,0))

    button.bind("<Button-1>", lambda event: log_in(name.get(), password.get()))

    signUp = ctk.CTkButton(root, text="Sign up", fg_color="transparent", hover=False, font=font2, command=signUp_ui)
    signUp.pack(padx=(150,0), pady=(20,0))

    
    signUp.bind("<Enter>", partial(on_enter, signUp))
    signUp.bind("<Leave>", partial(on_leave, signUp))

def signUp_ui():
    
    clear_theWindow()

    label = ctk.CTkLabel(root, text="SIGN UP", font=font1)
    label.pack(pady=30, padx=(0,135))

    name = ctk.CTkEntry(root, width=200, placeholder_text="username",font=font3)
    name.pack(pady=15)

    password = ctk.CTkEntry(root, width=200, placeholder_text="password", font=font3, show="*")
    password.pack(pady=20)

    confirm_password = ctk.CTkEntry(root, width=200, placeholder_text="confirm password", font=font3, show="*")
    confirm_password.pack(pady=20)

    button = ctk.CTkButton(root, text="Sign up", font=font2, width=200)
    button.pack(pady=(20,0))

    button.bind("<Button-1>", lambda event: sign_up(name.get(), password.get(), confirm_password.get()))

    logIn = ctk.CTkButton(root, text="Log in", fg_color="transparent", hover=False, font=font2, command=logIn_Ui)
    logIn.pack(padx=(150,0), pady=(10,0))

    
    logIn.bind("<Enter>", partial(on_enter, logIn))
    logIn.bind("<Leave>", partial(on_leave, logIn))


def app_ui(user):
    
    clear_theWindow()
    windowSize_animation()
    
    
    entry = ctk.CTkEntry(root, placeholder_text="Find by username", width=218, corner_radius=1, border_color="gray15", fg_color="gray15", border_width=3, height=40)
    entry.grid(row=0, column=0)
    entry.bind("<KeyRelease>", lambda event: update_scrollable_frame(entry.get(), scrollable_frame, entry, name_label, user, messages))

    name_frame = ctk.CTkFrame(root, width=382, height=40, corner_radius=1, fg_color="grey17")
    name_frame.grid(row=0, column=1, columnspan=2)
    name_frame.pack_propagate(0)


    name_label = ctk.CTkLabel(master=name_frame, text="", font=font2)
    name_label.pack(padx=(20,300), pady=10)


    scrollable_frame = ctk.CTkScrollableFrame(root, width=200, height=400, corner_radius=1, scrollbar_fg_color="gray17", scrollbar_button_color="gray17", scrollbar_button_hover_color="gray17")
    scrollable_frame.grid(row=1, column=0, sticky="e", rowspan=2)

    

    messages = ctk.CTkScrollableFrame(root, width=368, height=300, corner_radius=1, fg_color="gray14")
    messages.grid(row=1, column=1, columnspan=2, sticky="n")

    

    text_entry = ctk.CTkEntry(root, height=35, width=370, corner_radius=5, border_color="grey17", fg_color="grey17", placeholder_text="Send message")
    text_entry.grid(row=2, column=1, columnspan=2, sticky="n", pady=(0, 30))

    

    text_entry.bind("<Return>", lambda event: save_to_db(text_entry, user, name_label.cget("text")))

    update_scrollable_frame(entry.get(), scrollable_frame, entry, name_label, user, messages)
 

root = ctk.CTk()


font1 = ctk.CTkFont(family="bahnschrift", size=21)
font2 = ctk.CTkFont(family="bahnschrift", size=14)
font3 = ctk.CTkFont(family="bahnschrift", size=11)

root.geometry("330x400")

logIn_Ui()

root.resizable(False, False)

root.mainloop()

import socket
import threading
import sqlite3
import pickle
import time


conn = sqlite3.connect('chats.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        time TEXT,
        receiver TEXT
    )
''')
conn.commit()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')

conn.commit()



def handle_client(client_socket):
    global new_message_arrived
    con = sqlite3.connect('chats.db')
    cursor = con.cursor()
    try:
    
        message = client_socket.recv(1024)
        
        message = pickle.loads(message)
        

        
        
        if len(message) == 4:
            cursor.execute("INSERT INTO messages (username, message, time, receiver) VALUES (?, ?, ?, ?)", (message[0], message[1], message[3], message[2]))
            con.commit()

        elif len(message) == 2:
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (message[0], message[1]))
            result = cursor.fetchone()
            if result:
                response_message = "T"
                client_socket.send(response_message.encode('utf-8'))
            else:
                response_message = "F"
                client_socket.send(response_message.encode('utf-8'))

        elif len(message) == 3:
            if message[1] == message[2]:
                cursor.execute("SELECT * FROM users WHERE username = ?", (message[0],))
                result = cursor.fetchone()
                if result:
                    response_message = "T"
                    client_socket.send(response_message.encode('utf-8'))
                else:
                    response_message = "F"
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (message[0], message[1]))
                    con.commit()

                    client_socket.send(response_message.encode('utf-8'))
        


        elif len(message) == 6:
            cursor.execute("SELECT username FROM users")

            usernames = [user[0] for user in cursor.fetchall()]
            

            respond = pickle.dumps(usernames)
            client_socket.sendall(respond)

        elif len(message) == 7:
            user, receiver = message[1], message[2]
            last_update_time = message[3] if len(message) > 3 else None

            query = "SELECT username, receiver, message, time FROM messages WHERE ((username=? AND receiver=?) OR (username=? AND receiver=?))"
            params = (user, receiver, receiver, user)

            if last_update_time:
                query += " AND time > ?"
                params += (last_update_time,)

            cursor.execute(query, params)
            messages = cursor.fetchall()

            chunk_size = 10
            chunks = [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]

            try:
                if len(messages) > 0:
                    for chunk in chunks:
                        response = pickle.dumps(chunk)
                        client_socket.sendall(response)

                        conti = client_socket.recv(1024)
                        acknowledgment = pickle.loads(conti)
                        
                        # Check acknowledgment here if needed
                # Send end signal
                end_signal = pickle.dumps("end")
                client_socket.sendall(end_signal)
            except Exception as e:
                print(f"Error during data transmission: {e}")
                # Handle exceptions (like closing socket or logging error)



            
            



            
            
    except:
        print("error!")
       
        
        
   
    


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(5)
    print("[*] Kuunnellaan yhteyksiä osoitteessa localhost:")
                                                                                                                          
    while True:
        client, addr = server.accept()
        print(f"[*] Yhteys osoitteesta: {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
        

if __name__ == "__main__":
    start_server()

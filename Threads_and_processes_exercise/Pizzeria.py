import time

from multiprocessing.connection import Listener, Client

ADDRESS = ('localhost', 6000)

# A simple password to make sure we're connecting to the right server

AUTH_KEY = b'my_secret_password'


def run_server(log_queue):
    log_queue.put("SERVER: Pizzeria is open for business!")

    with Listener(ADDRESS, authkey=AUTH_KEY) as listener:

        log_queue.put(f"SERVER: Waiting for a customer to call at {ADDRESS}...")

        with listener.accept() as conn:

            log_queue.put(f"SERVER: A customer connected! {listener.last_accepted}")

            while True:

                try:

                    msg = conn.recv()

                    log_queue.put(f"SERVER: Received order: '{msg}'")

                    if msg == 'order:pepperoni':

                        conn.send("Pizza:pepperoni is on its way!")

                    elif msg == 'order:margherita':

                        conn.send("Pizza:margherita is on its way!")

                    elif msg == 'hangup':

                        log_queue.put("SERVER: Customer hung up. Closing connection.")

                        break

                except EOFError:

                    log_queue.put("SERVER: Connection closed by client unexpectedly.")

                    break

    # Signal that this process is done

    log_queue.put("DONE")


def run_client(log_queue):
    log_queue.put("CLIENT: I'm hungry for pizza!")

    time.sleep(1)

    try:

        with Client(ADDRESS, authkey=AUTH_KEY) as conn:

            log_queue.put("CLIENT: Placing order: 'order:pepperoni'")

            conn.send('order:pepperoni')

            log_queue.put(f"CLIENT: Pizzeria response: '{conn.recv()}'")

            time.sleep(2)

            log_queue.put("CLIENT: Placing order: 'order:margherita'")

            conn.send('order:margherita')

            log_queue.put(f"CLIENT: Pizzeria response: '{conn.recv()}'")

            conn.send('hangup')

            log_queue.put("CLIENT: All done, hanging up.")

    except ConnectionRefusedError:

        log_queue.put("CLIENT: Could not connect. Is the pizzeria open?")

    # Signal that this process is done

    log_queue.put("DONE")
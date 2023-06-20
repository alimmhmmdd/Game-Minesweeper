from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import itertools
from datetime import time, date, datetime
import time
import tkinter as tk

# Membuat jendela utama
root = tk.Tk()
root.title("Minesweeper")
root.geometry("350x350")

# Membuat label judul
judul = tk.Label(root, text="MINESWEEPER GAME \n Selamat Bermain", font=("Arial", 15))
judul.pack()

# Membuat tombol mulai
mulai = tk.Button(root, text="Mulai", font=("Arial", 13), command=lambda: mulai_game())
mulai.pack()

# Membuat fungsi untuk mulai game
def mulai_game():
    # Menutup jendela utama
    root.destroy()
    # Membuat jendela baru untuk game
    game = tk.Tk()
    game.title("Minesweeper")
    game.geometry("350x350")
    # Menampilkan pesan di jendela game
    pesan = "tk.Label"(game, text="Game dimulai!", font=("Arial", 32))
    pesan.pack()
    # Menjalankan jendela game
    game.mainloop()
# Menjalankan jendela utama
root.mainloop()


#Program Game Minesweeper
SIZE_X = 7
SIZE_Y = 8

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

window = None

class Minesweeper:
    def __init__(self, tk):
        self.frame = Frame(tk)
        self.frame.pack()
        self.mines = 10

        # import images
        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file="images/tile_"+str(i)+".gif"))

        # set up frame
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # set up labels/UI
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0"),
            "restart": Label(self.frame)
        }
        self.labels["time"].grid(row=0, column=0, columnspan=SIZE_Y)  # top full width
        self.labels["mines"].grid(row=SIZE_X+1, column=0, columnspan=int(SIZE_Y/2))  # bottom left
        self.labels["flags"].grid(row=SIZE_X+1, column=int(SIZE_Y/2)-1, columnspan=int(SIZE_Y/2))  # bottom right
        self.labels["restart"].grid(row=SIZE_X+2, column=0, columnspan=SIZE_Y)  # button row
        self.frame.columnconfigure(1, weight=1)
        self.restart()  # start game
        self.updateTimer()  # init timer

    def setup(self):
    # create flag and clicked tile variables
        self.button_dfs = Button(self.frame, text="DFS", command=self.show_dfs)
        self.button_dfs.grid(row=SIZE_X+3, column=0, columnspan=SIZE_Y)
        self.button_bfs = Button(self.frame, text="BFS", command=self.show_bfs)
        self.button_bfs.grid(row=SIZE_X+3, column=0, columnspan=SIZE_Y-5)
        self.button_restart = Button(self.frame, text="Restart", command=self.show_restart_message)
        self.button_restart.grid(row=SIZE_X+3, column=6, columnspan=SIZE_Y)

        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None

    # create buttons
        self.tiles = dict({})
    # Generate random unique indices for mine positions
        mine_indices = random.sample(range(SIZE_X * SIZE_Y), self.mines)
        mine_index = 0

        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False

            # tile image changeable for debug reasons:
                gfx = self.images["plain"]

            # Set mine position based on the generated indices
                if mine_index in mine_indices:
                    isMine = True
                mine_index += 1

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image=gfx),
                    "mines": 0  # calculated after grid is built
            }

                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid(row=x + 1, column=y)  # offset by 1 row for timer

                self.tiles[x][y] = tile

    # loop again to find nearby mines and display number on tile
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc
                
    def show_restart_message(self):
        res = tkMessageBox.askyesno("Restart", "Do you want to restart the game?")
        if res:
            self.restart()
        else:
            self.tk.quit()

    def restart(self):
        self.setup()
        self.refreshLabels() 

    def refreshLabels(self):
        self.labels["flags"].config(text="Flags: "+str(self.flagCount))
        self.labels["mines"].config(text="Mines: "+str(self.mines))

    def gameOver(self, won):
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image=self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image=self.images["mine"])

        self.tk.update()

        msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = tkMessageBox.askyesno("Game Over", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()
        
    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0] # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts # zero-pad
        self.labels["time"].config(text=ts)
        self.frame.after(100, self.updateTimer)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1},  #top right
            {"x": x-1,  "y": y},    #top middle
            {"x": x-1,  "y": y+1},  #top left
            {"x": x,    "y": y-1},  #left
            {"x": x,    "y": y+1},  #right
            {"x": x+1,  "y": y-1},  #bottom right
            {"x": x+1,  "y": y},    #bottom middle
            {"x": x+1,  "y": y+1},  #bottom left
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["isMine"] == True:
            # end game
            self.gameOver(False)
            return

        # change image
        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image=self.images["numbers"][tile["mines"]-1])
        # if not already set as clicked, change state and count
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (SIZE_X * SIZE_Y) - self.mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # if not clicked
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image=self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()
        # if flagged, unflag
        elif tile["state"] == 2:
            tile["button"].config(image=self.images["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image=self.images["numbers"][tile["mines"]-1])

        tile["state"] = STATE_CLICKED
        self.clickedCount += 1


    def show_dfs(self):
        self.startTime = None
        stack = [(0, 0)]  # Sesuaikan ini berdasarkan koordinat sel awal Anda
        visited = set([(0, 0)])  # Sesuaikan ini berdasarkan koordinat sel awal Anda
        fwdPath = {(0, 0): (0, 0)}  # Inisialisasi fwdPath dengan sel awal

        start_time = time.time()
        while stack:
            cell = stack.pop()
            x, y = cell
            initial_state = (self.tiles[x][y]["isMine"], self.tiles[x][y]["mines"])
            
            if initial_state[0]:
                continue

            self.tiles[x][y]["button"].config(image=self.images["clicked"])
            
            if initial_state[1] > 0:
                number_image = self.images["numbers"][initial_state[1] - 1]
                self.tiles[x][y]["button"].config(image=number_image)
            
            self.update_neighbors(x, y)
            self.tk.update()
            self.tk.after(1000)

            for neighbor in self.get_valid_neighbors(x, y):
                if neighbor not in visited and neighbor not in stack:
                    stack.append(neighbor)
                    visited.add(neighbor)
                    fwdPath[neighbor] = cell

        elapsed_time = time.time() - start_time
        self.startTime = None  # Reset timer
        print("Elapsed time:", elapsed_time, "seconds")

        # Display message box after DFS path is finished
        msg = f"Elapsed time:{elapsed_time:.2f} seconds. Play again?"
        res = tkMessageBox.askyesno("Finished", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()
    
    def show_bfs(self):
        self.startTime = None
        queue = deque([(0, 0)])  # Adjust this based on your starting cell coordinates
        visited = set([(0, 0)])  # Adjust this based on your starting cell coordinates
        fwdPath = {(0, 0): (0, 0)}  # Initialize fwdPath with the starting cell

        start_time = time.time()

        while queue:
            cell = queue.popleft()
            x, y = cell
            initial_state = (self.tiles[x][y]["isMine"], self.tiles[x][y]["mines"])
            if initial_state[0]:
                continue
            self.tiles[x][y]["button"].config(image=self.images["clicked"])
            if initial_state[1] > 0:
                number_image = self.images["numbers"][initial_state[1] - 1]
                self.tiles[x][y]["button"].config(image=number_image)
            self.update_neighbors(x, y)
            self.tk.update()
            self.tk.after(1000)
            
            for neighbor in self.get_valid_neighbors(x, y):
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    fwdPath[neighbor] = cell

        elapsed_time = time.time() - start_time
        self.startTime = None  # Reset timer
        print("Elapsed time:", elapsed_time, "seconds")

    # Display message box after BFS path is finished
        msg = f"Elapsed time: {elapsed_time:.2f} seconds. Play again?"
        res = tkMessageBox.askyesno("Finished", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    def get_valid_neighbors(self, x, y):
        coords = list(itertools.product(range(x - 1, x + 2), range(y - 1, y + 2)))
        valid_coords = [(i, j) for i, j in coords if (0 <= i < SIZE_X) and (0 <= j < SIZE_Y) and (i, j) != (x, y)]
        return valid_coords
    
    def update_neighbors(self, x, y):
        neighbors = self.getNeighbors(x, y)
        for neighbor in neighbors:
            neighbor_x = neighbor["coords"]["x"]
            neighbor_y = neighbor["coords"]["y"]
            initial_state = (self.tiles[neighbor_x][neighbor_y]["isMine"], self.tiles[neighbor_x][neighbor_y]["mines"])
            if initial_state[0] or self.tiles[neighbor_x][neighbor_y]["button"].cget("image") == self.images["flag"]:
                continue
            self.tiles[neighbor_x][neighbor_y]["button"].config(image=self.images["clicked"])
            if initial_state[1] > 0:
                number_image = self.images["numbers"][initial_state[1] - 1]
                self.tiles[neighbor_x][neighbor_y]["button"].config(image=number_image)
            self.tk.update()
            self.tk.after(100)

def onClosing():
    res = tkMessageBox.askyesno("Exit", "Are you sure to quit the game?")
    if res:
        window.destroy()
    
def main():
    global window
    window = Tk()
    # set program title
    window.protocol("WM_DELETE_WINDOW", onClosing)
    window.title("Minesweeper")
    window.geometry("250x320")
    # create game instance
    minesweeper = Minesweeper(window)
    minesweeper.setup()
    # run event loop
    window.mainloop()

if __name__ == "__main__":
    main()
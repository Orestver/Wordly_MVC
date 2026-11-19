from tkinterdnd2 import TkinterDnD
from main_controller import MainController

def main():
    root = TkinterDnD.Tk()
    root.title("Wordly Project - Learn Languages")
    root.geometry("1000x700")
    root.minsize(600, 400)
    root.resizable(False, True)
    controller = MainController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
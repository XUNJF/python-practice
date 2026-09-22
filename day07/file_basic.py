with open("note.txt", "w", encoding="utf-8") as f:
    f.write("hello\n")
    f.write("I'm happy\n")
    f.write("I'm Jack\n")





with open("note.txt", "a", encoding="utf-8") as f:
    f.write("hello\n")
    f.write("I'm happy\n")
    f.write("I'm Jack\n")
    
with open("note.txt", "r", encoding="utf-8") as f:
    contact = f.read()
print(contact.strip())
import re
path = r"c:\Users\yifan\Documents\GitHub\VideoMMEv2\index.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()
s = re.sub(r'\. [\s\u201c"]?thinking[\u201d"]? capability remains more oriented toward text reasoning and has difficulty directly improving visual understanding and may even be harmful\.', '.', s)
with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("Done")

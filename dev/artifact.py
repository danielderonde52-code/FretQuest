"""Maakt uit index.html de bron voor de Claude-artifact (voorvertoning in de chat):  python3 dev/artifact.py > /tmp/fretquest-artifact.html
De artifact is index.html zonder de omhullende pagina en zonder service worker, met een <title> vooraan."""
import os,sys
pg=open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'index.html'),encoding='utf-8').read()
a=pg.index('<body>\n')+7;b=pg.index("\n<script>if('serviceWorker'")
sys.stdout.write('<title>FretQuest</title>'+pg[a:b])
